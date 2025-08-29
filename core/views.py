from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
import pandas as pd
import io
import base64

from .models import Flight, Passenger, Booking, Staff, CheckIn
from .forms import (FlightForm, PassengerForm, BookingForm, StaffForm, 
                   CheckInForm, UserRegistrationForm, FlightSearchForm)

def is_staff_user(user):
    """Check if user is staff member"""
    return user.is_authenticated and (user.is_staff or hasattr(user, 'staff'))

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
import pandas as pd
import io
import base64

from .models import Flight, Passenger, Booking, Staff, CheckIn, UserProfile
from .forms import (FlightForm, PassengerForm, BookingForm, StaffForm, 
                   CheckInForm, UserRegistrationForm, FlightSearchForm)

def is_staff_user(user):
    """Check if user is staff member"""
    return user.is_authenticated and (user.is_staff or hasattr(user, 'staff'))

# Enhanced Home View with Portal Direction
def home(request):
    """Enhanced homepage with portal direction"""
    if request.user.is_authenticated:
        # Direct authenticated users to their appropriate portal
        try:
            profile = request.user.userprofile
            portal = profile.portal_access
            
            if portal == 'customer':
                return redirect('/customer/')
            elif portal == 'airline':
                return redirect('/airline/')
            elif portal == 'crew':
                return redirect('/crew/')
            elif portal == 'admin':
                return redirect('/admin-portal/')
        except UserProfile.DoesNotExist:
            # Create a default customer profile
            UserProfile.objects.create(
                user=request.user,
                portal_access='customer'
            )
            return redirect('/customer/')
    
    # Public homepage for non-authenticated users
    recent_flights = Flight.objects.filter(
        departure_time__gte=timezone.now()
    ).order_by('departure_time')[:6]
    
    total_flights = Flight.objects.count()
    total_passengers = Passenger.objects.count()
    total_bookings = Booking.objects.filter(status='confirmed').count()
    
    # Live departures for public information
    departing_soon = Flight.objects.filter(
        departure_time__gte=timezone.now(),
        departure_time__lte=timezone.now() + timedelta(hours=4)
    ).order_by('departure_time')[:8]
    
    context = {
        'recent_flights': recent_flights,
        'total_flights': total_flights,
        'total_passengers': total_passengers,
        'total_bookings': total_bookings,
        'departing_soon': departing_soon,
        'show_portal_links': True,  # Show portal access links for guests
    }
    return render(request, 'core/home.html', context)

def flight_list(request):
    """Public flight listing with search functionality"""
    form = FlightSearchForm(request.GET)
    flights = Flight.objects.filter(departure_time__gte=timezone.now()).order_by('departure_time')
    
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
    return render(request, 'core/flight_list.html', context)

def flight_detail(request, flight_id):
    """Flight detail view"""
    flight = get_object_or_404(Flight, id=flight_id)
    return render(request, 'core/flight_detail.html', {'flight': flight})

# Staff-only Views
@user_passes_test(is_staff_user)
def passenger_list(request):
    """List all passengers (staff only)"""
    passengers = Passenger.objects.all().order_by('last_name', 'first_name')
    
    search = request.GET.get('search')
    if search:
        passengers = passengers.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(passport_number__icontains=search)
        )
    
    paginator = Paginator(passengers, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/passenger_list.html', {'page_obj': page_obj})

@user_passes_test(is_staff_user)
def passenger_create(request):
    """Create new passenger"""
    if request.method == 'POST':
        form = PassengerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Passenger created successfully!')
            return redirect('passenger_list')
    else:
        form = PassengerForm()
    return render(request, 'core/passenger_form.html', {'form': form, 'title': 'Add Passenger'})

@user_passes_test(is_staff_user)
def passenger_edit(request, passenger_id):
    """Edit passenger"""
    passenger = get_object_or_404(Passenger, id=passenger_id)
    if request.method == 'POST':
        form = PassengerForm(request.POST, instance=passenger)
        if form.is_valid():
            form.save()
            messages.success(request, 'Passenger updated successfully!')
            return redirect('passenger_list')
    else:
        form = PassengerForm(instance=passenger)
    return render(request, 'core/passenger_form.html', {'form': form, 'title': 'Edit Passenger'})

@user_passes_test(is_staff_user)
def booking_list(request):
    """List all bookings (staff only)"""
    bookings = Booking.objects.select_related('passenger', 'flight').order_by('-booking_date')
    
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    paginator = Paginator(bookings, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/booking_list.html', {'page_obj': page_obj})

@user_passes_test(is_staff_user)
def booking_create(request):
    """Create new booking"""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.total_amount = booking.flight.price
            booking.save()
            
            # Update available seats
            flight = booking.flight
            flight.available_seats -= 1
            flight.save()
            
            messages.success(request, f'Booking created successfully! Reference: {booking.booking_reference}')
            return redirect('booking_list')
    else:
        form = BookingForm()
    return render(request, 'core/booking_form.html', {'form': form, 'title': 'Create Booking'})

@user_passes_test(is_staff_user)
def staff_list(request):
    """List all staff members"""
    staff_members = Staff.objects.select_related('user').order_by('user__last_name')
    
    role_filter = request.GET.get('role')
    if role_filter:
        staff_members = staff_members.filter(role=role_filter)
    
    paginator = Paginator(staff_members, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/staff_list.html', {'page_obj': page_obj})

@user_passes_test(is_staff_user)
def checkin_list(request):
    """List all check-ins"""
    checkins = CheckIn.objects.select_related('booking__passenger', 'booking__flight').order_by('-check_in_time')
    
    paginator = Paginator(checkins, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/checkin_list.html', {'page_obj': page_obj})

@user_passes_test(is_staff_user)
def checkin_create(request):
    """Create new check-in"""
    if request.method == 'POST':
        form = CheckInForm(request.POST)
        if form.is_valid():
            checkin = form.save(commit=False)
            if hasattr(request.user, 'staff'):
                checkin.staff = request.user.staff
            checkin.save()
            messages.success(request, 'Check-in completed successfully!')
            return redirect('checkin_list')
    else:
        form = CheckInForm()
    return render(request, 'core/checkin_form.html', {'form': form, 'title': 'Check-In Passenger'})

@user_passes_test(is_staff_user)
def reports(request):
    """Generate reports and visualizations"""
    # Basic statistics
    total_flights = Flight.objects.count()
    total_passengers = Passenger.objects.count()
    total_bookings = Booking.objects.count()
    total_staff = Staff.objects.count()
    
    # Bookings by status
    booking_stats = Booking.objects.values('status').annotate(count=Count('id'))
    
    # Flights by destination
    destination_stats = Flight.objects.values('arrival_city').annotate(count=Count('id')).order_by('-count')[:10]
    
    context = {
        'total_flights': total_flights,
        'total_passengers': total_passengers,
        'total_bookings': total_bookings,
        'total_staff': total_staff,
        'booking_stats': booking_stats,
        'destination_stats': destination_stats,
    }
    
    return render(request, 'core/reports.html', context)

def generate_chart(request, chart_type):
    """Generate charts using matplotlib"""
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if chart_type == 'destinations':
        # Flights by destination
        data = Flight.objects.values('arrival_city').annotate(count=Count('id')).order_by('-count')[:10]
        cities = [item['arrival_city'] for item in data]
        counts = [item['count'] for item in data]
        
        ax.bar(cities, counts, color='skyblue')
        ax.set_title('Top 10 Flight Destinations')
        ax.set_xlabel('Cities')
        ax.set_ylabel('Number of Flights')
        plt.xticks(rotation=45, ha='right')
        
    elif chart_type == 'bookings':
        # Bookings by status
        data = Booking.objects.values('status').annotate(count=Count('id'))
        statuses = [item['status'].title() for item in data]
        counts = [item['count'] for item in data]
        
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        ax.pie(counts, labels=statuses, autopct='%1.1f%%', colors=colors)
        ax.set_title('Booking Status Distribution')
        
    elif chart_type == 'age_distribution':
        # Passenger age distribution
        passengers = Passenger.objects.all()
        ages = [p.age for p in passengers]
        
        ax.hist(ages, bins=10, color='lightgreen', alpha=0.7, edgecolor='black')
        ax.set_title('Passenger Age Distribution')
        ax.set_xlabel('Age')
        ax.set_ylabel('Number of Passengers')
    
    plt.tight_layout()
    
    # Save plot to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    
    plt.close()
    
    return JsonResponse({'image': graphic})

# Authentication Views
def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})
