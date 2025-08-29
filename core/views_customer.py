# Customer Portal Views
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import Flight, Passenger, Booking, CheckIn, UserProfile
from .forms import FlightSearchForm, BookingForm, PassengerForm

def customer_dashboard(request):
    """Customer Portal Dashboard"""
    if request.user.is_authenticated:
        try:
            passenger = request.user.passenger
            recent_bookings = Booking.objects.filter(passenger=passenger).order_by('-booking_date')[:5]
            upcoming_flights = Booking.objects.filter(
                passenger=passenger,
                flight__departure_time__gte=timezone.now(),
                status__in=['confirmed', 'checked_in']
            ).order_by('flight__departure_time')[:3]
        except:
            recent_bookings = []
            upcoming_flights = []
    else:
        recent_bookings = []
        upcoming_flights = []
    
    # Public flight information
    departing_soon = Flight.objects.filter(
        departure_time__gte=timezone.now(),
        departure_time__lte=timezone.now() + timedelta(hours=6)
    ).order_by('departure_time')[:8]
    
    context = {
        'recent_bookings': recent_bookings,
        'upcoming_flights': upcoming_flights,
        'departing_soon': departing_soon,
    }
    return render(request, 'customer/dashboard.html', context)

def flight_search(request):
    """Advanced Flight Search"""
    form = FlightSearchForm(request.GET)
    flights = Flight.objects.filter(
        departure_time__gte=timezone.now(),
        available_seats__gt=0
    ).order_by('departure_time')
    
    if form.is_valid():
        if form.cleaned_data['departure_city']:
            flights = flights.filter(departure_city__icontains=form.cleaned_data['departure_city'])
        if form.cleaned_data['arrival_city']:
            flights = flights.filter(arrival_city__icontains=form.cleaned_data['arrival_city'])
        if form.cleaned_data['departure_date']:
            flights = flights.filter(departure_time__date=form.cleaned_data['departure_date'])
        if form.cleaned_data['airline']:
            flights = flights.filter(airline__icontains=form.cleaned_data['airline'])
    
    paginator = Paginator(flights, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'flights': page_obj,
    }
    return render(request, 'customer/flight_search.html', context)

def flight_detail_booking(request, flight_id):
    """Flight Detail with Booking Options"""
    flight = get_object_or_404(Flight, id=flight_id)
    
    # Check available seats by class
    business_available = max(0, flight.aircraft.business_seats if flight.aircraft else 0)
    economy_available = flight.available_seats
    
    context = {
        'flight': flight,
        'business_available': business_available,
        'economy_available': economy_available,
    }
    return render(request, 'customer/flight_detail.html', context)

@login_required
def make_booking(request, flight_id):
    """Create a new booking"""
    flight = get_object_or_404(Flight, id=flight_id)
    
    if request.method == 'POST':
        # Get or create passenger profile
        try:
            passenger = request.user.passenger
        except:
            # Create passenger from user data
            passenger = Passenger.objects.create(
                user=request.user,
                first_name=request.user.first_name,
                last_name=request.user.last_name,
                email=request.user.email,
                # Other fields would be filled in registration
                phone_number='+1234567890',
                date_of_birth='1990-01-01',
                gender='M',
                passport_number='TEMP123456',
                passport_expiry='2030-01-01',
                nationality='Unknown',
                address='Not provided'
            )
        
        seat_class = request.POST.get('seat_class', 'economy')
        seat_number = request.POST.get('seat_number', 'AUTO')
        
        # Calculate price based on class
        if seat_class == 'business':
            price = flight.business_price
        else:
            price = flight.economy_price
        
        # Create booking
        booking = Booking.objects.create(
            passenger=passenger,
            flight=flight,
            seat_number=seat_number,
            seat_class=seat_class,
            base_price=price,
            taxes_fees=price * 0.15,  # 15% taxes
            total_amount=price * 1.15,
            status='pending',
            created_by=request.user
        )
        
        # Update available seats
        flight.available_seats -= 1
        flight.save()
        
        messages.success(request, f'Booking created successfully! Reference: {booking.booking_reference}')
        return redirect('my_bookings')
    
    context = {
        'flight': flight,
    }
    return render(request, 'customer/make_booking.html', context)

@login_required
def my_bookings(request):
    """User's booking management"""
    try:
        passenger = request.user.passenger
        bookings = Booking.objects.filter(passenger=passenger).order_by('-booking_date')
    except:
        bookings = []
    
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'bookings': page_obj,
    }
    return render(request, 'customer/my_bookings.html', context)

@login_required
def booking_detail(request, booking_reference):
    """Detailed booking view with management options"""
    try:
        passenger = request.user.passenger
        booking = get_object_or_404(Booking, booking_reference=booking_reference, passenger=passenger)
    except:
        messages.error(request, 'Booking not found.')
        return redirect('my_bookings')
    
    context = {
        'booking': booking,
    }
    return render(request, 'customer/booking_detail.html', context)

@login_required
def online_checkin(request, booking_reference):
    """Online check-in process"""
    try:
        passenger = request.user.passenger
        booking = get_object_or_404(Booking, booking_reference=booking_reference, passenger=passenger)
    except:
        messages.error(request, 'Booking not found.')
        return redirect('my_bookings')
    
    if not booking.can_check_in:
        messages.error(request, 'Check-in is not available for this booking.')
        return redirect('booking_detail', booking_reference=booking_reference)
    
    if request.method == 'POST':
        # Process check-in
        checkin = CheckIn.objects.create(
            booking=booking,
            gate_number=booking.flight.gate_number or 'TBD',
            seat_number=booking.seat_number,
            check_in_method='online',
            status='checked_in'
        )
        
        booking.status = 'checked_in'
        booking.save()
        
        messages.success(request, 'Check-in completed successfully!')
        return redirect('boarding_pass', booking_reference=booking_reference)
    
    context = {
        'booking': booking,
    }
    return render(request, 'customer/online_checkin.html', context)

@login_required
def boarding_pass(request, booking_reference):
    """Digital boarding pass"""
    try:
        passenger = request.user.passenger
        booking = get_object_or_404(Booking, booking_reference=booking_reference, passenger=passenger)
        checkin = booking.checkin
    except:
        messages.error(request, 'Boarding pass not found.')
        return redirect('my_bookings')
    
    context = {
        'booking': booking,
        'checkin': checkin,
    }
    return render(request, 'customer/boarding_pass.html', context)

def live_flight_status(request):
    """Public flight status tracker"""
    flight_number = request.GET.get('flight_number')
    flight = None
    
    if flight_number:
        try:
            flight = Flight.objects.get(flight_number__iexact=flight_number)
        except Flight.DoesNotExist:
            messages.error(request, f'Flight {flight_number} not found.')
    
    context = {
        'flight': flight,
        'flight_number': flight_number,
    }
    return render(request, 'customer/flight_status.html', context)

@login_required
def loyalty_program(request):
    """Loyalty program dashboard"""
    try:
        profile = request.user.userprofile
        passenger = request.user.passenger
        
        # Calculate loyalty metrics
        total_bookings = Booking.objects.filter(passenger=passenger, status='completed').count()
        total_spent = sum(booking.total_amount for booking in Booking.objects.filter(passenger=passenger, payment_status=True))
        
        # Recent completed flights for points calculation
        recent_flights = Booking.objects.filter(
            passenger=passenger,
            status='completed'
        ).order_by('-flight__arrival_time')[:10]
        
    except:
        profile = None
        total_bookings = 0
        total_spent = 0
        recent_flights = []
    
    context = {
        'profile': profile,
        'total_bookings': total_bookings,
        'total_spent': total_spent,
        'recent_flights': recent_flights,
    }
    return render(request, 'customer/loyalty_program.html', context)

def help_center(request):
    """Customer support and help center"""
    faq_items = [
        {
            'question': 'How early can I check in?',
            'answer': 'Online check-in opens 24 hours before your flight departure time.'
        },
        {
            'question': 'Can I change my seat after booking?',
            'answer': 'Yes, you can change your seat through the "Manage Booking" section up to 4 hours before departure.'
        },
        {
            'question': 'What is the baggage allowance?',
            'answer': 'Economy class: 20kg checked baggage. Business class: 30kg checked baggage. Additional baggage can be purchased.'
        },
        {
            'question': 'How do I cancel my booking?',
            'answer': 'You can cancel your booking through "My Bookings". Cancellation fees may apply depending on your fare type.'
        },
    ]
    
    context = {
        'faq_items': faq_items,
    }
    return render(request, 'customer/help_center.html', context)
