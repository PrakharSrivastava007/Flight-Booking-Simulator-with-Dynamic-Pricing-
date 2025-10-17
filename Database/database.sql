CREATE DATABASE IF NOT EXISTS Flight_Booking;
USE Flight_Booking;

-- Users Table
CREATE TABLE Users (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    Email VARCHAR(100) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    First_name VARCHAR(100) NOT NULL,
    Last_name VARCHAR(55) NOT NULL,
    Phone VARCHAR(15),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    Index idx_email (Email)
);

-- Airlines Table
CREATE TABLE Airlines (
    AirlineID INT PRIMARY KEY AUTO_INCREMENT,
    Airline_Name VARCHAR(100) NOT NULL UNIQUE,
    Airline_Code VARCHAR(3) UNIQUE NOT NULL,
    Country VARCHAR(100),
    contact_email VARCHAR(100),
    contact_phone VARCHAR(15),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Data for Airlines
INSERT INTO Airlines (Airline_Name, Airline_Code, Country, contact_email, contact_phone) VALUES
('Air India', 'AI', 'India', 'support@airindia.in', '+91-1244629000'),
('IndiGo', '6E', 'India', 'customer.relations@goindigo.in', '+91-1246173838'),
('SpiceJet', 'SG', 'India', 'customer.relations@spicejet.com', '+91-9871803333'),
('Vistara', 'UK', 'India', 'customer.relations@airvistara.com', '+91-9289228888'),
('Air Asia India', 'I5', 'India', 'support@airasia.co.in', '+91-8045115555'),
('GoFirst', 'G8', 'India', 'info@flygofirst.com', '+91-2225027000');



-- Airports Table
CREATE TABLE Airports (
    AirportID INT PRIMARY KEY AUTO_INCREMENT,
    Airport_Name VARCHAR(100) NOT NULL,
    Airport_Code VARCHAR(3) UNIQUE NOT NULL,
    City VARCHAR(100) NOT NULL,
    Country VARCHAR(100) NOT NULL,
    Timezone VARCHAR(50),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Index idx_city (City),
    Index idx_country(Country)
);

-- Data for Airports
INSERT INTO Airports (Airport_Name, Airport_Code, City, Country, Timezone) VALUES
('Indira Gandhi International Airport', 'DEL', 'New Delhi', 'India', 'Asia/Kolkata'),
('Chhatrapati Shivaji Maharaj International Airport', 'BOM', 'Mumbai', 'India', 'Asia/Kolkata'),
('Kempegowda International Airport', 'BLR', 'Bangalore', 'India', 'Asia/Kolkata'),
('Chennai International Airport', 'MAA', 'Chennai', 'India', 'Asia/Kolkata'),
('Netaji Subhas Chandra Bose International Airport', 'CCU', 'Kolkata', 'India', 'Asia/Kolkata'),
('Rajiv Gandhi International Airport', 'HYD', 'Hyderabad', 'India', 'Asia/Kolkata'),
('Pune Airport', 'PNQ', 'Pune', 'India', 'Asia/Kolkata'),
('Sardar Vallabhbhai Patel International Airport', 'AMD', 'Ahmedabad', 'India', 'Asia/Kolkata'),
('Goa International Airport', 'GOI', 'Goa', 'India', 'Asia/Kolkata'),
('Cochin International Airport', 'COK', 'Kochi', 'India', 'Asia/Kolkata'),
('Jaipur International Airport', 'JAI', 'Jaipur', 'India', 'Asia/Kolkata'),
('Chaudhary Charan Singh International Airport', 'LKO', 'Lucknow', 'India', 'Asia/Kolkata'),
('Sheikh ul-Alam International Airport', 'SXR', 'Srinagar', 'India', 'Asia/Kolkata'),
('Kushok Bakula Rimpochee Airport', 'IXL', 'Leh', 'India', 'Asia/Kolkata'),
('Lokpriya Gopinath Bordoloi International Airport', 'GAU', 'Guwahati', 'India', 'Asia/Kolkata'),
('Trivandrum International Airport', 'TRV', 'Thiruvananthapuram', 'India', 'Asia/Kolkata'),
('Chandigarh International Airport', 'IXC', 'Chandigarh', 'India', 'Asia/Kolkata'),
('Dr. Babasaheb Ambedkar International Airport', 'NAG', 'Nagpur', 'India', 'Asia/Kolkata'),
('Jay Prakash Narayan International Airport', 'PAT', 'Patna', 'India', 'Asia/Kolkata'),
('Biju Patnaik International Airport', 'BBI', 'Bhubaneswar', 'India', 'Asia/Kolkata');


-- Flights Table
CREATE TABLE Flights (
    FlightID INT PRIMARY KEY AUTO_INCREMENT,
    AirlineID INT NOT NULL,
    Flight_Number VARCHAR(10) NOT NULL UNIQUE,
    Departure_AirportID INT NOT NULL,
    Arrival_AirportID INT NOT NULL,
    Departure_Time DATETIME NOT NULL,
    Arrival_Time DATETIME NOT NULL,
    Duration INT, -- Duration in minutes
    Price DECIMAL(10, 2) NOT NULL,
    Seats_Available INT DEFAULT 0,
    Flight_status ENUM('scheduled','delayed','cancelled','departed','arrived') DEFAULT 'scheduled',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (AirlineID) REFERENCES Airlines(AirlineID) ON DELETE CASCADE,
    FOREIGN KEY (Departure_AirportID) REFERENCES Airports(AirportID) ON DELETE RESTRICT,
    FOREIGN KEY (Arrival_AirportID) REFERENCES Airports(AirportID) ON DELETE RESTRICT,
    Index idx_flight_number (Flight_Number),
    Index idx_departure_time (Departure_Time),
    Index idx_arrival_time (Arrival_Time),
    Index idx_route (Departure_AirportID, Arrival_AirportID)
);

-- Data for Flights
INSERT INTO Flights (AirlineID, Flight_Number, Departure_AirportID, Arrival_AirportID, 
                     Departure_Time, Arrival_Time, Duration, Price, Seats_Available, Flight_status) 
VALUES
(1, 'AI101', 1, 2, '2025-10-20 06:00:00', '2025-10-20 08:15:00', 135, 5500.00, 180, 'scheduled'),
(2, '6E201', 1, 2, '2025-10-20 08:30:00', '2025-10-20 10:45:00', 135, 4800.00, 186, 'scheduled'),
(3, 'SG301', 1, 2, '2025-10-20 11:00:00', '2025-10-20 13:15:00', 135, 4500.00, 189, 'scheduled'),
(4, 'UK401', 1, 2, '2025-10-20 14:30:00', '2025-10-20 16:45:00', 135, 5200.00, 150, 'scheduled'),
(2, '6E203', 1, 2, '2025-10-20 18:00:00', '2025-10-20 20:15:00', 135, 5000.00, 186, 'scheduled'),
(1, 'AI102', 2, 1, '2025-10-20 07:00:00', '2025-10-20 09:15:00', 135, 5600.00, 180, 'scheduled'),
(2, '6E202', 2, 1, '2025-10-20 10:00:00', '2025-10-20 12:15:00', 135, 4900.00, 186, 'scheduled'),
(3, 'SG302', 2, 1, '2025-10-20 15:30:00', '2025-10-20 17:45:00', 135, 4700.00, 189, 'scheduled'),
(5, 'I5501', 2, 1, '2025-10-20 20:00:00', '2025-10-20 22:15:00', 135, 4300.00, 180, 'scheduled'),
(1, 'AI201', 1, 3, '2025-10-20 06:30:00', '2025-10-20 09:15:00', 165, 6000.00, 180, 'scheduled'),
(2, '6E301', 1, 3, '2025-10-20 09:00:00', '2025-10-20 11:45:00', 165, 5500.00, 186, 'scheduled'),
(4, 'UK501', 1, 3, '2025-10-20 13:00:00', '2025-10-20 15:45:00', 165, 6200.00, 150, 'scheduled'),
(3, 'SG401', 1, 3, '2025-10-20 17:00:00', '2025-10-20 19:45:00', 165, 5300.00, 189, 'scheduled'),
(1, 'AI202', 3, 1, '2025-10-20 07:00:00', '2025-10-20 09:45:00', 165, 6100.00, 180, 'scheduled'),
(2, '6E302', 3, 1, '2025-10-20 16:00:00', '2025-10-20 18:45:00', 165, 5700.00, 186, 'scheduled'),
(6, 'G8601', 3, 1, '2025-10-20 21:00:00', '2025-10-20 23:45:00', 165, 5400.00, 180, 'scheduled'),
(2, '6E401', 2, 3, '2025-10-20 08:00:00', '2025-10-20 09:45:00', 105, 4500.00, 186, 'scheduled'),
(3, 'SG403', 2, 3, '2025-10-20 12:00:00', '2025-10-20 13:45:00', 105, 4200.00, 189, 'scheduled'),
(5, 'I5601', 2, 3, '2025-10-20 19:00:00', '2025-10-20 20:45:00', 105, 4000.00, 180, 'scheduled'),
(1, 'AI301', 3, 2, '2025-10-20 10:00:00', '2025-10-20 11:45:00', 105, 4600.00, 180, 'scheduled'),
(2, '6E402', 3, 2, '2025-10-20 14:30:00', '2025-10-20 16:15:00', 105, 4300.00, 186, 'scheduled'),
(1, 'AI401', 1, 4, '2025-10-20 08:00:00', '2025-10-20 11:00:00', 180, 6500.00, 180, 'scheduled'),
(2, '6E501', 1, 4, '2025-10-20 15:00:00', '2025-10-20 18:00:00', 180, 6000.00, 186, 'scheduled'),
(1, 'AI601', 1, 5, '2025-10-20 09:00:00', '2025-10-20 11:30:00', 150, 5800.00, 180, 'scheduled'),
(2, '6E601', 1, 5, '2025-10-20 17:00:00', '2025-10-20 19:30:00', 150, 5400.00, 186, 'scheduled'),
(2, '6E701', 2, 9, '2025-10-20 10:30:00', '2025-10-20 11:45:00', 75, 3800.00, 180, 'scheduled'),
(3, 'SG701', 2, 9, '2025-10-20 14:00:00', '2025-10-20 15:15:00', 75, 3500.00, 189, 'scheduled'),
(3, 'SG801', 1, 11, '2025-10-20 09:00:00', '2025-10-20 10:30:00', 90, 4500.00, 189, 'scheduled'),
(6, 'G8801', 1, 11, '2025-10-20 16:30:00', '2025-10-20 18:00:00', 90, 4200.00, 180, 'scheduled'),
(1, 'AI701', 1, 6, '2025-10-20 11:00:00', '2025-10-20 13:30:00', 150, 5900.00, 180, 'scheduled'),
(2, '6E801', 1, 6, '2025-10-20 19:00:00', '2025-10-20 21:30:00', 150, 5500.00, 186, 'scheduled'),
(3, 'SG901', 2, 6, '2025-10-20 13:00:00', '2025-10-20 14:30:00', 90, 4100.00, 189, 'scheduled'),
(5, 'I5801', 2, 6, '2025-10-20 18:30:00', '2025-10-20 20:00:00', 90, 3900.00, 180, 'scheduled');


CREATE TABLE Seat_Inventory (
    Inventory_ID INT PRIMARY KEY AUTO_INCREMENT,
    FlightID INT NOT NULL,
    Class ENUM('economy','business','first') DEFAULT 'economy',
    Total_Seats INT NOT NULL,
    Available_seats INT NOT NULL,
    Price DECIMAL(4, 2) DEFAULT 1.00,
    Last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (FlightID) REFERENCES Flights(FlightID) ON DELETE CASCADE,
    UNIQUE KEY Unique_flight_class (FlightID, Class),
    Index idx_availability (FlightID, Available_seats)
);

-- Data for Seat_Inventory
INSERT INTO Seat_Inventory (FlightID, Class, Total_Seats, Available_seats, Price) VALUES
(1, 'economy', 150, 150, 1.00),
(1, 'business', 30, 30, 2.50),
(2, 'economy', 162, 162, 1.00),
(2, 'business', 24, 24, 2.30),
(3, 'economy', 189, 189, 1.00),
(4, 'economy', 120, 120, 1.00),
(4, 'business', 30, 30, 2.80),
(5, 'economy', 162, 162, 1.00),
(5, 'business', 24, 24, 2.30),
(6, 'economy', 150, 150, 1.00),
(6, 'business', 30, 30, 2.50),
(7, 'economy', 162, 162, 1.00),
(7, 'business', 24, 24, 2.30),
(8, 'economy', 189, 189, 1.00),
(9, 'economy', 180, 180, 1.00),
(10, 'economy', 150, 150, 1.00),
(10, 'business', 30, 30, 2.50),
(11, 'economy', 162, 162, 1.00),
(11, 'business', 24, 24, 2.30),
(12, 'economy', 120, 120, 1.00),
(12, 'business', 30, 30, 2.80),
(13, 'economy', 189, 189, 1.00),
(14, 'economy', 150, 150, 1.00),
(14, 'business', 30, 30, 2.50),
(15, 'economy', 162, 162, 1.00),
(15, 'business', 24, 24, 2.30),
(16, 'economy', 180, 180, 1.00),
(17, 'economy', 162, 162, 1.00),
(17, 'business', 24, 24, 2.30),
(18, 'economy', 189, 189, 1.00),
(19, 'economy', 180, 180, 1.00),
(20, 'economy', 150, 150, 1.00),
(20, 'business', 30, 30, 2.50),
(21, 'economy', 162, 162, 1.00),
(21, 'business', 24, 24, 2.30),
(22, 'economy', 150, 150, 1.00),
(22, 'business', 30, 30, 2.50),
(23, 'economy', 162, 162, 1.00),
(23, 'business', 24, 24, 2.30),
(24, 'economy', 150, 150, 1.00),
(24, 'business', 30, 30, 2.50),
(25, 'economy', 162, 162, 1.00),
(25, 'business', 24, 24, 2.30),
(26, 'economy', 156, 156, 1.00),
(26, 'business', 24, 24, 2.20),
(27, 'economy', 189, 189, 1.00),
(28, 'economy', 189, 189, 1.00),
(29, 'economy', 180, 180, 1.00),
(30, 'economy', 150, 150, 1.00),
(30, 'business', 30, 30, 2.50),
(31, 'economy', 162, 162, 1.00),
(31, 'business', 24, 24, 2.30),
(32, 'economy', 189, 189, 1.00),
(33, 'economy', 180, 180, 1.00);


-- Bookings Table
CREATE TABLE Bookings (
    BookingID INT PRIMARY KEY AUTO_INCREMENT,
    pnr VARCHAR(6) NOT NULL UNIQUE,
    UserID INT NOT NULL,
    FlightID INT NOT NULL,
    Seat_class ENUM('economy','business','first') DEFAULT 'economy',
    Num_passengers INT NOT NULL,
    Total_price DECIMAL(10, 2) NOT NULL,
    Booking_status ENUM('pending','confirmed','cancelled') DEFAULT 'pending',
    Payment_status ENUM('unpaid','paid','refunded') DEFAULT 'unpaid',
    Booking_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Payment_date TIMESTAMP NULL,
    Expiry_time TIMESTAMP NULL,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
    FOREIGN KEY (FlightID) REFERENCES Flights(FlightID) ON DELETE RESTRICT,
    Index idx_pnr (pnr),
    Index idx_user (UserID),
    Index idx_status (Booking_status),
    Index idx_expiry (Expiry_time)
);

-- Passengers Table
CREATE TABLE Passengers (
    PassengerID INT PRIMARY KEY AUTO_INCREMENT,
    BookingID INT NOT NULL,
    First_name VARCHAR(100) NOT NULL,
    Last_name VARCHAR(55) NOT NULL,
    Date_of_birth DATE NOT NULL,
    Gender ENUM('male','female','other') NOT NULL,
    Passport_number VARCHAR(20),
    Nationality VARCHAR(50),
    Email VARCHAR(100),
    Phone VARCHAR(15),
    FOREIGN KEY (BookingID) REFERENCES Bookings(BookingID) ON DELETE CASCADE,
    Index idx_booking (BookingID)
);

-- Pricing Rules Table
CREATE TABLE Pricing_rules(
    RuleID INT PRIMARY KEY AUTO_INCREMENT,
    Rule_name VARCHAR(100) NOT NULL,
    Rule_type ENUM('time_based','demand_based','seasonal') NOT NULL,
    Multiplier_min DECIMAL(4,2) NOT NULL,
    Multiplier_max DECIMAL(4,2) NOT NULL,
    Is_active BOOLEAN DEFAULT TRUE,
    Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data for Pricing Rules
INSERT INTO Pricing_rules (Rule_name, Rule_type, Multiplier_min, Multiplier_max, Is_active) VALUES
('Early Bird Discount', 'time_based', 0.90, 1.00, TRUE),
('Standard Pricing', 'time_based', 1.00, 1.20, TRUE),
('Last Minute Premium', 'time_based', 1.30, 1.60, TRUE),
('Low Demand', 'demand_based', 0.95, 1.00, TRUE),
('Moderate Demand', 'demand_based', 1.10, 1.30, TRUE),
('High Demand', 'demand_based', 1.40, 1.80, TRUE),
('Very High Demand', 'demand_based', 1.80, 2.20, TRUE),
('Peak Season', 'seasonal', 1.30, 1.50, TRUE),
('Off Season', 'seasonal', 0.85, 1.00, TRUE),
('Weekend Premium', 'time_based', 1.15, 1.25, TRUE);


-- Price History Table
    CREATE TABLE Price_history(
        HistoryID INT PRIMARY KEY AUTO_INCREMENT,
        FlightID INT NOT NULL,
        Seat_class ENUM('economy','business','first') DEFAULT 'economy',
        Calculated_price DECIMAL(10,2) NOT NULL,
        Available_seats INT NOT NULL,
        Days_to_departure INT NOT NULL,
        Recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (FlightID) REFERENCES Flights(FlightID) ON DELETE CASCADE,
        Index idx_flight_class(FlightID,Seat_class),
        Index idx_recorded (Recorded_at)
    );

-- Payments Transactions Table
CREATE TABLE payment_transactions(
    TransactionID INT PRIMARY KEY AUTO_INCREMENT,
    BookingID INT NOT NULL,
    Payment_method ENUM('credit_card','debit_card','upi','netbanking','wallet') NOT NULL,
    Transaction_amount DECIMAL(10,2) NOT NULL,
    Transaction_status ENUM('pending','success','failed','refunded') NOT NULL,
    Payment_gateway_response TEXT,
    Transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (BookingID) REFERENCES Bookings(BookingID) ON DELETE CASCADE,
    Index idx_booking (BookingID),
    Index idx_status (Transaction_status)
);
show tables;