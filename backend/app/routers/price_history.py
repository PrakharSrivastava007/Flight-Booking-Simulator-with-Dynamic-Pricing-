# Price history tracking endpoints

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.database_connection import get_db
from app.models import PriceHistory, Flight
from app.schemas import PriceHistoryResponse

router = APIRouter(prefix="/api/v1/price-history", tags=["Price History"])

@router.get("/{flight_id}", response_model=List[PriceHistoryResponse])
def get_price_history(
    flight_id: int,
    seat_class: str = 'economy',
    days: int = 7,
    db: Session = Depends(get_db)
):
    flight = db.query(Flight).filter(Flight.FlightID == flight_id).first()
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found"
        )
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    history = db.query(PriceHistory).filter(
        PriceHistory.FlightID == flight_id,
        PriceHistory.Seat_class == seat_class,
        PriceHistory.Recorded_at >= cutoff_date
    ).order_by(PriceHistory.Recorded_at.desc()).all()
    
    return history

@router.get("/{flight_id}/summary")
def get_price_summary(
    flight_id: int,
    seat_class: str = 'economy',
    db: Session = Depends(get_db)
):

    from sqlalchemy import func
    
    flight = db.query(Flight).filter(Flight.FlightID == flight_id).first()
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found"
        )
    
    stats = db.query(
        func.min(PriceHistory.Calculated_price).label('min_price'),
        func.max(PriceHistory.Calculated_price).label('max_price'),
        func.avg(PriceHistory.Calculated_price).label('avg_price'),
        func.count(PriceHistory.HistoryID).label('data_points')
    ).filter(
        PriceHistory.FlightID == flight_id,
        PriceHistory.Seat_class == seat_class
    ).first()
    
    # Get most recent price
    latest = db.query(PriceHistory).filter(
        PriceHistory.FlightID == flight_id,
        PriceHistory.Seat_class == seat_class
    ).order_by(PriceHistory.Recorded_at.desc()).first()
    
    return {
        "flight_id": flight_id,
        "seat_class": seat_class,
        "min_price": float(stats.min_price) if stats.min_price else 0.0,
        "max_price": float(stats.max_price) if stats.max_price else 0.0,
        "avg_price": float(stats.avg_price) if stats.avg_price else 0.0,
        "current_price": float(latest.Calculated_price) if latest else 0.0,
        "data_points": stats.data_points,
        "last_updated": latest.Recorded_at if latest else None
    }
