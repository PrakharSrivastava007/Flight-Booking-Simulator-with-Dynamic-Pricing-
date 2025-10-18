from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database_connection import get_db
from app.models import User, Booking, Passenger, Flight, Airline, Airport
from app.schemas import BookingCreate, BookingResponse, PassengerResponse
from app.utils.security import get_current_user
from app.services.booking_service import booking_service

router = APIRouter(prefix="/api/v1/bookings", tags=["Bookings"])

@router.post("/create", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    new_booking = booking_service.create_booking(
        booking_data=booking_data,
        user_id=current_user.UserID,
        db=db
    )
    
    # Fetch complete booking details
    return get_booking_by_pnr(new_booking.pnr, current_user, db)

@router.post("/{pnr}/confirm")
def confirm_booking(
    pnr: str,
    payment_method: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Verify booking belongs to user
    booking = db.query(Booking).filter(Booking.pnr == pnr.upper()).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.UserID != current_user.UserID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to confirm this booking"
        )
    
    confirmed_booking = booking_service.confirm_booking(pnr.upper(), payment_method, db)
    
    return {
        "message": "Booking confirmed successfully",
        "pnr": confirmed_booking.pnr,
        "status": confirmed_booking.Booking_status,
        "payment_status": confirmed_booking.Payment_status,
        "total_amount": float(confirmed_booking.Total_price)
    }

@router.get("/my-bookings", response_model=List[BookingResponse])
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    bookings = db.query(Booking).filter(Booking.UserID == current_user.UserID).all()
    
    result = []
    for booking in bookings:
        flight = db.query(Flight).filter(Flight.FlightID == booking.FlightID).first()
        airline = db.query(Airline).filter(Airline.AirlineID == flight.AirlineID).first()
        origin = db.query(Airport).filter(Airport.AirportID == flight.Departure_AirportID).first()
        dest = db.query(Airport).filter(Airport.AirportID == flight.Arrival_AirportID).first()
        passengers = db.query(Passenger).filter(Passenger.BookingID == booking.BookingID).all()
        
        result.append(BookingResponse(
            BookingID=booking.BookingID,
            pnr=booking.pnr,
            FlightID=booking.FlightID,
            flight_details={
                "flight_number": flight.Flight_Number,
                "airline": airline.Airline_Name,
                "origin": f"{origin.City} ({origin.Airport_Code})",
                "destination": f"{dest.City} ({dest.Airport_Code})",
                "departure": flight.Departure_Time.isoformat(),
                "arrival": flight.Arrival_Time.isoformat()
            },
            Seat_class=booking.Seat_class,
            Num_passengers=booking.Num_passengers,
            Total_price=float(booking.Total_price),
            Booking_status=booking.Booking_status,
            Payment_status=booking.Payment_status,
            Booking_Date=booking.Booking_Date,
            Expiry_time=booking.Expiry_time,
            passengers=[PassengerResponse(
                PassengerID=p.PassengerID,
                First_name=p.First_name,
                Last_name=p.Last_name,
                Date_of_birth=p.Date_of_birth,
                Gender=p.Gender,
                Passport_number=p.Passport_number,
                Nationality=p.Nationality,
                Email=p.Email,
                Phone=p.Phone
            ) for p in passengers]
        ))
    
    return result

@router.get("/{pnr}", response_model=BookingResponse)
def get_booking_by_pnr(
    pnr: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    booking = db.query(Booking).filter(Booking.pnr == pnr.upper()).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with PNR {pnr} not found"
        )
    
    # Verify booking belongs to user
    if booking.UserID != current_user.UserID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this booking"
        )
    
    # Get flight details
    flight = db.query(Flight).filter(Flight.FlightID == booking.FlightID).first()
    airline = db.query(Airline).filter(Airline.AirlineID == flight.AirlineID).first()
    origin = db.query(Airport).filter(Airport.AirportID == flight.Departure_AirportID).first()
    dest = db.query(Airport).filter(Airport.AirportID == flight.Arrival_AirportID).first()
    passengers = db.query(Passenger).filter(Passenger.BookingID == booking.BookingID).all()
    
    return BookingResponse(
        BookingID=booking.BookingID,
        pnr=booking.pnr,
        FlightID=booking.FlightID,
        flight_details={
            "flight_number": flight.Flight_Number,
            "airline": airline.Airline_Name,
            "airline_code": airline.Airline_Code,
            "origin": f"{origin.City} ({origin.Airport_Code})",
            "destination": f"{dest.City} ({dest.Airport_Code})",
            "departure": flight.Departure_Time.isoformat(),
            "arrival": flight.Arrival_Time.isoformat(),
            "duration": flight.Duration,
            "status": flight.Flight_status
        },
        Seat_class=booking.Seat_class,
        Num_passengers=booking.Num_passengers,
        Total_price=float(booking.Total_price),
        Booking_status=booking.Booking_status,
        Payment_status=booking.Payment_status,
        Booking_Date=booking.Booking_Date,
        Expiry_time=booking.Expiry_time,
        passengers=[PassengerResponse(
            PassengerID=p.PassengerID,
            First_name=p.First_name,
            Last_name=p.Last_name,
            Date_of_birth=p.Date_of_birth,
            Gender=p.Gender,
            Passport_number=p.Passport_number,
            Nationality=p.Nationality,
            Email=p.Email,
            Phone=p.Phone
        ) for p in passengers]
    )

@router.delete("/{pnr}/cancel")
def cancel_booking(
    pnr: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Verify booking belongs to user
    booking = db.query(Booking).filter(Booking.pnr == pnr.upper()).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.UserID != current_user.UserID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to cancel this booking"
        )
    
    result = booking_service.cancel_booking(pnr.upper(), db)
    return result

@router.get("/health")
def booking_service_health(db: Session = Depends(get_db)):
    total_bookings = db.query(Booking).count()
    confirmed_bookings = db.query(Booking).filter(Booking.Booking_status == 'confirmed').count()
    pending_bookings = db.query(Booking).filter(Booking.Booking_status == 'pending').count()
    
    return {
        "status": "healthy",
        "service": "bookings",
        "total_bookings": total_bookings,
        "confirmed": confirmed_bookings,
        "pending": pending_bookings
    }
