from datetime import datetime, timedelta
from typing import Dict, Tuple
import random
import math

class DynamicPricingEngine:

    # Indian Holiday Seasons (Peak Travel Months)
    PEAK_MONTHS = [12, 1, 4, 5, 6, 10, 11]  # Dec-Jan (Winter), Apr-Jun (Summer), Oct-Nov (Diwali)
    FESTIVAL_PERIODS = [
        (10, 15, 11, 15),  # Diwali period (Oct 15 - Nov 15)
        (12, 20, 1, 5),    # Christmas-New Year
        (3, 1, 3, 31),     # Holi season
        (4, 15, 6, 15),    # Summer vacation
    ]
    
    # Popular route categories (affects base demand)
    METRO_ROUTES = ['DEL-BOM', 'BOM-DEL', 'DEL-BLR', 'BLR-DEL', 'BOM-BLR', 'BLR-BOM']
    TOURIST_ROUTES = ['BOM-GOI', 'DEL-SXR', 'BLR-GOI', 'DEL-IXL']
    BUSINESS_ROUTES = ['DEL-HYD', 'BOM-HYD', 'BLR-HYD', 'DEL-PNQ']
    
    # Airline tiers (Indian carriers)
    AIRLINE_TIERS = {
        'AI': 'premium',   # Air India
        'UK': 'premium',   # Vistara
        '6E': 'standard',  # IndiGo
        'SG': 'budget',    # SpiceJet
        'I5': 'budget',    # Air Asia
        'G8': 'budget',    # GoFirst
    }
    
    def __init__(self):
        self.base_demand_factor = 1.0
        
    def calculate_price(
        self,
        base_fare: float,
        seats_available: int,
        total_seats: int,
        departure_time: datetime,
        origin_code: str,
        destination_code: str,
        airline_code: str,
        seat_class: str = 'economy'
    ) -> Dict[str, float]:

        
        # Calculate individual factors
        seat_factor = self._calculate_seat_availability_factor(seats_available, total_seats)
        time_factor = self._calculate_time_to_departure_factor(departure_time)
        demand_factor = self._calculate_demand_factor(departure_time, origin_code, destination_code)
        seasonal_factor = self._calculate_seasonal_factor(departure_time)
        weekend_factor = self._calculate_weekend_factor(departure_time)
        peak_hour_factor = self._calculate_peak_hour_factor(departure_time)
        route_factor = self._calculate_route_category_factor(origin_code, destination_code)
        airline_tier_factor = self._calculate_airline_tier_factor(airline_code)
        class_multiplier = self._get_class_multiplier(seat_class)
        
        # Combine all factors
        total_multiplier = (
            1.0 +
            seat_factor +
            time_factor +
            demand_factor +
            seasonal_factor +
            weekend_factor +
            peak_hour_factor +
            route_factor +
            airline_tier_factor
        )
        
        # Apply class multiplier
        final_price = base_fare * total_multiplier * class_multiplier
        
        # Apply realistic bounds (prevent extreme pricing)
        final_price = self._apply_price_bounds(final_price, base_fare)
        
        return {
            'final_price': round(final_price, 2),
            'base_fare': base_fare,
            'seat_factor': round(seat_factor, 3),
            'time_factor': round(time_factor, 3),
            'demand_factor': round(demand_factor, 3),
            'seasonal_factor': round(seasonal_factor, 3),
            'weekend_factor': round(weekend_factor, 3),
            'peak_hour_factor': round(peak_hour_factor, 3),
            'route_factor': round(route_factor, 3),
            'airline_tier_factor': round(airline_tier_factor, 3),
            'class_multiplier': class_multiplier,
            'total_multiplier': round(total_multiplier, 3)
        }
    
    def _calculate_seat_availability_factor(self, seats_available: int, total_seats: int) -> float:

        if total_seats == 0:
            return 0.0
            
        availability_percent = (seats_available / total_seats) * 100
        
        if availability_percent >= 80:
            return -0.10  # Discount to attract customers
        elif availability_percent >= 50:
            return 0.0    # Base price
        elif availability_percent >= 20:
            return 0.20   # Moderate increase
        elif availability_percent >= 10:
            return 0.40   # High demand pricing
        else:
            return 0.60   # Scarcity pricing
    
    def _calculate_time_to_departure_factor(self, departure_time: datetime) -> float:

        now = datetime.now()
        days_until_departure = (departure_time - now).days
        hours_until_departure = (departure_time - now).total_seconds() / 3600
        
        if days_until_departure >= 60:
            return -0.15
        elif days_until_departure >= 30:
            return -0.05
        elif days_until_departure >= 15:
            return 0.0
        elif days_until_departure >= 7:
            return 0.15
        elif days_until_departure >= 3:
            return 0.30
        elif days_until_departure >= 1:
            return 0.50
        elif hours_until_departure >= 1:
            return 0.80
        else:
            return 1.00  # Extreme last minute
    
    def _calculate_seasonal_factor(self, departure_time: datetime) -> float:

        month = departure_time.month
        day = departure_time.day
        
        # Check if in peak month
        if month in self.PEAK_MONTHS:
            base_seasonal = 0.15
        else:
            base_seasonal = 0.0
        
        # Check specific festival periods
        for start_month, start_day, end_month, end_day in self.FESTIVAL_PERIODS:
            if self._is_in_date_range(departure_time, start_month, start_day, end_month, end_day):
                return 0.25  # Maximum seasonal premium
        
        return base_seasonal
    
    def _calculate_weekend_factor(self, departure_time: datetime) -> float:

        day_of_week = departure_time.weekday()  # 0=Monday, 6=Sunday
        hour = departure_time.hour
        
        # Sunday (high demand for return flights)
        if day_of_week == 6:
            return 0.20
        
        # Saturday
        elif day_of_week == 5:
            return 0.15
        
        # Friday evening flights (weekend getaway)
        elif day_of_week == 4 and hour >= 17:
            return 0.18
        
        # Monday morning (business travel)
        elif day_of_week == 0 and hour <= 10:
            return 0.12
        
        return 0.0
    
    def _calculate_peak_hour_factor(self, departure_time: datetime) -> float:

        hour = departure_time.hour
        
        # Early morning flights (5 AM - 8 AM)
        if 5 <= hour < 8:
            return 0.12
        
        # Morning rush (8 AM - 10 AM)
        elif 8 <= hour < 10:
            return 0.08
        
        # Late evening (6 PM - 10 PM)
        elif 18 <= hour < 22:
            return 0.15
        
        # Mid-day off-peak (11 AM - 3 PM)
        elif 11 <= hour < 15:
            return -0.05
        
        # Late night red-eye (10 PM - 5 AM)
        elif hour >= 22 or hour < 5:
            return -0.10
        
        return 0.0
    
    def _calculate_route_category_factor(self, origin: str, destination: str) -> float:

        route = f"{origin}-{destination}"
        
        if route in self.METRO_ROUTES:
            return 0.10  # High demand metro routes
        elif route in self.TOURIST_ROUTES:
            return 0.08  # Popular tourist destinations
        elif route in self.BUSINESS_ROUTES:
            return 0.06  # Business travel routes
        
        return 0.0
    
    def _calculate_airline_tier_factor(self, airline_code: str) -> float:

        tier = self.AIRLINE_TIERS.get(airline_code, 'standard')
        
        if tier == 'premium':
            return 0.10
        elif tier == 'budget':
            return -0.05
        
        return 0.0  # Standard
    
    def _calculate_demand_factor(
        self,
        departure_time: datetime,
        origin: str,
        destination: str
    ) -> float:

        # Base random demand between -5% to +15%
        base_random = random.uniform(-0.05, 0.15)
        
        # Time-sensitive demand spike (closer to departure)
        days_until = (departure_time - datetime.now()).days
        if days_until <= 7:
            demand_spike = random.uniform(0.05, 0.20)
        else:
            demand_spike = 0.0
        
        return base_random + demand_spike
    
    def _get_class_multiplier(self, seat_class: str) -> float:

        multipliers = {
            'economy': 1.0,
            'business': 2.8,
            'first': 4.5
        }
        return multipliers.get(seat_class, 1.0)
    
    def _apply_price_bounds(self, calculated_price: float, base_fare: float) -> float:

        min_price = base_fare * 0.70
        max_price = base_fare * 2.50
        
        return max(min_price, min(calculated_price, max_price))
    
    def _is_in_date_range(
        self,
        check_date: datetime,
        start_month: int,
        start_day: int,
        end_month: int,
        end_day: int
    ) -> bool:
        
        check_month = check_date.month
        check_day = check_date.day
        
        if start_month == end_month:
            return check_month == start_month and start_day <= check_day <= end_day
        elif start_month < end_month:
            return (
                (check_month == start_month and check_day >= start_day) or
                (check_month == end_month and check_day <= end_day) or
                (start_month < check_month < end_month)
            )
        else: 
            return (
                (check_month == start_month and check_day >= start_day) or
                (check_month == end_month and check_day <= end_day) or
                (check_month > start_month or check_month < end_month)
            )


# Global instance
pricing_engine = DynamicPricingEngine()


def get_dynamic_price(
    base_fare: float,
    seats_available: int,
    total_seats: int,
    departure_time: datetime,
    origin_code: str,
    destination_code: str,
    airline_code: str,
    seat_class: str = 'economy'
) -> Dict[str, float]:
    
    return pricing_engine.calculate_price(
        base_fare=base_fare,
        seats_available=seats_available,
        total_seats=total_seats,
        departure_time=departure_time,
        origin_code=origin_code,
        destination_code=destination_code,
        airline_code=airline_code,
        seat_class=seat_class
    )
