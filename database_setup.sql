-- Airport Management System Database Setup
-- CBSE Class 12 Informatics Practices Project
-- MySQL Database Schema and Sample Data

-- Create Database (Run this first if database doesn't exist)
CREATE DATABASE IF NOT EXISTS airport_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE airport_management;

-- Flight Table
CREATE TABLE IF NOT EXISTS core_flight (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flight_number VARCHAR(10) UNIQUE NOT NULL,
    airline VARCHAR(100) NOT NULL,
    departure_city VARCHAR(100) NOT NULL,
    arrival_city VARCHAR(100) NOT NULL,
    departure_time DATETIME NOT NULL,
    arrival_time DATETIME NOT NULL,
    aircraft_type VARCHAR(50) NOT NULL,
    total_seats INT UNSIGNED NOT NULL,
    available_seats INT UNSIGNED NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled',
    gate_number VARCHAR(10),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Passenger Table
CREATE TABLE IF NOT EXISTS core_passenger (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    phone_number VARCHAR(17) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(1) NOT NULL,
    passport_number VARCHAR(20) UNIQUE NOT NULL,
    nationality VARCHAR(50) NOT NULL,
    address TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- User Table (Django's built-in user model structure)
CREATE TABLE IF NOT EXISTS auth_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME(6),
    is_superuser TINYINT(1) NOT NULL,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff TINYINT(1) NOT NULL,
    is_active TINYINT(1) NOT NULL,
    date_joined DATETIME(6) NOT NULL
);

-- Staff Table
CREATE TABLE IF NOT EXISTS core_staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL,
    department VARCHAR(100) NOT NULL,
    hire_date DATE NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    phone_number VARCHAR(17) NOT NULL,
    address TEXT NOT NULL,
    is_active TINYINT(1) DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- Booking Table
CREATE TABLE IF NOT EXISTS core_booking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_reference VARCHAR(10) UNIQUE NOT NULL,
    passenger_id INT NOT NULL,
    flight_id INT NOT NULL,
    seat_number VARCHAR(10) NOT NULL,
    booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'confirmed',
    total_amount DECIMAL(10,2) NOT NULL,
    payment_status TINYINT(1) DEFAULT 0,
    special_requests TEXT,
    FOREIGN KEY (passenger_id) REFERENCES core_passenger(id) ON DELETE CASCADE,
    FOREIGN KEY (flight_id) REFERENCES core_flight(id) ON DELETE CASCADE,
    UNIQUE KEY unique_flight_seat (flight_id, seat_number)
);

-- Check-in Table
CREATE TABLE IF NOT EXISTS core_checkin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT UNIQUE NOT NULL,
    check_in_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    boarding_time DATETIME,
    gate_number VARCHAR(10) NOT NULL,
    seat_number VARCHAR(10) NOT NULL,
    baggage_weight DECIMAL(5,2) DEFAULT 0.00,
    status VARCHAR(30) DEFAULT 'checked_in',
    staff_id INT,
    notes TEXT,
    FOREIGN KEY (booking_id) REFERENCES core_booking(id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES core_staff(id) ON DELETE SET NULL
);

-- Insert Sample Data

-- Sample Flights
INSERT INTO core_flight (flight_number, airline, departure_city, arrival_city, departure_time, arrival_time, aircraft_type, total_seats, available_seats, price, status, gate_number) VALUES
('AI101', 'Air India', 'Delhi', 'Mumbai', '2024-03-15 08:00:00', '2024-03-15 10:30:00', 'Boeing 737', 180, 45, 8500.00, 'scheduled', 'G5'),
('6E202', 'IndiGo', 'Mumbai', 'Bangalore', '2024-03-15 14:15:00', '2024-03-15 16:45:00', 'Airbus A320', 200, 67, 6500.00, 'scheduled', 'G12'),
('SG303', 'SpiceJet', 'Delhi', 'Chennai', '2024-03-16 06:30:00', '2024-03-16 09:15:00', 'Boeing 737', 150, 23, 7200.00, 'scheduled', 'G8'),
('UK404', 'Vistara', 'Bangalore', 'Kolkata', '2024-03-16 11:20:00', '2024-03-16 14:10:00', 'Airbus A320', 180, 89, 9100.00, 'scheduled', 'G15'),
('G8505', 'GoAir', 'Chennai', 'Hyderabad', '2024-03-17 16:45:00', '2024-03-17 18:30:00', 'Airbus A320', 180, 112, 5800.00, 'scheduled', 'G3'),
('AI606', 'Air India', 'Mumbai', 'Goa', '2024-03-17 09:30:00', '2024-03-17 11:00:00', 'ATR 72', 80, 15, 4500.00, 'boarding', 'G20'),
('6E707', 'IndiGo', 'Delhi', 'Pune', '2024-03-18 13:40:00', '2024-03-18 15:50:00', 'Airbus A320', 200, 78, 6800.00, 'scheduled', 'G7'),
('SG808', 'SpiceJet', 'Kolkata', 'Mumbai', '2024-03-18 18:15:00', '2024-03-18 21:30:00', 'Boeing 737', 150, 34, 8200.00, 'scheduled', 'G11'),
('UK909', 'Vistara', 'Hyderabad', 'Delhi', '2024-03-19 07:45:00', '2024-03-19 10:15:00', 'Boeing 777', 300, 156, 11500.00, 'scheduled', 'G2'),
('G8010', 'GoAir', 'Goa', 'Bangalore', '2024-03-19 12:20:00', '2024-03-19 14:00:00', 'Airbus A320', 180, 67, 5200.00, 'scheduled', 'G18');

-- Sample Passengers
INSERT INTO core_passenger (first_name, last_name, email, phone_number, date_of_birth, gender, passport_number, nationality, address) VALUES
('Rahul', 'Sharma', 'rahul.sharma@email.com', '+919876543210', '1990-05-15', 'M', 'AB1234567', 'Indian', '123 MG Road, Mumbai'),
('Priya', 'Patel', 'priya.patel@email.com', '+919876543211', '1985-08-22', 'F', 'CD2345678', 'Indian', '456 Park Street, Delhi'),
('Amit', 'Singh', 'amit.singh@email.com', '+919876543212', '1992-12-10', 'M', 'EF3456789', 'Indian', '789 Brigade Road, Bangalore'),
('Sunita', 'Gupta', 'sunita.gupta@email.com', '+919876543213', '1988-03-18', 'F', 'GH4567890', 'Indian', '321 Anna Salai, Chennai'),
('Vikram', 'Agarwal', 'vikram.agarwal@email.com', '+919876543214', '1995-11-05', 'M', 'IJ5678901', 'Indian', '654 Sector 17, Chandigarh'),
('Anita', 'Verma', 'anita.verma@email.com', '+919876543215', '1987-07-28', 'F', 'KL6789012', 'Indian', '987 Linking Road, Mumbai'),
('Rajesh', 'Jain', 'rajesh.jain@email.com', '+919876543216', '1993-01-12', 'M', 'MN7890123', 'Indian', '147 CP Tank, Mumbai'),
('Meera', 'Shah', 'meera.shah@email.com', '+919876543217', '1991-09-30', 'F', 'OP8901234', 'Indian', '258 Koramangala, Bangalore'),
('Suresh', 'Rao', 'suresh.rao@email.com', '+919876543218', '1986-04-25', 'M', 'QR9012345', 'Indian', '369 Jubilee Hills, Hyderabad'),
('Kavita', 'Reddy', 'kavita.reddy@email.com', '+919876543219', '1994-06-14', 'F', 'ST0123456', 'Indian', '741 T Nagar, Chennai'),
('John', 'Smith', 'john.smith@email.com', '+14155552345', '1980-03-20', 'M', 'US1234567', 'American', '123 Main St, San Francisco'),
('Emily', 'Johnson', 'emily.johnson@email.com', '+14155552346', '1982-11-15', 'F', 'US2345678', 'American', '456 Oak Ave, Los Angeles'),
('David', 'Brown', 'david.brown@email.com', '+442071234567', '1975-08-08', 'M', 'GB3456789', 'British', '789 King St, London'),
('Sarah', 'Wilson', 'sarah.wilson@email.com', '+442071234568', '1989-12-03', 'F', 'GB4567890', 'British', '321 Queen St, Manchester'),
('Michael', 'Davis', 'michael.davis@email.com', '+16135551234', '1983-05-27', 'M', 'CA5678901', 'Canadian', '654 Maple Ave, Toronto');

-- Sample Users (Admin and Staff)
INSERT INTO auth_user (password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES
('pbkdf2_sha256$260000$xyzabc123$hashedpassword', 1, 'admin', 'Admin', 'User', 'admin@airport.com', 1, 1, '2024-01-01 00:00:00'),
('pbkdf2_sha256$260000$xyzabc123$hashedpassword', 0, 'pilot1', 'Captain', 'Singh', 'pilot1@airport.com', 1, 1, '2024-01-15 00:00:00'),
('pbkdf2_sha256$260000$xyzabc123$hashedpassword', 0, 'crew1', 'Air', 'Hostess', 'crew1@airport.com', 1, 1, '2024-01-20 00:00:00'),
('pbkdf2_sha256$260000$xyzabc123$hashedpassword', 0, 'ground1', 'Ground', 'Staff', 'ground1@airport.com', 1, 1, '2024-01-25 00:00:00');

-- Sample Staff
INSERT INTO core_staff (user_id, employee_id, role, department, hire_date, salary, phone_number, address, is_active) VALUES
(2, 'EMP1001', 'pilot', 'Operations', '2023-06-15', 75000.00, '+919876501001', '101 Pilot Colony, Airport Road', 1),
(3, 'EMP1002', 'crew', 'Customer Service', '2023-08-20', 45000.00, '+919876501002', '102 Staff Quarter, Airport Road', 1),
(4, 'EMP1003', 'ground', 'Operations', '2023-10-10', 35000.00, '+919876501003', '103 Ground Staff Housing, Airport Road', 1);

-- Sample Bookings
INSERT INTO core_booking (booking_reference, passenger_id, flight_id, seat_number, status, total_amount, payment_status, special_requests) VALUES
('BOOK0001', 1, 1, '12A', 'confirmed', 8500.00, 1, 'Window seat'),
('BOOK0002', 2, 2, '15B', 'confirmed', 6500.00, 1, 'Vegetarian meal'),
('BOOK0003', 3, 3, '8C', 'confirmed', 7200.00, 1, NULL),
('BOOK0004', 4, 4, '22A', 'confirmed', 9100.00, 1, 'Aisle seat'),
('BOOK0005', 5, 5, '5F', 'confirmed', 5800.00, 1, NULL),
('BOOK0006', 6, 6, '3A', 'confirmed', 4500.00, 1, 'Extra legroom'),
('BOOK0007', 7, 7, '18D', 'confirmed', 6800.00, 1, NULL),
('BOOK0008', 8, 8, '11B', 'confirmed', 8200.00, 1, 'Special meal'),
('BOOK0009', 9, 9, '25A', 'confirmed', 11500.00, 1, 'Priority boarding'),
('BOOK0010', 10, 10, '14C', 'confirmed', 5200.00, 1, NULL),
('BOOK0011', 11, 1, '13B', 'pending', 8500.00, 0, NULL),
('BOOK0012', 12, 2, '16A', 'confirmed', 6500.00, 1, 'Wheelchair assistance'),
('BOOK0013', 13, 3, '9D', 'confirmed', 7200.00, 1, NULL),
('BOOK0014', 14, 4, '23B', 'confirmed', 9100.00, 1, NULL),
('BOOK0015', 15, 5, '6E', 'confirmed', 5800.00, 1, 'Child meal');

-- Sample Check-ins
INSERT INTO core_checkin (booking_id, gate_number, seat_number, baggage_weight, status, staff_id, notes) VALUES
(1, 'G5', '12A', 18.50, 'boarding_pass_issued', 2, 'Window seat confirmed'),
(2, 'G12', '15B', 20.00, 'checked_in', 3, 'Special meal arranged'),
(3, 'G8', '8C', 15.75, 'checked_in', 2, NULL),
(4, 'G15', '22A', 22.30, 'boarding_pass_issued', 3, 'Aisle seat confirmed'),
(5, 'G3', '5F', 19.20, 'checked_in', 2, NULL),
(6, 'G20', '3A', 16.80, 'gate_assigned', 3, 'Extra legroom seat'),
(7, 'G7', '18D', 21.50, 'checked_in', 2, NULL),
(8, 'G11', '11B', 17.90, 'boarding_pass_issued', 3, 'Special dietary requirements'),
(9, 'G2', '25A', 23.10, 'checked_in', 2, 'Priority boarding confirmed'),
(10, 'G18', '14C', 18.00, 'checked_in', 3, NULL);

-- Create Indexes for Better Performance
CREATE INDEX idx_flight_departure_time ON core_flight(departure_time);
CREATE INDEX idx_flight_status ON core_flight(status);
CREATE INDEX idx_passenger_email ON core_passenger(email);
CREATE INDEX idx_booking_status ON core_booking(status);
CREATE INDEX idx_booking_date ON core_booking(booking_date);

-- Create Views for Reporting
CREATE VIEW flight_booking_summary AS
SELECT 
    f.flight_number,
    f.airline,
    f.departure_city,
    f.arrival_city,
    f.departure_time,
    f.total_seats,
    f.available_seats,
    (f.total_seats - f.available_seats) as booked_seats,
    COUNT(b.id) as total_bookings,
    SUM(b.total_amount) as total_revenue
FROM core_flight f
LEFT JOIN core_booking b ON f.id = b.flight_id
GROUP BY f.id;

CREATE VIEW passenger_booking_details AS
SELECT 
    p.first_name,
    p.last_name,
    p.email,
    b.booking_reference,
    f.flight_number,
    f.departure_city,
    f.arrival_city,
    f.departure_time,
    b.seat_number,
    b.status as booking_status,
    b.total_amount
FROM core_passenger p
JOIN core_booking b ON p.id = b.passenger_id
JOIN core_flight f ON b.flight_id = f.id;

-- Stored Procedure for Flight Search
DELIMITER //
CREATE PROCEDURE SearchFlights(
    IN dep_city VARCHAR(100),
    IN arr_city VARCHAR(100),
    IN dep_date DATE
)
BEGIN
    SELECT 
        flight_number,
        airline,
        departure_city,
        arrival_city,
        departure_time,
        arrival_time,
        available_seats,
        price,
        status
    FROM core_flight
    WHERE 
        (dep_city IS NULL OR departure_city LIKE CONCAT('%', dep_city, '%'))
        AND (arr_city IS NULL OR arrival_city LIKE CONCAT('%', arr_city, '%'))
        AND (dep_date IS NULL OR DATE(departure_time) = dep_date)
        AND status = 'scheduled'
        AND available_seats > 0
    ORDER BY departure_time;
END //
DELIMITER ;

-- Show table information
SELECT 'Database setup completed successfully!' as Status;
SELECT TABLE_NAME, TABLE_ROWS 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'airport_management' 
AND TABLE_TYPE = 'BASE TABLE';
