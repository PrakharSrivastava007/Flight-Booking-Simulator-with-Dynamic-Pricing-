from sqlalchemy import text
from database_connection import engine

def test_database_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT DATABASE()"))
            print("Connected to database:", result.fetchone()[0])

            result = connection.execute(text("SELECT * FROM Airlines"))
            airlines = result.fetchall()

            print("\n Airlines in database:")
            for airline in airlines:
                print(f"  - {airline[1]} ({airline[2]})")
    except Exception as e:
        print("Database connection test failed:", str(e))

if __name__ == "__main__":
    test_database_connection()