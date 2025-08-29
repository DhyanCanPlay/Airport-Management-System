from django.contrib import admin
from .models import Flight, Passenger, Booking, Staff, CheckIn

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['flight_number', 'airline', 'departure_city', 'arrival_city', 'departure_time', 'status', 'available_seats']
    list_filter = ['status', 'airline', 'departure_city', 'arrival_city']
    search_fields = ['flight_number', 'airline', 'departure_city', 'arrival_city']
    date_hierarchy = 'departure_time'
    ordering = ['departure_time']
    
    fieldsets = (
        ('Flight Information', {
            'fields': ('flight_number', 'airline', 'aircraft_type')
        }),
        ('Route', {
            'fields': ('departure_city', 'arrival_city', 'departure_time', 'arrival_time')
        }),
        ('Seating & Pricing', {
            'fields': ('total_seats', 'available_seats', 'price')
        }),
        ('Status & Gate', {
            'fields': ('status', 'gate_number')
        }),
    )

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone_number', 'nationality', 'age']
    list_filter = ['gender', 'nationality']
    search_fields = ['first_name', 'last_name', 'email', 'passport_number']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'gender')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone_number', 'address')
        }),
        ('Travel Documents', {
            'fields': ('passport_number', 'nationality')
        }),
    )

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'passenger', 'flight', 'seat_number', 'status', 'booking_date', 'total_amount']
    list_filter = ['status', 'payment_status', 'flight__departure_city', 'flight__arrival_city']
    search_fields = ['booking_reference', 'passenger__first_name', 'passenger__last_name', 'flight__flight_number']
    date_hierarchy = 'booking_date'
    raw_id_fields = ['passenger', 'flight']
    
    fieldsets = (
        ('Booking Details', {
            'fields': ('booking_reference', 'passenger', 'flight', 'seat_number')
        }),
        ('Payment & Status', {
            'fields': ('status', 'total_amount', 'payment_status')
        }),
        ('Additional Information', {
            'fields': ('special_requests',)
        }),
    )

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'role', 'department', 'hire_date', 'is_active']
    list_filter = ['role', 'department', 'is_active', 'hire_date']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id', 'user__email']
    date_hierarchy = 'hire_date'
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Employment Details', {
            'fields': ('employee_id', 'role', 'department', 'hire_date', 'salary')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'address')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ['booking', 'check_in_time', 'gate_number', 'seat_number', 'status', 'baggage_weight']
    list_filter = ['status', 'gate_number', 'check_in_time']
    search_fields = ['booking__booking_reference', 'booking__passenger__first_name', 'booking__passenger__last_name']
    date_hierarchy = 'check_in_time'
    raw_id_fields = ['booking', 'staff']
    
    fieldsets = (
        ('Check-In Information', {
            'fields': ('booking', 'check_in_time', 'status')
        }),
        ('Gate & Seating', {
            'fields': ('gate_number', 'seat_number', 'boarding_time')
        }),
        ('Baggage & Staff', {
            'fields': ('baggage_weight', 'staff', 'notes')
        }),
    )
