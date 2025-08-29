from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .views_customer import customer_dashboard

urlpatterns = [
    # Main page redirects to customer portal
    path('', customer_dashboard, name='home'),
    
    # Legacy/Main Views (backward compatibility)
    path('legacy-home/', views.home, name='legacy_home'),
    path('flights/', views.flight_list, name='flight_list'),
    path('flights/<int:flight_id>/', views.flight_detail, name='flight_detail'),
    
    # Portal-specific URLs
    path('customer/', include('core.urls_customer')),
    path('airline/', include('core.urls_airline')), 
    path('crew/', include('core.urls_crew')),
    path('admin-portal/', include('core.urls_admin')),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    
    # Legacy Staff-only URLs (backward compatibility)
    path('passengers/', views.passenger_list, name='passenger_list'),
    path('passengers/add/', views.passenger_create, name='passenger_create'),
    path('passengers/<int:passenger_id>/edit/', views.passenger_edit, name='passenger_edit'),
    
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/add/', views.booking_create, name='booking_create'),
    
    path('staff/', views.staff_list, name='staff_list'),
    
    path('checkins/', views.checkin_list, name='checkin_list'),
    path('checkins/add/', views.checkin_create, name='checkin_create'),
    
    path('reports/', views.reports, name='reports'),
    path('charts/<str:chart_type>/', views.generate_chart, name='generate_chart'),
]
