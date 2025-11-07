# Flight Booking System with Dynamic Pricing

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)
![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?logo=mysql&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?logo=javascript&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

> An intelligent flight booking platform with dynamic pricing engine built for modern web applications.

[Features](#-features) • [Tech Stack](#-tech-stack) • [Installation](#-installation) • [Usage](#-usage) • [API Docs](#-api-documentation)

---

##  Overview

A full-stack flight booking application that simulates real-world airline reservation systems with intelligent dynamic pricing. This project demonstrates advanced backend development, RESTful API design, database management, and responsive frontend development.

### 🎯 Key Highlights

- **Dynamic Pricing Engine**: 8+ factors including demand, seasonality, time-to-departure, and seat availability
- **Secure Authentication**: JWT-based user authentication with bcrypt password hashing
- **Payment Integration**: Multiple payment methods (UPI, Cards, Net Banking, Wallets)
- **Real-time Updates**: Background market simulator for realistic price fluctuations
- **Receipt Generation**: Automatic PDF and JSON receipt downloads
- **Responsive Design**: Mobile-first approach with intuitive user experience
- **Concurrency Safe**: Proper seat locking mechanism for concurrent bookings

---

##  Features

### User Features
-  User Registration & Login with JWT authentication
-  Advanced Flight Search (origin, destination, date, class)
-  Real-time Dynamic Pricing based on market conditions
-  Multi-passenger Booking (1-9 passengers)
-  Multiple Payment Options
-  PDF & JSON Receipt Downloads
-  Booking Management (view, cancel, history)

### Admin Features
-  Flight Management (add, update, delete)
-  System Statistics & Analytics
-  Price Control & Adjustments
-  User Activity Monitoring

### Advanced Features
-  Background Market Simulator
-  Historical Price Tracking
-  External API Integration
-  Auto-expire Pending Bookings (15 min)
-  API Rate Limiting

---

## Tech Stack

### Backend
- **Python 3.9+** - Core language
- **FastAPI 0.104.1** - Web framework
- **SQLAlchemy 2.0.23** - ORM
- **MySQL 8.0+** - Database
- **JWT & Bcrypt** - Security
- **APScheduler** - Background tasks

### Frontend
- **HTML5, CSS3, JavaScript (ES6+)**
- **jsPDF** - PDF generation
- **Font Awesome** - Icons

---

##  Project Structure

    Flight-Booking-System/
    ├── flight_booking_backend/
    │ ├── app/
    │ │ ├── main.py # FastAPI entry point
    │ │ ├── models.py # Database models
    │ │ ├── schemas.py # Pydantic schemas
    │ │ ├── database_connection.py
    │ │ ├── routers/ # API endpoints
    │ │ ├── services/ # Business logic
    │ │ ├── utils/ # Utilities
    │ │ └── middleware/ # Middleware
    │ ├── requirements.txt
    │ ├── .env.example
    │ └── README.md
    ├── frontend/
    │ ├── *.html # Pages
    │ ├── css/ # Stylesheets
    │ └── js/ # JavaScript
    └── database/
    └── database.sql # Schema & data

---

## Prerequisites

- Python 3.9 or higher
- MySQL 8.0 or higher
- Modern web browser (Chrome 90+, Firefox 88+)
- Git (optional)

---

## Installation

### 1. Clone Repository

    git clone https://github.com/yourusername/flight-booking-system.git
    cd flight-booking-system

### 2. Setup Database

    Start MySQL
    mysql -u root -p

    Create database
    CREATE DATABASE Flight_Booking;
    USE Flight_Booking;
    SOURCE database/database.sql;


### 3. Setup Backend

    cd flight_booking_backend

    Create virtual environment
    python -m venv venv

    Activate virtual environment
    Windows: venv\Scripts\activate

    macOS/Linux: source venv/bin/activate

    Install dependencies
    pip install -r requirements.txt

    Create .env file
    cp .env.example .env

    Edit .env with your database credentials

### 4. Configure Environment

    Create `.env` file in `flight_booking_backend/`:

    DB_HOST=localhost
    DB_PORT=3306
    DB_USER=root
    DB_PASSWORD=your_mysql_password
    DB_NAME=Flight_Booking

    SECRET_KEY=your-secret-key-minimum-32-characters-long
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30

    APP_NAME=Flight Booking System
    APP_VERSION=1.0.0
    SIMULATOR_INTERVAL=300

---

## Running the Application

### Start Backend

    cd flight_booking_backend source venv/bin/activate 
    # or venv\Scripts\activate on Windows uvicorn 
    app.main:app --reload --host 0.0.0.0 --port 8000

### Start Frontend

**Option 1: VS Code Live Server (Recommended)**
1. Open `frontend/index.html` in VS Code
2. Right-click → "Open with Live Server"

**Option 2: Python HTTP Server**

    cd frontend
    python -m http.server 8080

### Access Application

- **Frontend**: http://localhost:5500 (or 8080)
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

### Key Endpoints

**Authentication**
- POST /api/v1/users/register # Register new user
- POST /api/v1/users/login # Login user
- GET /api/v1/users/me # Get user profile

**Flights**
- POST /api/v1/flights/search # Search flights
- GET /api/v1/flights/{id} # Get flight details
- GET /api/v1/flights/airlines/list
- GET /api/v1/flights/airports/list

**Bookings**
- POST /api/v1/bookings/create
- POST /api/v1/bookings/{pnr}/confirm
- GET /api/v1/bookings/my-bookings
- DELETE /api/v1/bookings/{pnr}/cancel

---

## Database Schema

### Main Tables
- **Users** - User accounts
- **Airlines** - Airline companies (6 records)
- **Airports** - Airport locations (20 records)
- **Flights** - Flight schedules (33 records)
- **SeatInventory** - Seat availability
- **Bookings** - User reservations
- **Passengers** - Passenger details
- **PaymentTransactions** - Payment records
- **PriceHistory** - Historical pricing
- **PricingRules** - Dynamic pricing rules

---

## Testing

### Test Backend

    Health check
    curl http://localhost:8000/health

    Test in Swagger UI
    Navigate to http://localhost:8000/docs

### Test Frontend
1. Register a new account
2. Login with credentials
3. Search for flights (DEL → BOM)
4. Complete a booking
5. Check "My Bookings"

---

##  Usage Guide

### Quick Start

1. **Register**: Create account at `/register.html`
2. **Login**: Login at `/login.html`
3. **Search**: Enter flight details on homepage
4. **Book**: Select flight and fill passenger info
5. **Pay**: Choose payment method and confirm
6. **Download**: Get PDF/JSON receipt

### Dynamic Pricing Factors

The system adjusts prices based on:
- Seat availability (higher demand = higher price)
- Time to departure (last-minute bookings cost more)
- Seasonal factors (holidays, peak seasons)
- Weekend premiums
- Route popularity
- Airline tier
- Peak hour pricing
- Historical demand patterns

---

##  Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

##  License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

##  Author

**Prakhar Srivastava**

- GitHub: [@PrakharSrivastava007](https://github.com/PrakharSrivastava007)
- LinkedIn: [Prakhar Srivastava](https://www.linkedin.com/in/prakhar-srivastava-0980b1248/)
- Email: 2k22.cscys.2212211@gmail.com

---

##  Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for powerful ORM capabilities
- Font Awesome for icons
- MakeMyTrip for UI/UX inspiration
- Open source community for invaluable resources

---

##  Project Stats

- **Lines of Code**: 15,000+
- **API Endpoints**: 30+
- **Database Tables**: 10
- **Frontend Pages**: 8
- **Technologies**: 12+

---

##  Future Enhancements

- [ ] Email/SMS notifications
- [ ] Multi-currency support
- [ ] Social authentication
- [ ] Mobile application
- [ ] AI-powered recommendations
- [ ] Advanced analytics dashboard

---

<div align="center">

**⭐ Star this repository if you found it helpful!**

Made with ❤️ by Prakhar Srivastava

</div>