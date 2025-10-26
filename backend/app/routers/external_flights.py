from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from typing import List
from app.services.external_airline_api import external_api
import logging

router = APIRouter(prefix="/api/v1/external", tags=["External APIs"])
logger = logging.getLogger(__name__)

@router.get("/flights/fetch")
async def fetch_external_schedules(
    airline_code: str,
    origin: str,
    destination: str,
    date: str
):

    try:
        departure_date = datetime.strptime(date, "%Y-%m-%d")
        
        schedules = await external_api.fetch_flight_schedules(
            airline_code=airline_code.upper(),
            origin=origin.upper(),
            destination=destination.upper(),
            date=departure_date
        )
        
        return {
            "source": "external_api",
            "airline": airline_code,
            "route": f"{origin}->{destination}",
            "date": date,
            "flights_found": len(schedules),
            "schedules": schedules
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    except Exception as e:
        logger.error(f"External API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"External airline API unavailable: {str(e)}"
        )

@router.get("/pricing/{airline_code}/{flight_number}")
async def get_external_pricing(airline_code: str, flight_number: str):
    try:
        pricing_data = await external_api.get_real_time_pricing(
            airline_code=airline_code.upper(),
            flight_number=flight_number.upper()
        )
        
        return {
            "source": "external_pricing_api",
            "data": pricing_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Pricing API unavailable: {str(e)}"
        )

@router.get("/availability/{flight_id}")
async def check_external_availability(flight_id: str, seat_class: str = "economy"):

    try:
        availability = await external_api.check_seat_availability(
            flight_id=flight_id,
            seat_class=seat_class
        )
        
        return {
            "source": "availability_api",
            "data": availability
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Availability API unavailable: {str(e)}"
        )
