from database_connection import SessionLocal
from models import Airline, Airport, Flight

def test_orm_queries():
    db = SessionLocal()
    
    try:
        airlines = db.query(Airline).all()
        print("Airlines using ORM:")
        for airline in airlines:
            print(f"  - {airline.Airline_Name} ({airline.Airline_Code})")

        flights = db.query(Flight).join(Airline).limit(5).all()
        print("\n Sample Flights:")
        for flight in flights:
            print(f"  - {flight.Flight_Number}: {flight.airline.Airline_Name}")
            
    except Exception as e:
        print("Error:", str(e))
    finally:
        db.close()

if __name__ == "__main__":
    test_orm_queries()
