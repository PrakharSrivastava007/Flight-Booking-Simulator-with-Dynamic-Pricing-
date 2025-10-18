# Admin endpoints for flight management

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel
from app.database_connection import get_db
from app.models import Flight, Airline, Airport, SeatInventory

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

# Request schemas
class FlightCreate(BaseModel):
    AirlineID: int
    Flight_Number: str
    Departure_AirportID: int
    Arrival_AirportID: int
    Departure_Time: datetime
    Arrival_Time: datetime
    Duration: int
    Price: float
    economy_seats: int
    business_seats: int = 0
    first_seats: int = 0

class FlightUpdate(BaseModel):
    Price: float = None
    Flight_status: str = None

@router.post("/flights", status_code=status.HTTP_201_CREATED)
def add_flight(
    flight_data: FlightCreate,
    db: Session = Depends(get_db)
):

    # Validate airline exists
    airline = db.query(Airline).filter(Airline.AirlineID == flight_data.AirlineID).first()
    if not airline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Airline not found"
        )
    
    # Validate airports exist
    origin = db.query(Airport).filter(Airport.AirportID == flight_data.Departure_AirportID).first()
    dest = db.query(Airport).filter(Airport.AirportID == flight_data.Arrival_AirportID).first()
    
    if not origin or not dest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid airport ID"
        )
    
    # Check if flight number already exists
    existing = db.query(Flight).filter(Flight.Flight_Number == flight_data.Flight_Number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Flight {flight_data.Flight_Number} already exists"
        )
    
    # Create flight
    total_seats = flight_data.economy_seats + flight_data.business_seats + flight_data.first_seats
    
    new_flight = Flight(
        AirlineID=flight_data.AirlineID,
        Flight_Number=flight_data.Flight_Number,
        Departure_AirportID=flight_data.Departure_AirportID,
        Arrival_AirportID=flight_data.Arrival_AirportID,
        Departure_Time=flight_data.Departure_Time,
        Arrival_Time=flight_data.Arrival_Time,
        Duration=flight_data.Duration,
        Price=flight_data.Price,
        Seats_Available=total_seats,
        Flight_status='scheduled'
    )
    
    db.add(new_flight)
    db.flush()  # Get flight ID
    
    # Create seat inventory
    if flight_data.economy_seats > 0:
        economy_inv = SeatInventory(
            FlightID=new_flight.FlightID,
            Class='economy',
            Total_Seats=flight_data.economy_seats,
            Available_seats=flight_data.economy_seats,
            Price=1.0
        )
        db.add(economy_inv)
    
    if flight_data.business_seats > 0:
        business_inv = SeatInventory(
            FlightID=new_flight.FlightID,
            Class='business',
            Total_Seats=flight_data.business_seats,
            Available_seats=flight_data.business_seats,
            Price=2.5
        )
        db.add(business_inv)
    
    if flight_data.first_seats > 0:
        first_inv = SeatInventory(
            FlightID=new_flight.FlightID,
            Class='first',
            Total_Seats=flight_data.first_seats,
            Available_seats=flight_data.first_seats,
            Price=4.5
        )
        db.add(first_inv)
    
    db.commit()
    db.refresh(new_flight)
    
    return {
        "message": "Flight added successfully",
        "flight_id": new_flight.FlightID,
        "flight_number": new_flight.Flight_Number,
        "route": f"{origin.Airport_Code} → {dest.Airport_Code}",
        "total_seats": total_seats
    }

@router.put("/flights/{flight_id}")
def update_flight(
    flight_id: int,
    update_data: FlightUpdate,
    db: Session = Depends(get_db)
):
    flight = db.query(Flight).filter(Flight.FlightID == flight_id).first()
    
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found"
        )
    
    if update_data.Price is not None:
        flight.Price = update_data.Price
    
    if update_data.Flight_status is not None:
        if update_data.Flight_status not in ['scheduled', 'delayed', 'cancelled', 'departed', 'arrived']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid flight status"
            )
        flight.Flight_status = update_data.Flight_status
    
    db.commit()
    
    return {
        "message": "Flight updated successfully",
        "flight_number": flight.Flight_Number,
        "new_price": float(flight.Price) if update_data.Price else None,
        "status": flight.Flight_status
    }

@router.delete("/flights/{flight_id}")
def delete_flight(
    flight_id: int,
    db: Session = Depends(get_db)
):

    flight = db.query(Flight).filter(Flight.FlightID == flight_id).first()
    
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found"
        )
    
    db.delete(flight)
    db.commit()
    
    return {
        "message": "Flight deleted successfully",
        "flight_number": flight.Flight_Number
    }

@router.get("/stats")
def get_system_stats(db: Session = Depends(get_db)):

    from app.models import User, Booking
    
    total_flights = db.query(Flight).count()
    scheduled_flights = db.query(Flight).filter(Flight.Flight_status == 'scheduled').count()
    total_users = db.query(User).count()
    total_bookings = db.query(Booking).count()
    confirmed_bookings = db.query(Booking).filter(Booking.Booking_status == 'confirmed').count()
    total_airlines = db.query(Airline).count()
    total_airports = db.query(Airport).count()
    
    return {
        "flights": {
            "total": total_flights,
            "scheduled": scheduled_flights
        },
        "users": {
            "total": total_users
        },
        "bookings": {
            "total": total_bookings,
            "confirmed": confirmed_bookings,
            "pending": total_bookings - confirmed_bookings
        },
        "airlines": total_airlines,
        "airports": total_airports
    }
