from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from database_connection import Base

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
    CreatedAt = Column(TIMESTAMP)
    
    airline = relationship("Airline", back_populates="flights")
