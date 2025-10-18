# Flight search and listing endpoints with dynamic pricing


from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, date
from typing import List, Optional
from app.database_connection import get_db
from app.models import Flight, Airline, Airport, SeatInventory
from app.schemas import (
    FlightSearchRequest,
    FlightSearchResponse,
    FlightDetailResponse,
    AirlineResponse,
    AirportResponse
)
from app.services.pricing_engine import get_dynamic_price

router = APIRouter(prefix="/api/v1/flights", tags=["Flights"])

@router.get("/", response_model=List[FlightSearchResponse])
def list_all_flights(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):

    flights = db.query(Flight).offset(skip).limit(limit).all()
    
    result = []
    for flight in flights:
        # Get airline and airport details
        airline = db.query(Airline).filter(Airline.AirlineID == flight.AirlineID).first()
        origin_airport = db.query(Airport).filter(Airport.AirportID == flight.Departure_AirportID).first()
        dest_airport = db.query(Airport).filter(Airport.AirportID == flight.Arrival_AirportID).first()
        
        # Get seat inventory
        seat_inv = db.query(SeatInventory).filter(
            SeatInventory.FlightID == flight.FlightID,
            SeatInventory.Class == 'economy'
        ).first()
        
        if not seat_inv:
            continue
        
        # Calculate dynamic price
        price_data = get_dynamic_price(
            base_fare=float(flight.Price),
            seats_available=seat_inv.Available_seats,
            total_seats=seat_inv.Total_Seats,
            departure_time=flight.Departure_Time,
            origin_code=origin_airport.Airport_Code,
            destination_code=dest_airport.Airport_Code,
            airline_code=airline.Airline_Code,
            seat_class='economy'
        )
        
        result.append(FlightSearchResponse(
            FlightID=flight.FlightID,
            Flight_Number=flight.Flight_Number,
            airline_name=airline.Airline_Name,
            airline_code=airline.Airline_Code,
            origin_city=origin_airport.City,
            origin_code=origin_airport.Airport_Code,
            destination_city=dest_airport.City,
            destination_code=dest_airport.Airport_Code,
            Departure_Time=flight.Departure_Time,
            Arrival_Time=flight.Arrival_Time,
            Duration=flight.Duration,
            base_price=float(flight.Price),
            dynamic_price=price_data['final_price'],
            price_breakdown=price_data,
            seats_available=seat_inv.Available_seats,
            seat_class='economy'
        ))
    
    return result

@router.post("/search", response_model=List[FlightSearchResponse])
def search_flights(
    search: FlightSearchRequest,
    db: Session = Depends(get_db)
):

    # Get airport IDs
    origin_airport = db.query(Airport).filter(Airport.Airport_Code == search.origin.upper()).first()
    dest_airport = db.query(Airport).filter(Airport.Airport_Code == search.destination.upper()).first()
    
    if not origin_airport or not dest_airport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid airport code"
        )
    
    # Build query
    query = db.query(Flight).filter(
        and_(
            Flight.Departure_AirportID == origin_airport.AirportID,
            Flight.Arrival_AirportID == dest_airport.AirportID,
            Flight.Departure_Time >= datetime.combine(search.departure_date, datetime.min.time()),
            Flight.Departure_Time < datetime.combine(search.departure_date, datetime.max.time()),
            Flight.Flight_status == 'scheduled'
        )
    )
    
    flights = query.all()
    
    if not flights:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No flights found from {search.origin} to {search.destination} on {search.departure_date}"
        )
    
    result = []
    for flight in flights:
        airline = db.query(Airline).filter(Airline.AirlineID == flight.AirlineID).first()
        
        # Get seat inventory for requested class
        seat_inv = db.query(SeatInventory).filter(
            and_(
                SeatInventory.FlightID == flight.FlightID,
                SeatInventory.Class == search.seat_class
            )
        ).first()
        
        if not seat_inv or seat_inv.Available_seats < search.passengers:
            continue  # Skip if not enough seats
        
        # Calculate dynamic price
        price_data = get_dynamic_price(
            base_fare=float(flight.Price),
            seats_available=seat_inv.Available_seats,
            total_seats=seat_inv.Total_Seats,
            departure_time=flight.Departure_Time,
            origin_code=search.origin.upper(),
            destination_code=search.destination.upper(),
            airline_code=airline.Airline_Code,
            seat_class=search.seat_class
        )
        
        # Apply max price filter
        if search.max_price and price_data['final_price'] > search.max_price:
            continue
        
        result.append(FlightSearchResponse(
            FlightID=flight.FlightID,
            Flight_Number=flight.Flight_Number,
            airline_name=airline.Airline_Name,
            airline_code=airline.Airline_Code,
            origin_city=origin_airport.City,
            origin_code=origin_airport.Airport_Code,
            destination_city=dest_airport.City,
            destination_code=dest_airport.Airport_Code,
            Departure_Time=flight.Departure_Time,
            Arrival_Time=flight.Arrival_Time,
            Duration=flight.Duration,
            base_price=float(flight.Price),
            dynamic_price=price_data['final_price'],
            price_breakdown=price_data,
            seats_available=seat_inv.Available_seats,
            seat_class=search.seat_class
        ))
    
    # Sort results
    if search.sort_by == "price":
        result.sort(key=lambda x: x.dynamic_price)
    elif search.sort_by == "duration":
        result.sort(key=lambda x: x.Duration)
    elif search.sort_by == "departure_time":
        result.sort(key=lambda x: x.Departure_Time)
    
    return result

@router.get("/{flight_id}", response_model=FlightDetailResponse)
def get_flight_details(flight_id: int, db: Session = Depends(get_db)):

    flight = db.query(Flight).filter(Flight.FlightID == flight_id).first()
    
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight with ID {flight_id} not found"
        )
    
    # Get related data
    airline = db.query(Airline).filter(Airline.AirlineID == flight.AirlineID).first()
    origin_airport = db.query(Airport).filter(Airport.AirportID == flight.Departure_AirportID).first()
    dest_airport = db.query(Airport).filter(Airport.AirportID == flight.Arrival_AirportID).first()
    seat_inventories = db.query(SeatInventory).filter(SeatInventory.FlightID == flight_id).all()
    
    # Calculate dynamic prices for all classes
    seat_inventory_data = []
    total_available = 0
    
    for seat_inv in seat_inventories:
        price_data = get_dynamic_price(
            base_fare=float(flight.Price),
            seats_available=seat_inv.Available_seats,
            total_seats=seat_inv.Total_Seats,
            departure_time=flight.Departure_Time,
            origin_code=origin_airport.Airport_Code,
            destination_code=dest_airport.Airport_Code,
            airline_code=airline.Airline_Code,
            seat_class=seat_inv.Class
        )
        
        seat_inventory_data.append({
            "class": seat_inv.Class,
            "total_seats": seat_inv.Total_Seats,
            "available_seats": seat_inv.Available_seats,
            "base_price": float(flight.Price),
            "dynamic_price": price_data['final_price'],
            "price_breakdown": price_data
        })
        
        total_available += seat_inv.Available_seats
    
    return FlightDetailResponse(
        FlightID=flight.FlightID,
        Flight_Number=flight.Flight_Number,
        airline=AirlineResponse(
            AirlineID=airline.AirlineID,
            Airline_Name=airline.Airline_Name,
            Airline_Code=airline.Airline_Code,
            Country=airline.Country
        ),
        departure_airport=AirportResponse(
            AirportID=origin_airport.AirportID,
            Airport_Name=origin_airport.Airport_Name,
            Airport_Code=origin_airport.Airport_Code,
            City=origin_airport.City,
            Country=origin_airport.Country,
            Timezone=origin_airport.Timezone
        ),
        arrival_airport=AirportResponse(
            AirportID=dest_airport.AirportID,
            Airport_Name=dest_airport.Airport_Name,
            Airport_Code=dest_airport.Airport_Code,
            City=dest_airport.City,
            Country=dest_airport.Country,
            Timezone=dest_airport.Timezone
        ),
        Departure_Time=flight.Departure_Time,
        Arrival_Time=flight.Arrival_Time,
        Duration=flight.Duration,
        base_price=float(flight.Price),
        dynamic_price=seat_inventory_data[0]['dynamic_price'] if seat_inventory_data else 0.0,
        Seats_Available=total_available,
        Flight_status=flight.Flight_status,
        seat_inventory=seat_inventory_data
    )

@router.get("/airlines/list", response_model=List[AirlineResponse])
def list_airlines(db: Session = Depends(get_db)):
    airlines = db.query(Airline).all()
    return airlines

@router.get("/airports/list", response_model=List[AirportResponse])
def list_airports(db: Session = Depends(get_db)):
    airports = db.query(Airport).all()
    return airports

@router.get("/health")
def flight_service_health(db: Session = Depends(get_db)):
    total_flights = db.query(Flight).count()
    scheduled_flights = db.query(Flight).filter(Flight.Flight_status == 'scheduled').count()
    
    return {
        "status": "healthy",
        "service": "flights",
        "total_flights": total_flights,
        "scheduled_flights": scheduled_flights
    }
