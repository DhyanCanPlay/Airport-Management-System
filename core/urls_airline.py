# Airline Operations Portal URLs
from django.urls import path
from . import views_airline

app_name = 'airline'

urlpatterns = [
    # Operations Dashboard
    path('', views_airline.operations_dashboard, name='operations_dashboard'),
    
    # Flight Management
    path('flights/schedule/', views_airline.flight_scheduling, name='flight_scheduling'),
    
    # Gate Management
    path('gates/', views_airline.gate_management, name='gate_management'),
    
    # Passenger Assistance
    path('passenger-assistance/', views_airline.passenger_assistance, name='passenger_assistance'),
    
    # Turnaround Operations
    path('turnaround/', views_airline.turnaround_coordination, name='turnaround_coordination'),
    
    # Analytics and Reporting
    path('analytics/', views_airline.analytics_reporting, name='analytics_reporting'),
    
    # Live Flight Map
    path('flight-map/', views_airline.live_flight_map, name='live_flight_map'),
    
    # System Alerts
    path('alerts/', views_airline.system_alerts, name='system_alerts'),
    path('alerts/<int:alert_id>/resolve/', views_airline.resolve_alert, name='resolve_alert'),
]
