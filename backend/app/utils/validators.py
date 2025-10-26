from datetime import datetime, date, timedelta
from fastapi import HTTPException, status

class BookingValidator:
    # Validation rules for booking operations
    
    MIN_PASSENGERS = 1
    MAX_PASSENGERS = 9
    MIN_BOOKING_ADVANCE_HOURS = 2  # Must book at least 2 hours before departure
    MAX_BOOKING_ADVANCE_DAYS = 365  # Can't book more than 1 year ahead
    
    @staticmethod
    def validate_departure_date(departure_date: date) -> None:
        # Validate departure date is within acceptable range
        today = date.today()
        max_date = today + timedelta(days=BookingValidator.MAX_BOOKING_ADVANCE_DAYS)
        
        if departure_date < today:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot book flights in the past"
            )
        
        if departure_date > max_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot book more than {BookingValidator.MAX_BOOKING_ADVANCE_DAYS} days in advance"
            )
    
    @staticmethod
    def validate_departure_time(departure_time: datetime) -> None:
        # Validate departure time allows minimum advance booking
        now = datetime.now()
        min_departure = now + timedelta(hours=BookingValidator.MIN_BOOKING_ADVANCE_HOURS)
        
        if departure_time < min_departure:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Must book at least {BookingValidator.MIN_BOOKING_ADVANCE_HOURS} hours before departure"
            )
    
    @staticmethod
    def validate_passenger_count(count: int) -> None:
        # Validate number of passengers
        if count < BookingValidator.MIN_PASSENGERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Minimum {BookingValidator.MIN_PASSENGERS} passenger required"
            )
        
        if count > BookingValidator.MAX_PASSENGERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {BookingValidator.MAX_PASSENGERS} passengers allowed per booking"
            )
    
    @staticmethod
    def validate_passenger_age(date_of_birth: date) -> str:
        # Validate passenger age and return category
        today = date.today()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        
        if age < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date of birth"
            )
        
        if age > 120:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid age"
            )
        
        # Return passenger category
        if age < 2:
            return "infant"
        elif age < 12:
            return "child"
        else:
            return "adult"
