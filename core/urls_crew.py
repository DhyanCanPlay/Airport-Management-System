# Crew Portal URLs
from django.urls import path
from . import views_crew

app_name = 'crew'

urlpatterns = [
    # Dashboard
    path('', views_crew.crew_dashboard, name='dashboard'),
    
    # Roster Management
    path('roster/', views_crew.my_roster, name='my_roster'),
    
    # Flight Briefing
    path('briefing/<int:assignment_id>/', views_crew.flight_briefing, name='flight_briefing'),
    
    # Bidding and Swaps
    path('bidding/', views_crew.bidding_swaps, name='bidding_swaps'),
    
    # Qualifications
    path('qualifications/', views_crew.my_qualifications, name='my_qualifications'),
    
    # Post-Flight Reports
    path('report/<int:assignment_id>/', views_crew.post_flight_report, name='post_flight_report'),
    
    # Messages
    path('messages/', views_crew.crew_messages, name='messages'),
    
    # Training Center
    path('training/', views_crew.training_center, name='training_center'),
]
