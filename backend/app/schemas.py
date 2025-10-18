from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

# Enums
class SeatClass(str, Enum):
    economy = "economy"
    business = "business"
    first = "first"

class FlightStatus(str, Enum):
    scheduled = "scheduled"
    delayed = "delayed"
    cancelled = "cancelled"
    departed = "departed"
    arrived = "arrived"

class BookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"

class PaymentStatus(str, Enum):
    unpaid = "unpaid"
    paid = "paid"
    refunded = "refunded"

class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"

# Base Schemas
class AirlineBase(BaseModel):
    Airline_Name: str
    Airline_Code: str = Field(..., min_length=2, max_length=3)
    Country: Optional[str] = None

class AirlineResponse(AirlineBase):
    AirlineID: int
    
    class Config:
        from_attributes = True

class AirportBase(BaseModel):
    Airport_Name: str
    Airport_Code: str = Field(..., min_length=3, max_length=3)
    City: str
    Country: str
    Timezone: Optional[str] = None

class AirportResponse(AirportBase):
    AirportID: int
    
    class Config:
        from_attributes = True

# Flight Schemas
class FlightSearchRequest(BaseModel):
    origin: str = Field(..., description="Origin airport code (e.g., DEL)")
    destination: str = Field(..., description="Destination airport code (e.g., BOM)")
    departure_date: date = Field(..., description="Departure date (YYYY-MM-DD)")
    seat_class: Optional[SeatClass] = SeatClass.economy
    passengers: int = Field(default=1, ge=1, le=9)
    max_price: Optional[float] = None
    sort_by: Optional[str] = Field(default="price", description="Sort by: price, duration, departure_time")

class FlightBase(BaseModel):
    Flight_Number: str
    Departure_Time: datetime
    Arrival_Time: datetime
    Duration: int
    Price: float

class FlightDetailResponse(BaseModel):
    FlightID: int
    Flight_Number: str
    airline: AirlineResponse
    departure_airport: AirportResponse
    arrival_airport: AirportResponse
    Departure_Time: datetime
    Arrival_Time: datetime
    Duration: int
    base_price: float
    dynamic_price: float
    Seats_Available: int
    Flight_status: FlightStatus
    seat_inventory: List[dict]
    
    class Config:
        from_attributes = True

class FlightSearchResponse(BaseModel):
    FlightID: int
    Flight_Number: str
    airline_name: str
    airline_code: str
    origin_city: str
    origin_code: str
    destination_city: str
    destination_code: str
    Departure_Time: datetime
    Arrival_Time: datetime
    Duration: int
    base_price: float
    dynamic_price: float
    price_breakdown: dict
    seats_available: int
    seat_class: str
    
    class Config:
        from_attributes = True

# Passenger Schemas
class PassengerCreate(BaseModel):
    First_name: str = Field(..., min_length=2, max_length=100)
    Last_name: str = Field(..., min_length=2, max_length=55)
    Date_of_birth: date
    Gender: Gender
    Passport_number: Optional[str] = None
    Nationality: str = "India"
    Email: EmailStr
    Phone: str = Field(..., regex=r"^\+?[1-9]\d{1,14}$")

class PassengerResponse(PassengerCreate):
    PassengerID: int
    
    class Config:
        from_attributes = True

# Booking Schemas
class BookingCreate(BaseModel):
    FlightID: int
    Seat_class: SeatClass = SeatClass.economy
    passengers: List[PassengerCreate] = Field(..., min_items=1, max_items=9)
    
    @validator('passengers')
    def validate_passengers(cls, v):
        if len(v) < 1:
            raise ValueError('At least one passenger is required')
        return v

class BookingResponse(BaseModel):
    BookingID: int
    pnr: str
    FlightID: int
    flight_details: dict
    Seat_class: SeatClass
    Num_passengers: int
    Total_price: float
    Booking_status: BookingStatus
    Payment_status: PaymentStatus
    Booking_Date: datetime
    Expiry_time: Optional[datetime]
    passengers: List[PassengerResponse]
    
    class Config:
        from_attributes = True

# User Schemas
class UserCreate(BaseModel):
    Email: EmailStr
    Password: str = Field(..., min_length=8)
    First_name: str
    Last_name: str
    Phone: str

class UserLogin(BaseModel):
    Email: EmailStr
    Password: str

class UserResponse(BaseModel):
    UserID: int
    Email: EmailStr
    First_name: str
    Last_name: str
    Phone: Optional[str]
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Price History Schema
class PriceHistoryResponse(BaseModel):
    HistoryID: int
    FlightID: int
    Seat_class: SeatClass
    Calculated_price: float
    Available_seats: int
    Days_to_departure: int
    Recorded_at: datetime
    
    class Config:
        from_attributes = True
