# System Administration Portal Views
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group, Permission
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta, date
import json

from .models import (UserProfile, Staff, SystemAlert, AuditLog, FlightOperationsMetrics,
                    Flight, Booking, Passenger, Gate, Aircraft)
from .forms import UserManagementForm, SystemConfigForm

def is_system_admin(user):
    """Check if user has system admin access"""
    if not user.is_authenticated:
        return False
    try:
        staff = user.staff
        return staff.role == 'admin' and staff.is_active
    except:
        return user.is_superuser

@user_passes_test(is_system_admin)
def admin_dashboard(request):
    """System Administration Dashboard"""
    # System health metrics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_count = Staff.objects.filter(is_active=True).count()
    
    # Recent activity
    recent_logins = AuditLog.objects.filter(
        action_type='login',
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    recent_bookings = Booking.objects.filter(
        booking_date__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    # System alerts summary
    critical_alerts = SystemAlert.objects.filter(
        alert_type='critical',
        is_resolved=False
    ).count()
    
    warning_alerts = SystemAlert.objects.filter(
        alert_type='warning',
        is_resolved=False
    ).count()
    
    # Integration status (simplified)
    integration_status = [
        {'system': 'Payment Gateway', 'status': 'operational', 'last_check': timezone.now()},
        {'system': 'Weather Service', 'status': 'operational', 'last_check': timezone.now()},
        {'system': 'Air Traffic Control', 'status': 'warning', 'last_check': timezone.now() - timedelta(minutes=5)},
        {'system': 'Baggage System', 'status': 'operational', 'last_check': timezone.now()},
    ]
    
    # Recent system changes
    recent_changes = AuditLog.objects.filter(
        action_type__in=['create', 'update', 'delete'],
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).order_by('-timestamp')[:10]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'staff_count': staff_count,
        'recent_logins': recent_logins,
        'recent_bookings': recent_bookings,
        'critical_alerts': critical_alerts,
        'warning_alerts': warning_alerts,
        'integration_status': integration_status,
        'recent_changes': recent_changes,
    }
    return render(request, 'admin/dashboard.html', context)

@user_passes_test(is_system_admin)
def user_management(request):
    """User Management Dashboard"""
    users = User.objects.all().order_by('-date_joined')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    elif status == 'staff':
        users = users.filter(is_staff=True)
    
    # Filter by portal access
    portal = request.GET.get('portal')
    if portal:
        users = users.filter(userprofile__portal_access=portal)
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'users': page_obj,
        'portal_choices': UserProfile.PORTAL_CHOICES,
    }
    return render(request, 'admin/user_management.html', context)

@user_passes_test(is_system_admin)
def create_user(request):
    """Create new user account"""
    if request.method == 'POST':
        form = UserManagementForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                portal_access=form.cleaned_data['portal_access'],
                phone_number=form.cleaned_data.get('phone_number', ''),
                loyalty_number=form.cleaned_data.get('loyalty_number', '')
            )
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action_type='create',
                model_name='User',
                object_id=str(user.id),
                description=f'Created user account: {user.username}',
                portal_used='admin'
            )
            
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('user_management')
    else:
        form = UserManagementForm()
    
    context = {
        'form': form,
        'title': 'Create User Account'
    }
    return render(request, 'admin/user_form.html', context)

@user_passes_test(is_system_admin)
def edit_user(request, user_id):
    """Edit user account"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserManagementForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            
            # Update user profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.portal_access = form.cleaned_data['portal_access']
            profile.phone_number = form.cleaned_data.get('phone_number', '')
            profile.loyalty_number = form.cleaned_data.get('loyalty_number', '')
            profile.save()
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action_type='update',
                model_name='User',
                object_id=str(user.id),
                description=f'Updated user account: {user.username}',
                portal_used='admin'
            )
            
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('user_management')
    else:
        # Prepopulate form with user profile data
        initial_data = {}
        try:
            profile = user.userprofile
            initial_data['portal_access'] = profile.portal_access
            initial_data['phone_number'] = profile.phone_number
            initial_data['loyalty_number'] = profile.loyalty_number
        except:
            pass
        
        form = UserManagementForm(instance=user, initial=initial_data)
    
    context = {
        'form': form,
        'user': user,
        'title': f'Edit User: {user.username}'
    }
    return render(request, 'admin/user_form.html', context)

@user_passes_test(is_system_admin)
def roles_permissions(request):
    """Roles & Permissions Management"""
    # Get all groups (roles)
    groups = Group.objects.all().order_by('name')
    
    # Get all permissions
    permissions = Permission.objects.all().order_by('content_type__model', 'codename')
    
    # Staff roles summary
    staff_roles = Staff.objects.values('role').annotate(count=Count('id')).order_by('role')
    
    context = {
        'groups': groups,
        'permissions': permissions,
        'staff_roles': staff_roles,
    }
    return render(request, 'admin/roles_permissions.html', context)

@user_passes_test(is_system_admin)
def system_configuration(request):
    """System Configuration Settings"""
    if request.method == 'POST':
        form = SystemConfigForm(request.POST)
        if form.is_valid():
            # Save configuration settings
            # This would typically update a settings model or configuration file
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action_type='admin',
                description='Updated system configuration',
                portal_used='admin'
            )
            
            messages.success(request, 'System configuration updated successfully!')
            return redirect('system_configuration')
    else:
        # Load current configuration
        initial_data = {
            'check_in_window': 24,
            'booking_deadline': 2,
            'max_baggage_weight': 30,
            'loyalty_points_rate': 1.0,
            'default_currency': 'USD',
            'maintenance_mode': False,
        }
        form = SystemConfigForm(initial=initial_data)
    
    # Current system data
    system_stats = {
        'total_aircraft': Aircraft.objects.count(),
        'total_gates': Gate.objects.count(),
        'active_staff': Staff.objects.filter(is_active=True).count(),
        'total_flights_today': Flight.objects.filter(departure_time__date=date.today()).count(),
    }
    
    context = {
        'form': form,
        'system_stats': system_stats,
    }
    return render(request, 'admin/system_configuration.html', context)

@user_passes_test(is_system_admin)
def integration_monitor(request):
    """Integration Health Monitor"""
    # Simulate integration status
    integrations = [
        {
            'name': 'Payment Gateway (Stripe)',
            'status': 'operational',
            'last_response': '145ms',
            'uptime': '99.9%',
            'last_check': timezone.now(),
            'errors_24h': 0
        },
        {
            'name': 'Weather Service API',
            'status': 'operational',
            'last_response': '89ms',
            'uptime': '99.8%',
            'last_check': timezone.now(),
            'errors_24h': 2
        },
        {
            'name': 'Air Traffic Control Feed',
            'status': 'warning',
            'last_response': '1200ms',
            'uptime': '97.5%',
            'last_check': timezone.now() - timedelta(minutes=5),
            'errors_24h': 15
        },
        {
            'name': 'Baggage Handling System',
            'status': 'operational',
            'last_response': '200ms',
            'uptime': '99.5%',
            'last_check': timezone.now(),
            'errors_24h': 1
        },
        {
            'name': 'Ground Transportation API',
            'status': 'error',
            'last_response': 'timeout',
            'uptime': '89.2%',
            'last_check': timezone.now() - timedelta(minutes=15),
            'errors_24h': 45
        }
    ]
    
    # Recent integration logs
    integration_logs = [
        {
            'timestamp': timezone.now() - timedelta(minutes=1),
            'system': 'Payment Gateway',
            'event': 'Transaction processed',
            'status': 'success'
        },
        {
            'timestamp': timezone.now() - timedelta(minutes=3),
            'system': 'Weather Service',
            'event': 'Weather data updated',
            'status': 'success'
        },
        {
            'timestamp': timezone.now() - timedelta(minutes=5),
            'system': 'ATC Feed',
            'event': 'Connection timeout',
            'status': 'error'
        }
    ]
    
    context = {
        'integrations': integrations,
        'integration_logs': integration_logs,
    }
    return render(request, 'admin/integration_monitor.html', context)

@user_passes_test(is_system_admin)
def audit_log(request):
    """Audit Log Viewer"""
    logs = AuditLog.objects.all().order_by('-timestamp')
    
    # Filter by action type
    action_type = request.GET.get('action_type')
    if action_type:
        logs = logs.filter(action_type=action_type)
    
    # Filter by user
    user_id = request.GET.get('user')
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    # Filter by portal
    portal = request.GET.get('portal')
    if portal:
        logs = logs.filter(portal_used=portal)
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        logs = logs.filter(timestamp__gte=start_date)
    if end_date:
        logs = logs.filter(timestamp__lte=end_date)
    
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique users for filter dropdown
    users = User.objects.filter(
        id__in=AuditLog.objects.values_list('user_id', flat=True).distinct()
    ).order_by('username')
    
    context = {
        'page_obj': page_obj,
        'logs': page_obj,
        'action_types': AuditLog.ACTION_TYPES,
        'users': users,
        'portal_choices': UserProfile.PORTAL_CHOICES,
    }
    return render(request, 'admin/audit_log.html', context)

@user_passes_test(is_system_admin)
def system_metrics(request):
    """System Performance Metrics"""
    # Get date range
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    
    # Generate or retrieve metrics
    metrics = []
    current_date = start_date
    while current_date <= end_date:
        # Get or create metrics for this date
        metric, created = FlightOperationsMetrics.objects.get_or_create(
            date=current_date,
            defaults={
                'total_flights': Flight.objects.filter(departure_time__date=current_date).count(),
                'total_passengers': Booking.objects.filter(
                    flight__departure_time__date=current_date,
                    status__in=['confirmed', 'checked_in']
                ).count(),
                'revenue': sum(
                    booking.total_amount for booking in Booking.objects.filter(
                        flight__departure_time__date=current_date,
                        payment_status=True
                    )
                ),
            }
        )
        metrics.append(metric)
        current_date += timedelta(days=1)
    
    # Calculate summary statistics
    total_revenue = sum(m.revenue for m in metrics)
    total_flights = sum(m.total_flights for m in metrics)
    total_passengers = sum(m.total_passengers for m in metrics)
    avg_load_factor = sum(m.gate_utilization for m in metrics) / len(metrics) if metrics else 0
    
    context = {
        'metrics': metrics,
        'start_date': start_date,
        'end_date': end_date,
        'total_revenue': total_revenue,
        'total_flights': total_flights,
        'total_passengers': total_passengers,
        'avg_load_factor': avg_load_factor,
    }
    return render(request, 'admin/system_metrics.html', context)

@user_passes_test(is_system_admin)
def database_backup(request):
    """Database Backup and Maintenance"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'backup':
            # Simulate backup creation
            backup_name = f"backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}.sql"
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action_type='admin',
                description=f'Created database backup: {backup_name}',
                portal_used='admin'
            )
            
            messages.success(request, f'Database backup created successfully: {backup_name}')
        
        elif action == 'optimize':
            # Simulate database optimization
            AuditLog.objects.create(
                user=request.user,
                action_type='admin',
                description='Performed database optimization',
                portal_used='admin'
            )
            
            messages.success(request, 'Database optimization completed successfully!')
        
        return redirect('database_backup')
    
    # Recent backups (simulated)
    recent_backups = [
        {
            'name': 'backup_20250829_120000.sql',
            'size': '125 MB',
            'created': timezone.now() - timedelta(hours=12),
            'type': 'Automatic'
        },
        {
            'name': 'backup_20250828_120000.sql',
            'size': '122 MB',
            'created': timezone.now() - timedelta(days=1, hours=12),
            'type': 'Automatic'
        },
        {
            'name': 'backup_manual_20250827.sql',
            'size': '119 MB',
            'created': timezone.now() - timedelta(days=2),
            'type': 'Manual'
        }
    ]
    
    # Database statistics
    db_stats = {
        'total_size': '1.2 GB',
        'table_count': 15,
        'total_records': 50000,
        'last_backup': timezone.now() - timedelta(hours=12),
        'backup_status': 'Automatic backups enabled'
    }
    
    context = {
        'recent_backups': recent_backups,
        'db_stats': db_stats,
    }
    return render(request, 'admin/database_backup.html', context)
