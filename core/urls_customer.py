# Customer Portal URLs
from django.urls import path
from . import views_customer

app_name = 'customer'

urlpatterns = [
    # Dashboard and Home
    path('', views_customer.customer_dashboard, name='dashboard'),
    
    # Flight Search and Booking
    path('flights/', views_customer.flight_search, name='flight_search'),
    path('flights/<int:flight_id>/', views_customer.flight_detail_booking, name='flight_detail'),
    path('book/<int:flight_id>/', views_customer.make_booking, name='make_booking'),
    
    # Booking Management
    path('my-bookings/', views_customer.my_bookings, name='my_bookings'),
    path('booking/<str:booking_reference>/', views_customer.booking_detail, name='booking_detail'),
    
    # Check-in Process
    path('checkin/<str:booking_reference>/', views_customer.online_checkin, name='online_checkin'),
    path('boarding-pass/<str:booking_reference>/', views_customer.boarding_pass, name='boarding_pass'),
    
    # Flight Status
    path('flight-status/', views_customer.live_flight_status, name='flight_status'),
    
    # Loyalty Program
    path('loyalty/', views_customer.loyalty_program, name='loyalty_program'),
    
    # Help Center
    path('help/', views_customer.help_center, name='help_center'),
]
