from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Enum, ForeignKey, TIMESTAMP, Text, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database_connection import Base

class User(Base):
    __tablename__ = "Users"
    
    UserID = Column(Integer, primary_key=True, autoincrement=True)
    Email = Column(String(100), nullable=False, unique=True, index=True)
    PasswordHash = Column(String(255), nullable=False)
    First_name = Column(String(100), nullable=False)
    Last_name = Column(String(55), nullable=False)
    Phone = Column(String(15))
    CreatedAt = Column(TIMESTAMP, default=datetime.utcnow)
    UpdatedAt = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    bookings = relationship("Booking", back_populates="user")

class Airline(Base):
    __tablename__ = "Airlines"
    
    AirlineID = Column(Integer, primary_key=True, autoincrement=True)
    Airline_Name = Column(String(100), nullable=False, unique=True)
    Airline_Code = Column(String(3), nullable=False, unique=True)
    Country = Column(String(100))
    contact_email = Column(String(100))
    contact_phone = Column(String(15))
    CreatedAt = Column(TIMESTAMP)
    
    
    flights = relationship("Flight", back_populates="airline")


class Airport(Base):
    __tablename__ = "Airports"
    
    AirportID = Column(Integer, primary_key=True, autoincrement=True)
    Airport_Name = Column(String(100), nullable=False)
    Airport_Code = Column(String(3), nullable=False, unique=True)
    City = Column(String(100), nullable=False)
    Country = Column(String(100), nullable=False)
    Timezone = Column(String(50))
    CreatedAt = Column(TIMESTAMP)


class Flight(Base):
    __tablename__ = "Flights"
    
    FlightID = Column(Integer, primary_key=True, autoincrement=True)
    AirlineID = Column(Integer, ForeignKey("Airlines.AirlineID"), nullable=False)
    Flight_Number = Column(String(10), nullable=False, unique=True)
    Departure_AirportID = Column(Integer, ForeignKey("Airports.AirportID"), nullable=False)
    Arrival_AirportID = Column(Integer, ForeignKey("Airports.AirportID"), nullable=False)
    Departure_Time = Column(DateTime, nullable=False)
    Arrival_Time = Column(DateTime, nullable=False)
    Duration = Column(Integer)
    Price = Column(DECIMAL(10, 2), nullable=False)
    Seats_Available = Column(Integer, default=0)
    Flight_status = Column(Enum('scheduled', 'delayed', 'cancelled', 'departed', 'arrived'), default='scheduled')
    CreatedAt = Column(TIMESTAMP,default=datetime.utcnow)
    
    airline = relationship("Airline", back_populates="flights")
    departure_airport = relationship("Airport", foreign_keys=[Departure_AirportID])
    arrival_airport = relationship("Airport", foreign_keys=[Arrival_AirportID])
    seat_inventory = relationship("SeatInventory", back_populates="flight")
    bookings = relationship("Booking", back_populates="flight")
    price_history = relationship("PriceHistory", back_populates="flight")

class SeatInventory(Base):
    __tablename__ = "Seat_Inventory"
    
    Inventory_ID = Column(Integer, primary_key=True, autoincrement=True)
    FlightID = Column(Integer, ForeignKey("Flights.FlightID"), nullable=False)
    Class = Column(Enum('economy', 'business', 'first'), default='economy')
    Total_Seats = Column(Integer, nullable=False)
    Available_seats = Column(Integer, nullable=False)
    Price = Column(DECIMAL(4, 2), default=1.00)  # Price multiplier
    Last_updated = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    flight = relationship("Flight", back_populates="seat_inventory")

class Booking(Base):
    __tablename__ = "Bookings"
    
    BookingID = Column(Integer, primary_key=True, autoincrement=True)
    pnr = Column(String(6), nullable=False, unique=True, index=True)
    UserID = Column(Integer, ForeignKey("Users.UserID"), nullable=False)
    FlightID = Column(Integer, ForeignKey("Flights.FlightID"), nullable=False)
    Seat_class = Column(Enum('economy', 'business', 'first'), default='economy')
    Num_passengers = Column(Integer, nullable=False)
    Total_price = Column(DECIMAL(10, 2), nullable=False)
    Booking_status = Column(
        Enum('pending', 'confirmed', 'cancelled'),
        default='pending'
    )
    Payment_status = Column(
        Enum('unpaid', 'paid', 'refunded'),
        default='unpaid'
    )
    Booking_Date = Column(TIMESTAMP, default=datetime.utcnow)
    Payment_date = Column(TIMESTAMP, nullable=True)
    Expiry_time = Column(TIMESTAMP, nullable=True)
    
    
    user = relationship("User", back_populates="bookings")
    flight = relationship("Flight", back_populates="bookings")
    passengers = relationship("Passenger", back_populates="booking")
    transactions = relationship("PaymentTransaction", back_populates="booking")


class Passenger(Base):
    __tablename__ = "Passengers"
    
    PassengerID = Column(Integer, primary_key=True, autoincrement=True)
    BookingID = Column(Integer, ForeignKey("Bookings.BookingID"), nullable=False)
    First_name = Column(String(100), nullable=False)
    Last_name = Column(String(55), nullable=False)
    Date_of_birth = Column(Date, nullable=False)
    Gender = Column(Enum('male', 'female', 'other'), nullable=False)
    Passport_number = Column(String(20))
    Nationality = Column(String(50))
    Email = Column(String(100))
    Phone = Column(String(15))
    
    
    booking = relationship("Booking", back_populates="passengers")


class PricingRule(Base):
    __tablename__ = "Pricing_rules"
    
    RuleID = Column(Integer, primary_key=True, autoincrement=True)
    Rule_name = Column(String(100), nullable=False)
    Rule_type = Column(
        Enum('time_based', 'demand_based', 'seasonal'),
        nullable=False
    )
    Multiplier_min = Column(DECIMAL(4, 2), nullable=False)
    Multiplier_max = Column(DECIMAL(4, 2), nullable=False)
    Is_active = Column(Boolean, default=True)
    Created_at = Column(TIMESTAMP, default=datetime.utcnow)


class PriceHistory(Base):
    __tablename__ = "Price_history"
    
    HistoryID = Column(Integer, primary_key=True, autoincrement=True)
    FlightID = Column(Integer, ForeignKey("Flights.FlightID"), nullable=False)
    Seat_class = Column(Enum('economy', 'business', 'first'), default='economy')
    Calculated_price = Column(DECIMAL(10, 2), nullable=False)
    Available_seats = Column(Integer, nullable=False)
    Days_to_departure = Column(Integer, nullable=False)
    Recorded_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    
    
    flight = relationship("Flight", back_populates="price_history")


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    
    TransactionID = Column(Integer, primary_key=True, autoincrement=True)
    BookingID = Column(Integer, ForeignKey("Bookings.BookingID"), nullable=False)
    Payment_method = Column(
        Enum('credit_card', 'debit_card', 'upi', 'netbanking', 'wallet'),
        nullable=False
    )
    Transaction_amount = Column(DECIMAL(10, 2), nullable=False)
    Transaction_status = Column(
        Enum('pending', 'success', 'failed', 'refunded'),
        nullable=False
    )
    Payment_gateway_response = Column(Text)
    Transaction_date = Column(TIMESTAMP, default=datetime.utcnow)
    
    
    booking = relationship("Booking", back_populates="transactions")