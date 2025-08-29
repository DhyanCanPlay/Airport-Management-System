# Crew Portal Views
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta, date
import json

from .models import Staff, CrewAssignment, Flight, AuditLog
from .forms import PostFlightReportForm, CrewAvailabilityForm

def is_crew_member(user):
    """Check if user is crew member"""
    if not user.is_authenticated:
        return False
    try:
        staff = user.staff
        return staff.role in ['pilot', 'copilot', 'cabin_crew'] and staff.is_active
    except:
        return False

@user_passes_test(is_crew_member)
def crew_dashboard(request):
    """Crew Portal Dashboard"""
    staff = request.user.staff
    
    # Upcoming assignments
    upcoming_assignments = CrewAssignment.objects.filter(
        staff=staff,
        flight__departure_time__gte=timezone.now(),
        status__in=['scheduled', 'confirmed']
    ).order_by('flight__departure_time')[:5]
    
    # Today's assignments
    today_assignments = CrewAssignment.objects.filter(
        staff=staff,
        flight__departure_time__date=date.today(),
        status__in=['scheduled', 'confirmed']
    ).order_by('flight__departure_time')
    
    # Recent completed flights
    completed_assignments = CrewAssignment.objects.filter(
        staff=staff,
        status='completed'
    ).order_by('-flight__departure_time')[:5]
    
    # License and certification status
    license_valid = staff.license_valid
    license_expires_soon = False
    medical_expires_soon = False
    
    if staff.license_expiry:
        days_to_expiry = (staff.license_expiry - date.today()).days
        license_expires_soon = days_to_expiry <= 30
    
    if staff.medical_expiry:
        days_to_medical_expiry = (staff.medical_expiry - date.today()).days
        medical_expires_soon = days_to_medical_expiry <= 30
    
    # Training due
    training_due = staff.needs_training
    
    context = {
        'staff': staff,
        'upcoming_assignments': upcoming_assignments,
        'today_assignments': today_assignments,
        'completed_assignments': completed_assignments,
        'license_valid': license_valid,
        'license_expires_soon': license_expires_soon,
        'medical_expires_soon': medical_expires_soon,
        'training_due': training_due,
    }
    return render(request, 'crew/dashboard.html', context)

@user_passes_test(is_crew_member)
def my_roster(request):
    """Personal Roster - Interactive Calendar"""
    staff = request.user.staff
    
    # Get month/year from request or default to current
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    
    # Get assignments for the month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    assignments = CrewAssignment.objects.filter(
        staff=staff,
        flight__departure_time__date__range=[start_date, end_date]
    ).order_by('flight__departure_time')
    
    # Organize assignments by date
    assignments_by_date = {}
    for assignment in assignments:
        flight_date = assignment.flight.departure_time.date()
        if flight_date not in assignments_by_date:
            assignments_by_date[flight_date] = []
        assignments_by_date[flight_date].append(assignment)
    
    # Calculate total flight hours for the month
    total_hours = 0
    for assignment in assignments:
        if assignment.flight.arrival_time and assignment.flight.departure_time:
            flight_duration = assignment.flight.arrival_time - assignment.flight.departure_time
            total_hours += flight_duration.total_seconds() / 3600
    
    # Navigation dates
    if month == 1:
        prev_month = {'year': year - 1, 'month': 12}
    else:
        prev_month = {'year': year, 'month': month - 1}
    
    if month == 12:
        next_month = {'year': year + 1, 'month': 1}
    else:
        next_month = {'year': year, 'month': month + 1}
    
    context = {
        'staff': staff,
        'assignments': assignments,
        'assignments_by_date': assignments_by_date,
        'current_month': f"{date(year, month, 1).strftime('%B %Y')}",
        'total_hours': round(total_hours, 1),
        'prev_month': prev_month,
        'next_month': next_month,
        'year': year,
        'month': month,
    }
    return render(request, 'crew/my_roster.html', context)

@user_passes_test(is_crew_member)
def flight_briefing(request, assignment_id):
    """Flight Briefing Packets"""
    staff = request.user.staff
    assignment = get_object_or_404(CrewAssignment, id=assignment_id, staff=staff)
    flight = assignment.flight
    
    # Mark briefing as completed
    if request.method == 'POST':
        assignment.briefing_completed = True
        assignment.save()
        
        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action_type='update',
            model_name='CrewAssignment',
            object_id=str(assignment.id),
            description=f'Completed briefing for flight {flight.flight_number}',
            portal_used='crew'
        )
        
        messages.success(request, 'Flight briefing marked as completed.')
        return redirect('my_roster')
    
    # Generate briefing data
    briefing_data = {
        'flight_plan': {
            'route': f"{flight.departure_airport} → {flight.arrival_airport}",
            'distance': '2,450 km',  # Simplified
            'flight_time': str(flight.arrival_time - flight.departure_time),
            'altitude': '35,000 ft',
            'airspeed': '850 km/h',
        },
        'weather': {
            'departure': 'Clear, 22°C, Wind: 10 km/h NE',
            'arrival': 'Partly cloudy, 18°C, Wind: 15 km/h SW',
            'en_route': 'Light turbulence expected over mountain ranges',
        },
        'passenger_info': {
            'total_passengers': flight.total_seats - flight.available_seats,
            'business_class': 12,  # Simplified
            'economy_class': flight.total_seats - flight.available_seats - 12,
            'special_assistance': 3,
            'unaccompanied_minors': 1,
        },
        'notams': [
            'RUNWAY 09/27 CLOSED FOR MAINTENANCE 1200-1800 UTC',
            'TEMPORARY RESTRICTED AREA ACTIVE OVER CITY CENTER',
            'VOR STATION XYZ OUT OF SERVICE',
        ],
        'crew_info': [
            assignment for assignment in CrewAssignment.objects.filter(flight=flight)
        ]
    }
    
    context = {
        'assignment': assignment,
        'flight': flight,
        'briefing_data': briefing_data,
    }
    return render(request, 'crew/flight_briefing.html', context)

@user_passes_test(is_crew_member)
def bidding_swaps(request):
    """Bidding & Schedule Swaps"""
    staff = request.user.staff
    
    # Available flights for bidding (next month)
    next_month = date.today().replace(day=1) + timedelta(days=32)
    next_month = next_month.replace(day=1)
    
    available_flights = Flight.objects.filter(
        departure_time__month=next_month.month,
        departure_time__year=next_month.year
    ).exclude(
        id__in=CrewAssignment.objects.filter(
            flight__departure_time__month=next_month.month,
            flight__departure_time__year=next_month.year
        ).values_list('flight_id', flat=True)
    )[:20]  # Limit for demo
    
    # Current assignments available for swap
    my_assignments = CrewAssignment.objects.filter(
        staff=staff,
        flight__departure_time__gte=timezone.now() + timedelta(days=7),  # Must be at least a week away
        status='scheduled'
    )
    
    # Swap requests from other crew members
    swap_requests = []  # Would be implemented with a SwapRequest model
    
    context = {
        'available_flights': available_flights,
        'my_assignments': my_assignments,
        'swap_requests': swap_requests,
        'next_month': next_month.strftime('%B %Y'),
    }
    return render(request, 'crew/bidding_swaps.html', context)

@user_passes_test(is_crew_member)
def my_qualifications(request):
    """Personal Qualifications Dashboard"""
    staff = request.user.staff
    
    # Calculate days until expiry
    license_days_left = None
    medical_days_left = None
    training_days_left = None
    
    if staff.license_expiry:
        license_days_left = (staff.license_expiry - date.today()).days
    
    if staff.medical_expiry:
        medical_days_left = (staff.medical_expiry - date.today()).days
    
    if staff.next_training_due:
        training_days_left = (staff.next_training_due - date.today()).days
    
    # Qualification history (simplified)
    qualification_history = [
        {
            'type': 'Commercial Pilot License',
            'obtained': '2020-03-15',
            'expires': staff.license_expiry,
            'status': 'Valid' if staff.license_valid else 'Expired'
        },
        {
            'type': 'Medical Certificate Class 1',
            'obtained': '2023-08-10',
            'expires': staff.medical_expiry,
            'status': 'Valid'
        },
        {
            'type': 'Recurrent Training',
            'completed': staff.last_training,
            'next_due': staff.next_training_due,
            'status': 'Current' if not staff.needs_training else 'Due'
        }
    ]
    
    context = {
        'staff': staff,
        'license_days_left': license_days_left,
        'medical_days_left': medical_days_left,
        'training_days_left': training_days_left,
        'qualification_history': qualification_history,
    }
    return render(request, 'crew/my_qualifications.html', context)

@user_passes_test(is_crew_member)
def post_flight_report(request, assignment_id):
    """Post-Flight Reporting"""
    staff = request.user.staff
    assignment = get_object_or_404(CrewAssignment, id=assignment_id, staff=staff)
    
    # Only allow reports for completed or current flights
    if assignment.flight.departure_time > timezone.now():
        messages.error(request, 'Cannot submit report for future flights.')
        return redirect('my_roster')
    
    if request.method == 'POST':
        form = PostFlightReportForm(request.POST)
        if form.is_valid():
            # Save report to assignment
            assignment.post_flight_report = form.cleaned_data['report_content']
            assignment.status = 'completed'
            assignment.save()
            
            # Update staff flight hours
            if assignment.flight.arrival_time and assignment.flight.departure_time:
                flight_duration = assignment.flight.arrival_time - assignment.flight.departure_time
                flight_hours = flight_duration.total_seconds() / 3600
                staff.flight_hours += int(flight_hours)
                staff.save()
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action_type='update',
                model_name='CrewAssignment',
                object_id=str(assignment.id),
                description=f'Submitted post-flight report for {assignment.flight.flight_number}',
                portal_used='crew'
            )
            
            messages.success(request, 'Post-flight report submitted successfully.')
            return redirect('my_roster')
    else:
        form = PostFlightReportForm()
    
    context = {
        'assignment': assignment,
        'form': form,
    }
    return render(request, 'crew/post_flight_report.html', context)

@user_passes_test(is_crew_member)
def crew_messages(request):
    """Crew Communication Center"""
    # This would integrate with a messaging system
    # For demo purposes, showing static content
    
    messages_list = [
        {
            'id': 1,
            'from': 'Crew Scheduling',
            'subject': 'Schedule Change - Flight AA123',
            'date': timezone.now() - timedelta(hours=2),
            'read': False,
            'priority': 'high'
        },
        {
            'id': 2,
            'from': 'Training Department',
            'subject': 'Recurrent Training Reminder',
            'date': timezone.now() - timedelta(days=1),
            'read': True,
            'priority': 'normal'
        },
        {
            'id': 3,
            'from': 'Operations',
            'subject': 'Weather Advisory - Route Updates',
            'date': timezone.now() - timedelta(days=2),
            'read': True,
            'priority': 'normal'
        }
    ]
    
    context = {
        'messages': messages_list,
    }
    return render(request, 'crew/messages.html', context)

@user_passes_test(is_crew_member)
def training_center(request):
    """Training and Certification Center"""
    staff = request.user.staff
    
    # Available training modules
    training_modules = [
        {
            'title': 'Emergency Procedures Review',
            'duration': '2 hours',
            'required': staff.needs_training,
            'deadline': staff.next_training_due,
            'status': 'available'
        },
        {
            'title': 'New Aircraft Type Rating',
            'duration': '40 hours',
            'required': False,
            'deadline': None,
            'status': 'available'
        },
        {
            'title': 'Customer Service Excellence',
            'duration': '1 hour',
            'required': False,
            'deadline': None,
            'status': 'completed'
        }
    ]
    
    # Training history
    training_history = [
        {
            'course': 'Annual Recurrent Training',
            'completed': staff.last_training,
            'score': '95%',
            'instructor': 'Capt. Johnson'
        }
    ]
    
    context = {
        'staff': staff,
        'training_modules': training_modules,
        'training_history': training_history,
    }
    return render(request, 'crew/training_center.html', context)
