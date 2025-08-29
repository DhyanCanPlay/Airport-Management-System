"""
Sample Data Creation Script for Airport Management System
CBSE Class 12 Informatics Practices Project

This script creates sample data for testing and demonstration purposes.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airport_mgmt.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Flight, Passenger, Booking, Staff, CheckIn

def create_sample_flights():
    """Create sample flight data"""
    print("Creating sample flights...")
    
    airlines = ['Air India', 'IndiGo', 'SpiceJet', 'Vistara', 'GoAir']
    cities = {
        'Delhi': 'DEL',
        'Mumbai': 'BOM', 
        'Bangalore': 'BLR',
        'Chennai': 'MAA',
        'Kolkata': 'CCU',
        'Hyderabad': 'HYD',
        'Pune': 'PNQ',
        'Ahmedabad': 'AMD',
        'Kochi': 'COK',
        'Goa': 'GOI'
    }
    
    aircraft_types = ['Boeing 737', 'Airbus A320', 'Boeing 777', 'Airbus A330', 'ATR 72']
    
    city_list = list(cities.keys())
    base_date = datetime.now()
    
    flights_data = []
    
    for i in range(20):
        airline = random.choice(airlines)
        departure_city = random.choice(city_list)
        arrival_city = random.choice([c for c in city_list if c != departure_city])
        
        # Generate flight number
        flight_number = f"{airline[:2].upper()}{random.randint(100, 999)}"
        
        # Generate times
        departure_time = base_date + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(6, 22),
            minutes=random.choice([0, 30])
        )
        arrival_time = departure_time + timedelta(hours=random.randint(1, 4))
        
        total_seats = random.choice([150, 180, 200, 250, 300])
        available_seats = random.randint(0, total_seats // 2)
        
        price = Decimal(random.randint(3000, 15000))
        
        status = random.choice(['scheduled', 'scheduled', 'scheduled', 'boarding', 'departed'])
        
        flight_data = {
            'flight_number': flight_number,
            'airline': airline,
            'departure_city': departure_city,
            'arrival_city': arrival_city,
            'departure_time': departure_time,
            'arrival_time': arrival_time,
            'aircraft_type': random.choice(aircraft_types),
            'total_seats': total_seats,
            'available_seats': available_seats,
            'price': price,
            'status': status,
            'gate_number': f"G{random.randint(1, 20)}" if random.choice([True, False]) else None
        }
        
        flights_data.append(flight_data)
    
    # Create flights
    for flight_data in flights_data:
        flight, created = Flight.objects.get_or_create(
            flight_number=flight_data['flight_number'],
            defaults=flight_data
        )
        if created:
            print(f"Created flight: {flight.flight_number}")

def create_sample_passengers():
    """Create sample passenger data"""
    print("Creating sample passengers...")
    
    first_names = [
        'Rahul', 'Priya', 'Amit', 'Sunita', 'Vikram', 'Anita', 'Rajesh', 'Meera',
        'Suresh', 'Kavita', 'Arjun', 'Pooja', 'Manoj', 'Deepa', 'Ravi', 'Shalini'
    ]
    
    last_names = [
        'Sharma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Agarwal', 'Verma', 'Jain',
        'Shah', 'Rao', 'Reddy', 'Nair', 'Iyer', 'Chopra', 'Malhotra', 'Sinha'
    ]
    
    nationalities = ['Indian', 'American', 'British', 'Canadian', 'Australian', 'German']
    
    for i in range(25):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Generate email
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@email.com"
        
        # Generate phone
        phone_number = f"+91{random.randint(7000000000, 9999999999)}"
        
        # Generate birth date (age between 18-80)
        birth_date = datetime.now().date() - timedelta(days=random.randint(18*365, 80*365))
        
        gender = random.choice(['M', 'F'])
        
        # Generate passport number
        passport_number = f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))}{random.randint(1000000, 9999999)}"
        
        nationality = random.choice(nationalities)
        
        address = f"{random.randint(1, 999)} {random.choice(['Main', 'Park', 'Oak', 'Pine'])} Street, {random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai'])}"
        
        passenger_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone_number': phone_number,
            'date_of_birth': birth_date,
            'gender': gender,
            'passport_number': passport_number,
            'nationality': nationality,
            'address': address
        }
        
        try:
            passenger, created = Passenger.objects.get_or_create(
                email=email,
                defaults=passenger_data
            )
            if created:
                print(f"Created passenger: {passenger.full_name}")
        except Exception as e:
            print(f"Error creating passenger: {e}")

def create_sample_users_and_staff():
    """Create sample users and staff"""
    print("Creating sample users and staff...")
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'first_name': 'Admin',
            'last_name': 'User',
            'email': 'admin@airport.com',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin')
        admin_user.save()
        print("Created admin user")
    
    # Create staff users
    staff_data = [
        {'username': 'pilot1', 'first_name': 'Captain', 'last_name': 'Singh', 'role': 'pilot'},
        {'username': 'crew1', 'first_name': 'Air', 'last_name': 'Hostess', 'role': 'crew'},
        {'username': 'ground1', 'first_name': 'Ground', 'last_name': 'Staff', 'role': 'ground'},
        {'username': 'security1', 'first_name': 'Security', 'last_name': 'Officer', 'role': 'security'},
    ]
    
    for staff_info in staff_data:
        user, created = User.objects.get_or_create(
            username=staff_info['username'],
            defaults={
                'first_name': staff_info['first_name'],
                'last_name': staff_info['last_name'],
                'email': f"{staff_info['username']}@airport.com",
                'is_staff': True,
            }
        )
        if created:
            user.set_password('staff123')
            user.save()
            
            # Create staff record
            staff, created = Staff.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': f"EMP{random.randint(1000, 9999)}",
                    'role': staff_info['role'],
                    'department': random.choice(['Operations', 'Safety', 'Customer Service']),
                    'hire_date': datetime.now().date() - timedelta(days=random.randint(30, 1000)),
                    'salary': Decimal(random.randint(30000, 80000)),
                    'phone_number': f"+91{random.randint(7000000000, 9999999999)}",
                    'address': f"{random.randint(1, 999)} Staff Colony, Airport Road",
                    'is_active': True
                }
            )
            if created:
                print(f"Created staff: {staff.user.get_full_name()}")

def create_sample_bookings():
    """Create sample bookings"""
    print("Creating sample bookings...")
    
    passengers = list(Passenger.objects.all())
    flights = list(Flight.objects.all())
    
    if not passengers or not flights:
        print("No passengers or flights available for bookings")
        return
    
    for i in range(30):
        passenger = random.choice(passengers)
        flight = random.choice(flights)
        
        # Check if booking already exists
        if Booking.objects.filter(passenger=passenger, flight=flight).exists():
            continue
        
        seat_number = f"{random.randint(1, 30)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}"
        
        booking_data = {
            'passenger': passenger,
            'flight': flight,
            'seat_number': seat_number,
            'status': random.choice(['confirmed', 'confirmed', 'confirmed', 'pending']),
            'total_amount': flight.price,
            'payment_status': random.choice([True, False]),
            'special_requests': random.choice([None, 'Vegetarian meal', 'Window seat', 'Aisle seat'])
        }
        
        try:
            booking = Booking.objects.create(**booking_data)
            print(f"Created booking: {booking.booking_reference}")
        except Exception as e:
            print(f"Error creating booking: {e}")

def create_sample_checkins():
    """Create sample check-ins"""
    print("Creating sample check-ins...")
    
    confirmed_bookings = Booking.objects.filter(status='confirmed')
    staff_members = list(Staff.objects.all())
    
    # Create check-ins for some bookings
    for booking in confirmed_bookings[:15]:  # Check-in first 15 bookings
        if CheckIn.objects.filter(booking=booking).exists():
            continue
        
        checkin_data = {
            'booking': booking,
            'gate_number': f"G{random.randint(1, 20)}",
            'seat_number': booking.seat_number,
            'baggage_weight': Decimal(random.uniform(15.0, 25.0)),
            'status': random.choice(['checked_in', 'boarding_pass_issued']),
            'staff': random.choice(staff_members) if staff_members else None,
            'notes': random.choice([None, 'Extra baggage', 'Priority boarding', 'Medical assistance'])
        }
        
        try:
            checkin = CheckIn.objects.create(**checkin_data)
            print(f"Created check-in for booking: {checkin.booking.booking_reference}")
        except Exception as e:
            print(f"Error creating check-in: {e}")

def main():
    """Main function to create all sample data"""
    print("Creating sample data for Airport Management System")
    print("=" * 50)
    
    try:
        create_sample_flights()
        create_sample_passengers()
        create_sample_users_and_staff()
        create_sample_bookings()
        create_sample_checkins()
        
        print("\n" + "=" * 50)
        print("Sample data creation completed!")
        print(f"Flights: {Flight.objects.count()}")
        print(f"Passengers: {Passenger.objects.count()}")
        print(f"Users: {User.objects.count()}")
        print(f"Staff: {Staff.objects.count()}")
        print(f"Bookings: {Booking.objects.count()}")
        print(f"Check-ins: {CheckIn.objects.count()}")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")

if __name__ == "__main__":
    main()
