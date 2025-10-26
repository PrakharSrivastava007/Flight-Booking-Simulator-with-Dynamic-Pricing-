import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

class ExternalAirlineAPI:
    
    def __init__(self):
        self.api_response_time = 0.5  # Simulate network delay (seconds)
        self.api_failure_rate = 0.05  # 5% failure rate to simulate real-world
        
    async def fetch_flight_schedules(
        self,
        airline_code: str,
        origin: str,
        destination: str,
        date: datetime
    ) -> List[Dict]:

        # Simulate API call delay
        await asyncio.sleep(self.api_response_time)
        
        # Simulate occasional API failures
        if random.random() < self.api_failure_rate:
            raise Exception(f"External API timeout for {airline_code}")
        
        logger.info(f"Fetching external schedules: {airline_code} {origin}->{destination}")
        
        # Simulated response from external API
        schedules = [
            {
                "external_id": f"EXT_{airline_code}_{random.randint(1000, 9999)}",
                "airline_code": airline_code,
                "flight_number": f"{airline_code}{random.randint(100, 999)}",
                "origin": origin,
                "destination": destination,
                "departure_time": date + timedelta(hours=random.randint(6, 20)),
                "arrival_time": date + timedelta(hours=random.randint(8, 22)),
                "aircraft_type": random.choice(["Boeing 737", "Airbus A320", "ATR 72"]),
                "available_seats": random.randint(50, 180),
                "base_fare": random.uniform(3000, 8000),
                "amenities": ["WiFi", "Meals"] if random.random() > 0.5 else ["Snacks"],
                "baggage_allowance": "15kg check-in + 7kg cabin",
                "source": f"{airline_code}_API"
            }
            for _ in range(random.randint(2, 5))  # 2-5 flights
        ]
        
        return schedules
    
    async def get_real_time_pricing(
        self,
        airline_code: str,
        flight_number: str
    ) -> Dict:

        # Simulate fetching real-time pricing from airline API

        await asyncio.sleep(0.3)
        
        return {
            "flight_number": flight_number,
            "airline_code": airline_code,
            "economy": {
                "fare": random.uniform(4000, 7000),
                "available": random.randint(10, 100),
                "fare_class": random.choice(["L", "M", "K", "T"])
            },
            "business": {
                "fare": random.uniform(12000, 20000),
                "available": random.randint(5, 30),
                "fare_class": random.choice(["C", "D", "J"])
            },
            "timestamp": datetime.now().isoformat(),
            "source": f"{airline_code}_Pricing_API"
        }
    
    async def check_seat_availability(
        self,
        flight_id: str,
        seat_class: str
    ) -> Dict:
        
        # Simulate checking real-time seat availability
       
        await asyncio.sleep(0.2)
        
        return {
            "flight_id": flight_id,
            "seat_class": seat_class,
            "available": random.randint(5, 50),
            "status": random.choice(["Available", "Limited", "Waitlist"]),
            "last_updated": datetime.now().isoformat()
        }

# Global instance
external_api = ExternalAirlineAPI()
