from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import datetime, date
import random
import string

# Enhanced User Profile for Role-Based Access
class UserProfile(models.Model):
    PORTAL_CHOICES = [
        ('customer', 'Customer Portal'),
        ('airline', 'Airline Operations'),
        ('crew', 'Crew Portal'),
        ('admin', 'System Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    portal_access = models.CharField(max_length=20, choices=PORTAL_CHOICES, default='customer')
    phone_number = models.CharField(max_length=17, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    loyalty_number = models.CharField(max_length=20, blank=True)
    loyalty_tier = models.CharField(max_length=20, default='Silver')
    loyalty_points = models.PositiveIntegerField(default=0)
    preferred_language = models.CharField(max_length=10, default='en')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.portal_access}"

# Gate Management System
class Gate(models.Model):
    GATE_STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('cleaning', 'Being Cleaned'),
    ]
    
    gate_number = models.CharField(max_length=10, unique=True)
    terminal = models.CharField(max_length=10)
    gate_type = models.CharField(max_length=20, default='Standard')  # Standard, Wide-body, Regional
    capacity = models.PositiveIntegerField(default=200)
    status = models.CharField(max_length=20, choices=GATE_STATUS_CHOICES, default='available')
    current_flight = models.ForeignKey('Flight', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_gate')
    next_available = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Gate {self.gate_number} - Terminal {self.terminal}"

# Aircraft Fleet Management
class Aircraft(models.Model):
    AIRCRAFT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('grounded', 'Grounded'),
        ('retired', 'Retired'),
    ]
    
    registration = models.CharField(max_length=10, unique=True)
    aircraft_type = models.CharField(max_length=50)
    manufacturer = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    total_seats = models.PositiveIntegerField()
    business_seats = models.PositiveIntegerField(default=0)
    economy_seats = models.PositiveIntegerField()
    year_manufactured = models.PositiveIntegerField()
    last_maintenance = models.DateField()
    next_maintenance = models.DateField()
    status = models.CharField(max_length=20, choices=AIRCRAFT_STATUS_CHOICES, default='active')
    current_location = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.registration} - {self.aircraft_type}"

class Flight(models.Model):
    FLIGHT_STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('boarding', 'Boarding'),
        ('departed', 'Departed'),
        ('arrived', 'Arrived'),
        ('delayed', 'Delayed'),
        ('cancelled', 'Cancelled'),
    ]
    
    flight_number = models.CharField(max_length=10, unique=True)
    airline = models.CharField(max_length=100)
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, null=True, blank=True)
    departure_city = models.CharField(max_length=100)
    arrival_city = models.CharField(max_length=100)
    departure_airport = models.CharField(max_length=10, default='UNK')  # IATA code
    arrival_airport = models.CharField(max_length=10, default='UNK')    # IATA code
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    actual_departure = models.DateTimeField(null=True, blank=True)
    actual_arrival = models.DateTimeField(null=True, blank=True)
    aircraft_type = models.CharField(max_length=50)
    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()
    business_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    economy_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Backward compatibility
    status = models.CharField(max_length=20, choices=FLIGHT_STATUS_CHOICES, default='scheduled')
    gate = models.ForeignKey(Gate, on_delete=models.SET_NULL, null=True, blank=True)
    gate_number = models.CharField(max_length=10, blank=True, null=True)
    boarding_time = models.DateTimeField(null=True, blank=True)
    check_in_opens = models.DateTimeField(null=True, blank=True)
    weather_conditions = models.CharField(max_length=100, blank=True)
    delay_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.flight_number} - {self.departure_city} to {self.arrival_city}"
    
    @property
    def is_delayed(self):
        if self.actual_departure and self.departure_time:
            return self.actual_departure > self.departure_time
        return False
    
    @property
    def delay_minutes(self):
        if self.is_delayed:
            return int((self.actual_departure - self.departure_time).total_seconds() / 60)
        return 0
    
    @property
    def boarding_status(self):
        from django.utils import timezone
        now = timezone.now()
        if self.boarding_time and now >= self.boarding_time:
            return 'boarding'
        elif self.status == 'departed':
            return 'departed'
        else:
            return 'not_boarding'
    
    class Meta:
        ordering = ['departure_time']

# Enhanced Passenger Model for Customer Portal
class Passenger(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    TITLE_CHOICES = [
        ('Mr', 'Mr.'),
        ('Mrs', 'Mrs.'),
        ('Ms', 'Ms.'),
        ('Dr', 'Dr.'),
        ('Prof', 'Prof.'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, default='Mr')
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    passport_number = models.CharField(max_length=20, unique=True)
    passport_expiry = models.DateField(default=date(2030, 1, 1))
    nationality = models.CharField(max_length=50)
    address = models.TextField()
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=17, blank=True)
    dietary_preferences = models.CharField(max_length=100, blank=True)
    mobility_assistance = models.BooleanField(default=False)
    frequent_flyer_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.title} {self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.title} {self.first_name} {self.last_name}"
    
    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

# Enhanced Booking Model for Customer Portal
class Booking(models.Model):
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Flight Completed'),
    ]
    
    CLASS_CHOICES = [
        ('economy', 'Economy'),
        ('business', 'Business'),
        ('first', 'First Class'),
    ]
    
    booking_reference = models.CharField(max_length=10, unique=True)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    seat_class = models.CharField(max_length=20, choices=CLASS_CHOICES, default='economy')
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxes_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    special_requests = models.TextField(blank=True, null=True)
    meal_preference = models.CharField(max_length=50, blank=True)
    seat_preference = models.CharField(max_length=50, blank=True)
    baggage_allowance = models.PositiveIntegerField(default=20)  # kg
    extra_baggage = models.PositiveIntegerField(default=0)  # kg
    insurance_opted = models.BooleanField(default=False)
    insurance_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.booking_reference} - {self.passenger.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        super().save(*args, **kwargs)
    
    @property
    def can_check_in(self):
        from django.utils import timezone
        # Check-in opens 24 hours before departure
        check_in_time = self.flight.departure_time - timezone.timedelta(hours=24)
        return timezone.now() >= check_in_time and self.status == 'confirmed'
    
    @property
    def check_in_status(self):
        if hasattr(self, 'checkin'):
            return self.checkin.status
        return 'not_checked_in'
    
    class Meta:
        unique_together = ['flight', 'seat_number']

# Enhanced Staff Model for Crew Portal
class Staff(models.Model):
    ROLE_CHOICES = [
        ('pilot', 'Pilot'),
        ('copilot', 'Co-Pilot'),
        ('cabin_crew', 'Cabin Crew'),
        ('ground_staff', 'Ground Staff'),
        ('security', 'Security'),
        ('maintenance', 'Maintenance'),
        ('dispatcher', 'Flight Dispatcher'),
        ('gate_agent', 'Gate Agent'),
        ('customer_service', 'Customer Service'),
        ('baggage_handler', 'Baggage Handler'),
        ('admin', 'Administrator'),
    ]
    
    QUALIFICATION_STATUS = [
        ('current', 'Current'),
        ('expired', 'Expired'),
        ('pending', 'Renewal Pending'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.CharField(max_length=100)
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=17, blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    license_expiry = models.DateField(null=True, blank=True)
    medical_certificate = models.CharField(max_length=50, blank=True)
    medical_expiry = models.DateField(null=True, blank=True)
    qualification_status = models.CharField(max_length=20, choices=QUALIFICATION_STATUS, default='current')
    flight_hours = models.PositiveIntegerField(default=0)
    last_training = models.DateField(null=True, blank=True)
    next_training_due = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"
    
    @property
    def needs_training(self):
        if self.next_training_due:
            return date.today() >= self.next_training_due
        return False
    
    @property
    def license_valid(self):
        if self.license_expiry:
            return date.today() < self.license_expiry
        return True
    
    class Meta:
        verbose_name_plural = "Staff"

# Crew Scheduling System
class CrewAssignment(models.Model):
    ASSIGNMENT_STATUS = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    role_on_flight = models.CharField(max_length=50)  # Captain, First Officer, etc.
    assignment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ASSIGNMENT_STATUS, default='scheduled')
    check_in_time = models.DateTimeField(null=True, blank=True)
    briefing_completed = models.BooleanField(default=False)
    post_flight_report = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.flight.flight_number}"
    
    class Meta:
        unique_together = ['staff', 'flight']

# Enhanced Check-in Model
class CheckIn(models.Model):
    CHECK_IN_STATUS_CHOICES = [
        ('checked_in', 'Checked In'),
        ('boarding_pass_issued', 'Boarding Pass Issued'),
        ('security_cleared', 'Security Cleared'),
        ('at_gate', 'At Gate'),
        ('boarded', 'Boarded'),
        ('no_show', 'No Show'),
    ]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(auto_now_add=True)
    boarding_time = models.DateTimeField(blank=True, null=True)
    gate_number = models.CharField(max_length=10)
    seat_number = models.CharField(max_length=10)
    baggage_weight = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    excess_baggage_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    boarding_pass_url = models.CharField(max_length=255, blank=True)
    qr_code = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=30, choices=CHECK_IN_STATUS_CHOICES, default='checked_in')
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    check_in_method = models.CharField(max_length=20, default='online')  # online, kiosk, counter
    special_assistance = models.TextField(blank=True)
    security_notes = models.TextField(blank=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Check-in for {self.booking.booking_reference}"
    
    @property
    def boarding_group(self):
        # Simple boarding group assignment based on seat class
        if self.booking.seat_class == 'first':
            return 'A'
        elif self.booking.seat_class == 'business':
            return 'B'
        else:
            return 'C'
    
    class Meta:
        verbose_name = "Check-In"
        verbose_name_plural = "Check-Ins"

# System Administration Models
class SystemAlert(models.Model):
    ALERT_TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    affected_system = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.alert_type.upper()}: {self.title}"
    
    class Meta:
        ordering = ['-created_at']

class AuditLog(models.Model):
    ACTION_TYPES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('booking', 'Booking Action'),
        ('checkin', 'Check-in Action'),
        ('admin', 'Admin Action'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    portal_used = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.action_type} - {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']

# Operational Dashboard Models
class FlightOperationsMetrics(models.Model):
    date = models.DateField(unique=True)
    total_flights = models.PositiveIntegerField(default=0)
    on_time_departures = models.PositiveIntegerField(default=0)
    delayed_flights = models.PositiveIntegerField(default=0)
    cancelled_flights = models.PositiveIntegerField(default=0)
    average_delay_minutes = models.PositiveIntegerField(default=0)
    total_passengers = models.PositiveIntegerField(default=0)
    passenger_satisfaction = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    gate_utilization = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    crew_utilization = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Metrics for {self.date}"
    
    @property
    def on_time_percentage(self):
        if self.total_flights > 0:
            return (self.on_time_departures / self.total_flights) * 100
        return 0
    
    class Meta:
        ordering = ['-date']
