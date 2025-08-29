from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (Flight, Passenger, Booking, Staff, CheckIn, Gate, Aircraft, 
                    CrewAssignment, UserProfile)

class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = ['flight_number', 'airline', 'aircraft', 'departure_city', 'arrival_city', 
                 'departure_airport', 'arrival_airport', 'departure_time', 'arrival_time', 
                 'aircraft_type', 'total_seats', 'available_seats', 'economy_price', 
                 'business_price', 'status', 'gate']
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'flight_number': forms.TextInput(attrs={'class': 'form-control'}),
            'airline': forms.TextInput(attrs={'class': 'form-control'}),
            'departure_city': forms.TextInput(attrs={'class': 'form-control'}),
            'arrival_city': forms.TextInput(attrs={'class': 'form-control'}),
            'departure_airport': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IATA Code (e.g., JFK)'}),
            'arrival_airport': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IATA Code (e.g., LAX)'}),
            'aircraft_type': forms.TextInput(attrs={'class': 'form-control'}),
            'total_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'economy_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'business_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'aircraft': forms.Select(attrs={'class': 'form-control'}),
            'gate': forms.Select(attrs={'class': 'form-control'}),
        }

class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ['title', 'first_name', 'middle_name', 'last_name', 'email', 'phone_number', 
                 'date_of_birth', 'gender', 'passport_number', 'passport_expiry', 'nationality', 
                 'address', 'emergency_contact_name', 'emergency_contact_phone', 'dietary_preferences',
                 'mobility_assistance', 'frequent_flyer_number']
        widgets = {
            'title': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_expiry': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'dietary_preferences': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vegetarian, Halal, etc.'}),
            'mobility_assistance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'frequent_flyer_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['passenger', 'flight', 'seat_number', 'seat_class', 'meal_preference', 
                 'seat_preference', 'special_requests', 'insurance_opted']
        widgets = {
            'passenger': forms.Select(attrs={'class': 'form-control'}),
            'flight': forms.Select(attrs={'class': 'form-control'}),
            'seat_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 12A'}),
            'seat_class': forms.Select(attrs={'class': 'form-control'}),
            'meal_preference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vegetarian, Hindu, etc.'}),
            'seat_preference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Window, Aisle, etc.'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'insurance_opted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show flights that have available seats
        self.fields['flight'].queryset = Flight.objects.filter(available_seats__gt=0, status='scheduled')

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['user', 'employee_id', 'role', 'department', 'hire_date', 'salary', 
                 'phone_number', 'address', 'emergency_contact', 'emergency_phone',
                 'license_number', 'license_expiry', 'medical_certificate', 'medical_expiry',
                 'is_active']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'license_expiry': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'medical_certificate': forms.TextInput(attrs={'class': 'form-control'}),
            'medical_expiry': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CheckInForm(forms.ModelForm):
    class Meta:
        model = CheckIn
        fields = ['booking', 'gate_number', 'seat_number', 'baggage_weight', 'special_assistance', 'notes']
        widgets = {
            'booking': forms.Select(attrs={'class': 'form-control'}),
            'gate_number': forms.TextInput(attrs={'class': 'form-control'}),
            'seat_number': forms.TextInput(attrs={'class': 'form-control'}),
            'baggage_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'special_assistance': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show confirmed bookings that haven't been checked in yet
        from django.db.models import Q
        checked_in_bookings = CheckIn.objects.values_list('booking_id', flat=True)
        self.fields['booking'].queryset = Booking.objects.filter(
            status='confirmed'
        ).exclude(id__in=checked_in_bookings)

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

class FlightSearchForm(forms.Form):
    departure_city = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'From'})
    )
    arrival_city = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'To'})
    )
    departure_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    airline = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Airline'})
    )
    seat_class = forms.ChoiceField(
        choices=[('', 'Any Class'), ('economy', 'Economy'), ('business', 'Business'), ('first', 'First')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

# New forms for enhanced functionality
class GateAssignmentForm(forms.Form):
    flight = forms.ModelChoiceField(
        queryset=Flight.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    gate = forms.ModelChoiceField(
        queryset=Gate.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
class CrewAssignmentForm(forms.ModelForm):
    class Meta:
        model = CrewAssignment
        fields = ['staff', 'flight', 'role_on_flight']
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-control'}),
            'flight': forms.Select(attrs={'class': 'form-control'}),
            'role_on_flight': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Captain, First Officer, etc.'}),
        }

class PostFlightReportForm(forms.Form):
    flight_hours = forms.DecimalField(
        max_digits=5, 
        decimal_places=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
    )
    fuel_consumption = forms.DecimalField(
        max_digits=8, 
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    weather_conditions = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    turbulence_level = forms.ChoiceField(
        choices=[('none', 'None'), ('light', 'Light'), ('moderate', 'Moderate'), ('severe', 'Severe')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    passenger_incidents = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    technical_issues = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    report_content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'General flight report...'})
    )

class CrewAvailabilityForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    availability_type = forms.ChoiceField(
        choices=[('available', 'Available'), ('unavailable', 'Unavailable'), ('limited', 'Limited Availability')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

class UserManagementForm(forms.ModelForm):
    portal_access = forms.ChoiceField(
        choices=UserProfile.PORTAL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    loyalty_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class SystemConfigForm(forms.Form):
    # General Settings
    check_in_window = forms.IntegerField(
        label="Check-in Window (hours before departure)",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    booking_deadline = forms.IntegerField(
        label="Booking Deadline (hours before departure)",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    max_baggage_weight = forms.IntegerField(
        label="Maximum Baggage Weight (kg)",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    # Loyalty Program
    loyalty_points_rate = forms.DecimalField(
        label="Loyalty Points Rate (points per dollar)",
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    # System Settings
    default_currency = forms.ChoiceField(
        choices=[('USD', 'US Dollar'), ('EUR', 'Euro'), ('GBP', 'British Pound')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    maintenance_mode = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Email Settings
    email_notifications = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    sms_notifications = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
