from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import asyncio
import logging
import os
from dotenv import load_dotenv
from app.middleware.rate_limiter import RateLimitMiddleware
from app.routers import external_flights

# Load environment variables
load_dotenv()

# Import routers
from app.routers import users, flights, bookings, admin, price_history
from app.services.simulator import market_simulator
from app.database_connection import engine, Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Flight Booking API...")
    
    # Create database tables if they don't exist
    # Base.metadata.create_all(bind=engine)  # Uncomment if you want auto-creation
    
    # Start background market simulator
    simulator_interval = int(os.getenv("SIMULATOR_INTERVAL", "300"))  # 5 minutes default
    simulator_task = asyncio.create_task(
        market_simulator.scheduler_loop(interval=simulator_interval)
    )
    logger.info(f"Market simulator started (interval: {simulator_interval}s)")
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("Shutting down Flight Booking API...")
    market_simulator.stop()
    simulator_task.cancel()
    try:
        await simulator_task
    except asyncio.CancelledError:
        pass
    logger.info("Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title=os.getenv("APP_NAME", "Flight Booking Simulator"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="""
    ## Flight Booking Simulator with Dynamic Pricing 🛫
    
    A comprehensive flight booking system featuring:
    
    * **Dynamic Pricing Engine** - Real-time price calculations based on demand
    * **Seat Management** - Concurrent booking with seat locking
    * **User Authentication** - JWT-based secure authentication
    * **Booking Workflow** - Complete booking lifecycle management
    * **Market Simulator** - Background process simulating real-world conditions
    * **Price History** - Track price changes over time
    * **Admin APIs** - Flight management capabilities
    
    ### Features:
    - Indian aviation market optimized pricing
    - Seasonal and peak hour pricing
    - Route-based demand factors
    - Airline tier differentiation
    - Automatic booking expiry
    - Refund processing
    
    ### Authentication:
    1. Register at `/api/v1/users/register`
    2. Login at `/api/v1/users/login` to get access token
    3. Use token in Authorization header: `Bearer <token>`
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration - Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
            "message": "Validation error - please check your request data"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": str(exc),
            "message": "Internal server error"
        }
    )

# Include routers
app.include_router(users.router)
app.include_router(flights.router)
app.include_router(bookings.router)
app.include_router(admin.router)
app.include_router(price_history.router)
app.include_router(external_flights.router)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():

    return {
        "message": "Welcome to Flight Booking Simulator API",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "features": [
            "Dynamic pricing based on demand",
            "Real-time seat availability",
            "Secure user authentication",
            "Background market simulator",
            "Price history tracking",
            "Admin flight management"
        ]
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """
    System health check
    
    Returns status of all services
    """
    from app.database_connection import SessionLocal
    from app.models import Flight, Booking, User
    
    db = SessionLocal()
    try:
        # Check database connectivity
        total_flights = db.query(Flight).count()
        total_bookings = db.query(Booking).count()
        total_users = db.query(User).count()
        
        return {
            "status": "healthy",
            "timestamp": asyncio.get_event_loop().time(),
            "services": {
                "api": "running",
                "database": "connected",
                "simulator": "running" if market_simulator.is_running else "stopped"
            },
            "statistics": {
                "flights": total_flights,
                "bookings": total_bookings,
                "users": total_users
            },
            "simulator": {
                "running": market_simulator.is_running,
                "interval": f"{market_simulator.simulation_interval}s"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
    finally:
        db.close()

@app.get("/api/v1/info", tags=["Info"])
async def api_info():

    return {
        "api_name": "Flight Booking Simulator",
        "version": "1.0.0",
        "endpoints": {
            "users": {
                "register": "POST /api/v1/users/register",
                "login": "POST /api/v1/users/login",
                "profile": "GET /api/v1/users/me"
            },
            "flights": {
                "list_all": "GET /api/v1/flights/",
                "search": "POST /api/v1/flights/search",
                "details": "GET /api/v1/flights/{flight_id}",
                "airlines": "GET /api/v1/flights/airlines/list",
                "airports": "GET /api/v1/flights/airports/list"
            },
            "bookings": {
                "create": "POST /api/v1/bookings/create",
                "confirm": "POST /api/v1/bookings/{pnr}/confirm",
                "my_bookings": "GET /api/v1/bookings/my-bookings",
                "details": "GET /api/v1/bookings/{pnr}",
                "cancel": "DELETE /api/v1/bookings/{pnr}/cancel"
            },
            "admin": {
                "add_flight": "POST /api/v1/admin/flights",
                "update_flight": "PUT /api/v1/admin/flights/{flight_id}",
                "delete_flight": "DELETE /api/v1/admin/flights/{flight_id}",
                "stats": "GET /api/v1/admin/stats"
            },
            "price_history": {
                "history": "GET /api/v1/price-history/{flight_id}",
                "summary": "GET /api/v1/price-history/{flight_id}/summary"
            }
        }
    }

# For running with uvicorn directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
