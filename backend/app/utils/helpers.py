import random
import string
from datetime import datetime

def generate_pnr() -> str:
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    digits = ''.join(random.choices(string.digits, k=3))
    return f"{letters}{digits}"

def calculate_flight_duration(departure: datetime, arrival: datetime) -> int:
    return int((arrival - departure).total_seconds() / 60)

def format_currency(amount: float) -> str:
    return f"₹{amount:,.2f}"

def validate_airport_code(code: str) -> bool:
    return len(code) == 3 and code.isalpha() and code.isupper()
