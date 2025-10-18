import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database_connection import SessionLocal
from app.models import Flight, SeatInventory, PriceHistory, Booking
from app.services.pricing_engine import get_dynamic_price
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketSimulator:

    def __init__(self):
        self.is_running = False
        self.simulation_interval = 300  # 5 minutes (300 seconds)
    
    async def simulate_market_step(self):

        db = SessionLocal()
        
        try:
            # Get all scheduled flights in the next 60 days
            future_date = datetime.now() + timedelta(days=60)
            flights = db.query(Flight).filter(
                and_(
                    Flight.Flight_status == 'scheduled',
                    Flight.Departure_Time > datetime.now(),
                    Flight.Departure_Time <= future_date
                )
            ).all()
            
            if not flights:
                logger.info("No flights to simulate")
                return
            
            # Simulate market activity for random subset of flights
            num_flights_to_update = min(len(flights), random.randint(5, 15))
            selected_flights = random.sample(flights, num_flights_to_update)
            
            logger.info(f"Simulating market for {num_flights_to_update} flights")
            
            for flight in selected_flights:
                await self._simulate_flight_activity(flight, db)
            
            # Auto-expire pending bookings
            await self._expire_pending_bookings(db)
            
            db.commit()
            logger.info("Market simulation step completed")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Simulation error: {e}")
        finally:
            db.close()
    
    async def _simulate_flight_activity(self, flight: Flight, db: Session):
        
        from app.models import Airline, Airport
        
        # Get flight details
        airline = db.query(Airline).filter(Airline.AirlineID == flight.AirlineID).first()
        origin = db.query(Airport).filter(Airport.AirportID == flight.Departure_AirportID).first()
        dest = db.query(Airport).filter(Airport.AirportID == flight.Arrival_AirportID).first()
        
        # Get seat inventories
        seat_inventories = db.query(SeatInventory).filter(
            SeatInventory.FlightID == flight.FlightID
        ).all()
        
        for seat_inv in seat_inventories:
            # Calculate days until departure
            days_to_departure = (flight.Departure_Time - datetime.now()).days
            
            # Determine activity probability based on time to departure
            if days_to_departure <= 7:
                activity_chance = 0.7  # High activity close to departure
            elif days_to_departure <= 30:
                activity_chance = 0.5  # Moderate activity
            else:
                activity_chance = 0.3  # Lower activity for far future
            
            # Decide if any activity happens for this flight
            if random.random() > activity_chance:
                continue
            
            # Simulate bookings (reduce availability)
            if seat_inv.Available_seats > 0 and random.random() < 0.6:  # 60% chance of booking
                # Book 1-3 seats
                seats_to_book = min(
                    random.randint(1, 3),
                    seat_inv.Available_seats
                )
                seat_inv.Available_seats -= seats_to_book
                logger.info(
                    f"Simulated booking: {seats_to_book} seats on {flight.Flight_Number} "
                    f"({seat_inv.Class}) - {seat_inv.Available_seats}/{seat_inv.Total_Seats} remaining"
                )
            
            # Simulate cancellations (increase availability)
            elif seat_inv.Available_seats < seat_inv.Total_Seats and random.random() < 0.2:  # 20% chance
                seats_to_release = min(
                    random.randint(1, 2),
                    seat_inv.Total_Seats - seat_inv.Available_seats
                )
                seat_inv.Available_seats += seats_to_release
                logger.info(
                    f"Simulated cancellation: {seats_to_release} seats on {flight.Flight_Number} "
                    f"({seat_inv.Class}) - {seat_inv.Available_seats}/{seat_inv.Total_Seats} available"
                )
            
            # Calculate and record new price
            price_data = get_dynamic_price(
                base_fare=float(flight.Price),
                seats_available=seat_inv.Available_seats,
                total_seats=seat_inv.Total_Seats,
                departure_time=flight.Departure_Time,
                origin_code=origin.Airport_Code,
                destination_code=dest.Airport_Code,
                airline_code=airline.Airline_Code,
                seat_class=seat_inv.Class
            )
            
            # Store price history
            price_record = PriceHistory(
                FlightID=flight.FlightID,
                Seat_class=seat_inv.Class,
                Calculated_price=price_data['final_price'],
                Available_seats=seat_inv.Available_seats,
                Days_to_departure=max(0, days_to_departure)
            )
            db.add(price_record)
            
            logger.info(
                f"Price update: {flight.Flight_Number} ({seat_inv.Class}) - "
                f"₹{price_data['final_price']:.2f} "
                f"(base: ₹{float(flight.Price):.2f})"
            )
    
    async def _expire_pending_bookings(self, db: Session):

        now = datetime.now()
        
        expired_bookings = db.query(Booking).filter(
            and_(
                Booking.Booking_status == 'pending',
                Booking.Expiry_time <= now,
                Booking.Expiry_time.isnot(None)
            )
        ).all()
        
        if not expired_bookings:
            return
        
        logger.info(f"Expiring {len(expired_bookings)} pending bookings")
        
        for booking in expired_bookings:
            # Release seats back to inventory
            seat_inv = db.query(SeatInventory).filter(
                and_(
                    SeatInventory.FlightID == booking.FlightID,
                    SeatInventory.Class == booking.Seat_class
                )
            ).first()
            
            if seat_inv:
                seat_inv.Available_seats += booking.Num_passengers
                logger.info(
                    f"Released {booking.Num_passengers} seats for expired booking {booking.pnr}"
                )
            
            # Update booking status
            booking.Booking_status = 'cancelled'
        
        logger.info("Expired bookings processed")
    
    async def scheduler_loop(self, interval: int = None):

        if interval:
            self.simulation_interval = interval
        
        self.is_running = True
        logger.info(f"Market simulator started (interval: {self.simulation_interval}s)")
        
        while self.is_running:
            try:
                await self.simulate_market_step()
                await asyncio.sleep(self.simulation_interval)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def stop(self):
        self.is_running = False
        logger.info("Market simulator stopped")

market_simulator = MarketSimulator()
