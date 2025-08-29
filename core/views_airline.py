# Airline Operations Portal Views
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta, date
import json

from .models import (Flight, Passenger, Booking, Staff, CheckIn, Gate, Aircraft, 
                    CrewAssignment, SystemAlert, FlightOperationsMetrics, AuditLog)
from .forms import FlightForm, GateAssignmentForm, CrewAssignmentForm

def is_airline_staff(user):
    """Check if user has airline operations access"""
    if not user.is_authenticated:
        return False
    try:
        staff = user.staff
        return staff.role in ['dispatcher', 'gate_agent', 'ground_staff', 'admin'] and staff.is_active
    except:
        return user.is_staff

@user_passes_test(is_airline_staff)
def operations_dashboard(request):
    """Main Operations Command Dashboard"""
    today = date.today()
    
    # Real-time flight metrics
    flights_today = Flight.objects.filter(departure_time__date=today)
    total_flights = flights_today.count()
    on_time_flights = flights_today.filter(status='departed', actual_departure__lte=timezone.F('departure_time')).count()
    delayed_flights = flights_today.filter(status='delayed').count()
    cancelled_flights = flights_today.filter(status='cancelled').count()
    
    # Current active flights
    active_flights = Flight.objects.filter(
        departure_time__lte=timezone.now(),
        arrival_time__gte=timezone.now(),
        status__in=['departed', 'boarding']
    ).order_by('departure_time')
    
    # Gate utilization
    total_gates = Gate.objects.count()
    occupied_gates = Gate.objects.filter(status='occupied').count()
    gate_utilization = (occupied_gates / total_gates * 100) if total_gates > 0 else 0
    
    # Upcoming departures (next 2 hours)
    upcoming_departures = Flight.objects.filter(
        departure_time__gte=timezone.now(),
        departure_time__lte=timezone.now() + timedelta(hours=2),
        status='scheduled'
    ).order_by('departure_time')[:10]
    
    # Recent alerts
    recent_alerts = SystemAlert.objects.filter(
        is_resolved=False
    ).order_by('-created_at')[:5]
    
    # Weather info (simplified)
    weather_conditions = "Clear skies, 22°C, Wind: 10 km/h NE"
    
    context = {
        'total_flights': total_flights,
        'on_time_flights': on_time_flights,
        'delayed_flights': delayed_flights,
        'cancelled_flights': cancelled_flights,
        'on_time_percentage': (on_time_flights / total_flights * 100) if total_flights > 0 else 0,
        'active_flights': active_flights,
        'gate_utilization': gate_utilization,
        'upcoming_departures': upcoming_departures,
        'recent_alerts': recent_alerts,
        'weather_conditions': weather_conditions,
    }
    return render(request, 'airline/operations_dashboard.html', context)

@user_passes_test(is_airline_staff)
def flight_scheduling(request):
    """Interactive Flight Scheduling Dashboard"""
    # Get flights for the next 7 days
    start_date = timezone.now().date()
    end_date = start_date + timedelta(days=7)
    
    flights = Flight.objects.filter(
        departure_time__date__range=[start_date, end_date]
    ).order_by('departure_time')
    
    # Available aircraft
    available_aircraft = Aircraft.objects.filter(status='active')
    
    # Gate availability
    gates = Gate.objects.all().order_by('gate_number')
    
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            flight = form.save()
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action_type='create',
                model_name='Flight',
                object_id=str(flight.id),
                description=f'Created flight {flight.flight_number}',
                portal_used='airline'
            )
            
            messages.success(request, f'Flight {flight.flight_number} scheduled successfully!')
            return redirect('flight_scheduling')
    else:
        form = FlightForm()
    
    context = {
        'flights': flights,
        'available_aircraft': available_aircraft,
        'gates': gates,
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'airline/flight_scheduling.html', context)

@user_passes_test(is_airline_staff)
def gate_management(request):
    """Automated Gate Management Dashboard"""
    gates = Gate.objects.all().order_by('terminal', 'gate_number')
    
    # Current gate assignments
    current_assignments = Flight.objects.filter(
        gate__isnull=False,
        departure_time__date=date.today(),
        status__in=['scheduled', 'boarding', 'delayed']
    ).order_by('departure_time')
    
    # Boarding timeline for next 4 hours
    boarding_timeline = Flight.objects.filter(
        departure_time__gte=timezone.now(),
        departure_time__lte=timezone.now() + timedelta(hours=4),
        gate__isnull=False
    ).order_by('departure_time')
    
    context = {
        'gates': gates,
        'current_assignments': current_assignments,
        'boarding_timeline': boarding_timeline,
    }
    return render(request, 'airline/gate_management.html', context)

@user_passes_test(is_airline_staff)
def passenger_assistance(request):
    """Passenger Exception Handling Interface"""
    # Passengers needing assistance
    assistance_needed = []
    
    # Failed check-ins
    failed_checkins = Booking.objects.filter(
        flight__departure_time__gte=timezone.now(),
        flight__departure_time__lte=timezone.now() + timedelta(hours=24),
        status='confirmed'
    ).exclude(
        id__in=CheckIn.objects.values_list('booking_id', flat=True)
    )
    
    # Special assistance requests
    special_assistance = CheckIn.objects.filter(
        booking__flight__departure_time__gte=timezone.now(),
        special_assistance__isnull=False
    ).exclude(special_assistance='')
    
    # Overbooked flights
    overbooked_flights = []
    for flight in Flight.objects.filter(departure_time__date=date.today()):
        booked_seats = Booking.objects.filter(flight=flight, status__in=['confirmed', 'checked_in']).count()
        if booked_seats > flight.total_seats:
            overbooked_flights.append({
                'flight': flight,
                'overbooked_by': booked_seats - flight.total_seats
            })
    
    context = {
        'failed_checkins': failed_checkins,
        'special_assistance': special_assistance,
        'overbooked_flights': overbooked_flights,
    }
    return render(request, 'airline/passenger_assistance.html', context)

@user_passes_test(is_airline_staff)
def turnaround_coordination(request):
    """Aircraft Turnaround Coordination Dashboard"""
    # Flights arriving in next 2 hours
    arriving_flights = Flight.objects.filter(
        arrival_time__gte=timezone.now(),
        arrival_time__lte=timezone.now() + timedelta(hours=2),
        status__in=['departed', 'boarding']
    ).order_by('arrival_time')
    
    # Flights departing in next 4 hours (potential turnarounds)
    departing_flights = Flight.objects.filter(
        departure_time__gte=timezone.now(),
        departure_time__lte=timezone.now() + timedelta(hours=4),
        status='scheduled'
    ).order_by('departure_time')
    
    # Turnaround tasks template
    turnaround_tasks = [
        {'task': 'Passenger Disembarkation', 'duration': 20, 'status': 'pending'},
        {'task': 'Cabin Cleaning', 'duration': 30, 'status': 'pending'},
        {'task': 'Catering Service', 'duration': 15, 'status': 'pending'},
        {'task': 'Fuel Service', 'duration': 25, 'status': 'pending'},
        {'task': 'Baggage Unloading', 'duration': 20, 'status': 'pending'},
        {'task': 'Baggage Loading', 'duration': 25, 'status': 'pending'},
        {'task': 'Safety Check', 'duration': 15, 'status': 'pending'},
        {'task': 'Passenger Boarding', 'duration': 30, 'status': 'pending'},
    ]
    
    context = {
        'arriving_flights': arriving_flights,
        'departing_flights': departing_flights,
        'turnaround_tasks': turnaround_tasks,
    }
    return render(request, 'airline/turnaround_coordination.html', context)

@user_passes_test(is_airline_staff)
def analytics_reporting(request):
    """Analytics & Reporting Suite"""
    # Date range selection
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    
    # Performance metrics
    flights_in_period = Flight.objects.filter(departure_time__date__range=[start_date, end_date])
    
    total_flights = flights_in_period.count()
    on_time_flights = flights_in_period.filter(
        actual_departure__lte=timezone.F('departure_time')
    ).count()
    
    # Revenue analysis
    revenue_data = []
    bookings_in_period = Booking.objects.filter(
        booking_date__date__range=[start_date, end_date],
        payment_status=True
    )
    
    total_revenue = sum(booking.total_amount for booking in bookings_in_period)
    average_ticket_price = bookings_in_period.aggregate(avg_price=Avg('total_amount'))['avg_price'] or 0
    
    # Route profitability
    route_performance = flights_in_period.values(
        'departure_city', 'arrival_city'
    ).annotate(
        flight_count=Count('id'),
        total_bookings=Count('booking')
    ).order_by('-flight_count')[:10]
    
    # Passenger load factor
    load_factors = []
    for flight in flights_in_period:
        booked_seats = Booking.objects.filter(flight=flight, status__in=['confirmed', 'checked_in']).count()
        load_factor = (booked_seats / flight.total_seats * 100) if flight.total_seats > 0 else 0
        load_factors.append(load_factor)
    
    average_load_factor = sum(load_factors) / len(load_factors) if load_factors else 0
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_flights': total_flights,
        'on_time_flights': on_time_flights,
        'on_time_percentage': (on_time_flights / total_flights * 100) if total_flights > 0 else 0,
        'total_revenue': total_revenue,
        'average_ticket_price': average_ticket_price,
        'average_load_factor': average_load_factor,
        'route_performance': route_performance,
    }
    return render(request, 'airline/analytics_reporting.html', context)

@user_passes_test(is_airline_staff)
def live_flight_map(request):
    """Live Flight Tracking Map"""
    # Active flights (in-air)
    active_flights = Flight.objects.filter(
        status='departed',
        actual_departure__isnull=False,
        arrival_time__gte=timezone.now()
    )
    
    # Prepare flight data for map
    flight_data = []
    for flight in active_flights:
        # Calculate estimated position (simplified)
        flight_duration = (flight.arrival_time - flight.departure_time).total_seconds()
        elapsed_time = (timezone.now() - flight.actual_departure).total_seconds()
        progress = min(elapsed_time / flight_duration, 1.0) if flight_duration > 0 else 0
        
        flight_data.append({
            'flight_number': flight.flight_number,
            'departure_city': flight.departure_city,
            'arrival_city': flight.arrival_city,
            'progress': progress * 100,
            'altitude': 35000,  # Simplified
            'speed': 850,       # Simplified
            'status': flight.status,
        })
    
    context = {
        'flight_data': json.dumps(flight_data),
        'active_flights': active_flights,
    }
    return render(request, 'airline/live_flight_map.html', context)

@user_passes_test(is_airline_staff)
def system_alerts(request):
    """System Alerts and Notifications"""
    alerts = SystemAlert.objects.all().order_by('-created_at')
    
    # Filter by type if specified
    alert_type = request.GET.get('type')
    if alert_type:
        alerts = alerts.filter(alert_type=alert_type)
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'unresolved':
        alerts = alerts.filter(is_resolved=False)
    elif status == 'resolved':
        alerts = alerts.filter(is_resolved=True)
    
    paginator = Paginator(alerts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'alert_types': SystemAlert.ALERT_TYPES,
    }
    return render(request, 'airline/system_alerts.html', context)

@user_passes_test(is_airline_staff)
def resolve_alert(request, alert_id):
    """Mark alert as resolved"""
    alert = get_object_or_404(SystemAlert, id=alert_id)
    
    if request.method == 'POST':
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save()
        
        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action_type='update',
            model_name='SystemAlert',
            object_id=str(alert.id),
            description=f'Resolved alert: {alert.title}',
            portal_used='airline'
        )
        
        messages.success(request, 'Alert marked as resolved.')
    
    return redirect('system_alerts')
