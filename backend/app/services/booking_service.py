

from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.models import Flight, SeatInventory, Booking, Passenger, PaymentTransaction
from app.schemas import BookingCreate, PassengerCreate
from app.utils.helpers import generate_pnr
from app.services.pricing_engine import get_dynamic_price

class BookingService:
    
    @staticmethod
    def create_booking(
        booking_data: BookingCreate,
        user_id: int,
        db: Session
    ) -> Booking:

        try:
            # Start transaction
            flight = db.query(Flight).filter(
                and_(
                    Flight.FlightID == booking_data.FlightID,
                    Flight.Flight_status == 'scheduled'
                )
            ).with_for_update().first()  # Lock row for update
            
            if not flight:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Flight not found or not available for booking"
                )
            
            # Check if flight is in the future
            if flight.Departure_Time <= datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot book flights that have already departed"
                )
            
            # Get seat inventory with lock
            seat_inv = db.query(SeatInventory).filter(
                and_(
                    SeatInventory.FlightID == booking_data.FlightID,
                    SeatInventory.Class == booking_data.Seat_class
                )
            ).with_for_update().first()
            
            if not seat_inv:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Seat class {booking_data.Seat_class} not available for this flight"
                )
            
            # Check seat availability
            num_passengers = len(booking_data.passengers)
            if seat_inv.Available_seats < num_passengers:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Only {seat_inv.Available_seats} seats available, requested {num_passengers}"
                )
            
            # Calculate dynamic price
            from app.models import Airline, Airport
            airline = db.query(Airline).filter(Airline.AirlineID == flight.AirlineID).first()
            origin = db.query(Airport).filter(Airport.AirportID == flight.Departure_AirportID).first()
            dest = db.query(Airport).filter(Airport.AirportID == flight.Arrival_AirportID).first()
            
            price_data = get_dynamic_price(
                base_fare=float(flight.Price),
                seats_available=seat_inv.Available_seats,
                total_seats=seat_inv.Total_Seats,
                departure_time=flight.Departure_Time,
                origin_code=origin.Airport_Code,
                destination_code=dest.Airport_Code,
                airline_code=airline.Airline_Code,
                seat_class=booking_data.Seat_class
            )
            
            price_per_seat = price_data['final_price']
            total_price = price_per_seat * num_passengers
            
            # Generate unique PNR
            pnr = generate_pnr()
            while db.query(Booking).filter(Booking.pnr == pnr).first():
                pnr = generate_pnr()  # Regenerate if collision
            
            # Create booking
            new_booking = Booking(
                pnr=pnr,
                UserID=user_id,
                FlightID=booking_data.FlightID,
                Seat_class=booking_data.Seat_class,
                Num_passengers=num_passengers,
                Total_price=total_price,
                Booking_status='pending',
                Payment_status='unpaid',
                Expiry_time=datetime.now() + timedelta(minutes=15)  # 15 min to complete payment
            )
            
            db.add(new_booking)
            db.flush()  # Get booking ID without committing
            
            # Create passenger records
            for passenger_data in booking_data.passengers:
                passenger = Passenger(
                    BookingID=new_booking.BookingID,
                    First_name=passenger_data.First_name,
                    Last_name=passenger_data.Last_name,
                    Date_of_birth=passenger_data.Date_of_birth,
                    Gender=passenger_data.Gender,
                    Passport_number=passenger_data.Passport_number,
                    Nationality=passenger_data.Nationality,
                    Email=passenger_data.Email,
                    Phone=passenger_data.Phone
                )
                db.add(passenger)
            
            # Lock seats (reduce availability)
            seat_inv.Available_seats -= num_passengers
            
            # Commit transaction
            db.commit()
            db.refresh(new_booking)
            
            return new_booking
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Booking failed: {str(e)}"
            )
    
    @staticmethod
    def confirm_booking(pnr: str, payment_method: str, db: Session) -> Booking:
        booking = db.query(Booking).filter(Booking.pnr == pnr).first()
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        if booking.Booking_status == 'confirmed':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking already confirmed"
            )
        
        # Check if booking expired
        if booking.Expiry_time and datetime.now() > booking.Expiry_time:
            # Release seats and cancel booking
            BookingService.cancel_booking(pnr, db)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking expired. Please create a new booking."
            )
        
        # Update booking status
        booking.Booking_status = 'confirmed'
        booking.Payment_status = 'paid'
        booking.Payment_date = datetime.now()
        booking.Expiry_time = None
        
        # Create payment transaction record
        transaction = PaymentTransaction(
            BookingID=booking.BookingID,
            Payment_method=payment_method,
            Transaction_amount=booking.Total_price,
            Transaction_status='success',
            Payment_gateway_response="Payment successful"
        )
        db.add(transaction)
        
        db.commit()
        db.refresh(booking)
        
        return booking
    
    @staticmethod
    def cancel_booking(pnr: str, db: Session) -> dict:

        booking = db.query(Booking).filter(Booking.pnr == pnr).first()
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        if booking.Booking_status == 'cancelled':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking already cancelled"
            )
        
        # Release seats
        seat_inv = db.query(SeatInventory).filter(
            and_(
                SeatInventory.FlightID == booking.FlightID,
                SeatInventory.Class == booking.Seat_class
            )
        ).first()
        
        if seat_inv:
            seat_inv.Available_seats += booking.Num_passengers
        
        # Update booking status
        booking.Booking_status = 'cancelled'
        
        # Handle refund if payment was made
        if booking.Payment_status == 'paid':
            booking.Payment_status = 'refunded'
            
            # Create refund transaction
            transaction = PaymentTransaction(
                BookingID=booking.BookingID,
                Payment_method='refund',
                Transaction_amount=booking.Total_price,
                Transaction_status='refunded',
                Payment_gateway_response="Refund processed"
            )
            db.add(transaction)
        
        db.commit()
        
        return {
            "message": "Booking cancelled successfully",
            "pnr": pnr,
            "refund_amount": float(booking.Total_price) if booking.Payment_status == 'refunded' else 0.0
        }

booking_service = BookingService()
