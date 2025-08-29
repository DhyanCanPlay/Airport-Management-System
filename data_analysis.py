"""
Airport Management System - Data Analysis & Visualization
CBSE Class 12 Informatics Practices Project

This script demonstrates the use of Pandas and Matplotlib for data analysis
and visualization as required for the CBSE IP practical.
"""

import os
import sys
import django
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airport_mgmt.settings')
django.setup()

from core.models import Flight, Passenger, Booking, Staff, CheckIn

def analyze_flight_data():
    """Analyze flight data using Pandas"""
    print("=== FLIGHT DATA ANALYSIS ===")
    
    # Get flight data
    flights = Flight.objects.all().values(
        'flight_number', 'airline', 'departure_city', 'arrival_city',
        'departure_time', 'arrival_time', 'total_seats', 'available_seats',
        'price', 'status'
    )
    
    if not flights:
        print("No flight data available")
        return None
        
    # Create DataFrame
    df_flights = pd.DataFrame(flights)
    
    print(f"Total Flights: {len(df_flights)}")
    print(f"Airlines: {df_flights['airline'].nunique()}")
    print(f"Routes: {df_flights['departure_city'].nunique()} -> {df_flights['arrival_city'].nunique()}")
    
    # Analysis by airline
    airline_stats = df_flights.groupby('airline').agg({
        'flight_number': 'count',
        'price': ['mean', 'min', 'max'],
        'total_seats': 'sum'
    }).round(2)
    
    print("\n--- Airline Statistics ---")
    print(airline_stats)
    
    # Most popular destinations
    destinations = df_flights['arrival_city'].value_counts().head(10)
    print("\n--- Top 10 Destinations ---")
    print(destinations)
    
    return df_flights

def analyze_passenger_data():
    """Analyze passenger demographics"""
    print("\n=== PASSENGER DATA ANALYSIS ===")
    
    # Get passenger data
    passengers = Passenger.objects.all().values(
        'first_name', 'last_name', 'date_of_birth', 'gender', 'nationality'
    )
    
    if not passengers:
        print("No passenger data available")
        return None
        
    df_passengers = pd.DataFrame(passengers)
    
    # Calculate ages
    today = pd.Timestamp.now()
    df_passengers['age'] = (today - pd.to_datetime(df_passengers['date_of_birth'])).dt.days // 365
    
    print(f"Total Passengers: {len(df_passengers)}")
    print(f"Age Statistics:")
    print(df_passengers['age'].describe())
    
    # Gender distribution
    gender_dist = df_passengers['gender'].value_counts()
    print(f"\n--- Gender Distribution ---")
    print(gender_dist)
    
    # Nationality distribution
    nationality_dist = df_passengers['nationality'].value_counts().head(10)
    print(f"\n--- Top 10 Nationalities ---")
    print(nationality_dist)
    
    return df_passengers

def analyze_booking_data():
    """Analyze booking patterns"""
    print("\n=== BOOKING DATA ANALYSIS ===")
    
    # Get booking data with related flight and passenger info
    bookings = Booking.objects.select_related('flight', 'passenger').all()
    
    if not bookings:
        print("No booking data available")
        return None
        
    booking_data = []
    for booking in bookings:
        booking_data.append({
            'booking_reference': booking.booking_reference,
            'booking_date': booking.booking_date,
            'status': booking.status,
            'total_amount': float(booking.total_amount),
            'flight_number': booking.flight.flight_number,
            'airline': booking.flight.airline,
            'departure_city': booking.flight.departure_city,
            'arrival_city': booking.flight.arrival_city,
            'passenger_age': booking.passenger.age
        })
    
    df_bookings = pd.DataFrame(booking_data)
    
    print(f"Total Bookings: {len(df_bookings)}")
    
    # Status distribution
    status_dist = df_bookings['status'].value_counts()
    print(f"\n--- Booking Status Distribution ---")
    print(status_dist)
    
    # Revenue analysis
    total_revenue = df_bookings['total_amount'].sum()
    avg_booking_value = df_bookings['total_amount'].mean()
    print(f"\n--- Revenue Analysis ---")
    print(f"Total Revenue: ₹{total_revenue:,.2f}")
    print(f"Average Booking Value: ₹{avg_booking_value:,.2f}")
    
    # Bookings by airline
    airline_bookings = df_bookings.groupby('airline').agg({
        'booking_reference': 'count',
        'total_amount': 'sum'
    }).sort_values('total_amount', ascending=False)
    print(f"\n--- Bookings by Airline ---")
    print(airline_bookings)
    
    return df_bookings

def create_visualizations():
    """Create charts using Matplotlib"""
    print("\n=== CREATING VISUALIZATIONS ===")
    
    # Set up matplotlib style
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Airport Management System - Data Analysis Dashboard', fontsize=16, fontweight='bold')
    
    # Chart 1: Flight Destinations
    flights = Flight.objects.all()
    if flights:
        destinations = {}
        for flight in flights:
            destinations[flight.arrival_city] = destinations.get(flight.arrival_city, 0) + 1
        
        cities = list(destinations.keys())[:8]  # Top 8 destinations
        counts = [destinations[city] for city in cities]
        
        axes[0, 0].bar(cities, counts, color='skyblue', edgecolor='navy', alpha=0.7)
        axes[0, 0].set_title('Top Flight Destinations', fontweight='bold')
        axes[0, 0].set_xlabel('Cities')
        axes[0, 0].set_ylabel('Number of Flights')
        axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Chart 2: Booking Status Distribution
    bookings = Booking.objects.all()
    if bookings:
        status_count = {}
        for booking in bookings:
            status_count[booking.status] = status_count.get(booking.status, 0) + 1
        
        labels = list(status_count.keys())
        sizes = list(status_count.values())
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        
        axes[0, 1].pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        axes[0, 1].set_title('Booking Status Distribution', fontweight='bold')
    
    # Chart 3: Passenger Age Distribution
    passengers = Passenger.objects.all()
    if passengers:
        ages = [passenger.age for passenger in passengers]
        
        axes[1, 0].hist(ages, bins=15, color='lightgreen', alpha=0.7, edgecolor='darkgreen')
        axes[1, 0].set_title('Passenger Age Distribution', fontweight='bold')
        axes[1, 0].set_xlabel('Age')
        axes[1, 0].set_ylabel('Number of Passengers')
        axes[1, 0].grid(True, alpha=0.3)
    
    # Chart 4: Revenue by Airline
    if bookings:
        airline_revenue = {}
        for booking in bookings:
            airline = booking.flight.airline
            airline_revenue[airline] = airline_revenue.get(airline, 0) + float(booking.total_amount)
        
        airlines = list(airline_revenue.keys())
        revenue = list(airline_revenue.values())
        
        axes[1, 1].barh(airlines, revenue, color='orange', alpha=0.7)
        axes[1, 1].set_title('Revenue by Airline', fontweight='bold')
        axes[1, 1].set_xlabel('Revenue (₹)')
        axes[1, 1].set_ylabel('Airlines')
    
    plt.tight_layout()
    plt.savefig('airport_analysis_dashboard.png', dpi=300, bbox_inches='tight')
    print("Dashboard saved as 'airport_analysis_dashboard.png'")
    
    # Individual charts for reports
    create_individual_charts()

def create_individual_charts():
    """Create individual charts for web reports"""
    
    # Flight destinations chart
    plt.figure(figsize=(10, 6))
    flights = Flight.objects.all()
    if flights:
        destinations = {}
        for flight in flights:
            destinations[flight.arrival_city] = destinations.get(flight.arrival_city, 0) + 1
        
        cities = list(destinations.keys())[:10]
        counts = [destinations[city] for city in cities]
        
        plt.bar(cities, counts, color='steelblue', alpha=0.8)
        plt.title('Top 10 Flight Destinations', fontsize=14, fontweight='bold')
        plt.xlabel('Cities')
        plt.ylabel('Number of Flights')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('destinations_chart.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    # Age distribution chart
    plt.figure(figsize=(10, 6))
    passengers = Passenger.objects.all()
    if passengers:
        ages = [passenger.age for passenger in passengers]
        
        plt.hist(ages, bins=12, color='lightcoral', alpha=0.7, edgecolor='darkred')
        plt.title('Passenger Age Distribution', fontsize=14, fontweight='bold')
        plt.xlabel('Age')
        plt.ylabel('Number of Passengers')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('age_distribution_chart.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    print("Individual charts saved successfully")

def generate_summary_report():
    """Generate a comprehensive summary report"""
    print("\n=== GENERATING SUMMARY REPORT ===")
    
    report = []
    report.append("AIRPORT MANAGEMENT SYSTEM - DATA ANALYSIS REPORT")
    report.append("=" * 60)
    report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Flight statistics
    flight_count = Flight.objects.count()
    report.append(f"FLIGHT STATISTICS:")
    report.append(f"Total Flights: {flight_count}")
    
    if flight_count > 0:
        airlines = Flight.objects.values_list('airline', flat=True).distinct()
        report.append(f"Airlines: {len(airlines)}")
        
        destinations = Flight.objects.values_list('arrival_city', flat=True).distinct()
        report.append(f"Destinations: {len(destinations)}")
    
    # Passenger statistics
    passenger_count = Passenger.objects.count()
    report.append(f"\nPASSENGER STATISTICS:")
    report.append(f"Total Passengers: {passenger_count}")
    
    # Booking statistics
    booking_count = Booking.objects.count()
    confirmed_bookings = Booking.objects.filter(status='confirmed').count()
    report.append(f"\nBOOKING STATISTICS:")
    report.append(f"Total Bookings: {booking_count}")
    report.append(f"Confirmed Bookings: {confirmed_bookings}")
    
    if booking_count > 0:
        total_revenue = sum(float(b.total_amount) for b in Booking.objects.all())
        report.append(f"Total Revenue: ₹{total_revenue:,.2f}")
    
    # Staff statistics
    staff_count = Staff.objects.count()
    report.append(f"\nSTAFF STATISTICS:")
    report.append(f"Total Staff: {staff_count}")
    
    # Check-in statistics
    checkin_count = CheckIn.objects.count()
    report.append(f"\nCHECK-IN STATISTICS:")
    report.append(f"Total Check-ins: {checkin_count}")
    
    report_text = "\n".join(report)
    
    # Save to file
    with open('airport_summary_report.txt', 'w') as f:
        f.write(report_text)
    
    print(report_text)
    print("\nSummary report saved as 'airport_summary_report.txt'")

def main():
    """Main function to run all analyses"""
    print("Airport Management System - Data Analysis")
    print("CBSE Class 12 Informatics Practices Project")
    print("=" * 50)
    
    try:
        # Run analyses
        df_flights = analyze_flight_data()
        df_passengers = analyze_passenger_data()
        df_bookings = analyze_booking_data()
        
        # Create visualizations
        create_visualizations()
        
        # Generate report
        generate_summary_report()
        
        print("\n" + "=" * 50)
        print("Analysis completed successfully!")
        print("Files generated:")
        print("- airport_analysis_dashboard.png")
        print("- destinations_chart.png")
        print("- age_distribution_chart.png")
        print("- airport_summary_report.txt")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        print("Make sure the database is set up and contains sample data.")

if __name__ == "__main__":
    main()
