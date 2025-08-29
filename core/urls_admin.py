# System Administration Portal URLs
from django.urls import path
from . import views_admin

app_name = 'admin_portal'

urlpatterns = [
    # Dashboard
    path('', views_admin.admin_dashboard, name='dashboard'),
    
    # User Management
    path('users/', views_admin.user_management, name='user_management'),
    path('users/create/', views_admin.create_user, name='create_user'),
    path('users/<int:user_id>/edit/', views_admin.edit_user, name='edit_user'),
    
    # Roles and Permissions
    path('roles/', views_admin.roles_permissions, name='roles_permissions'),
    
    # System Configuration
    path('config/', views_admin.system_configuration, name='system_configuration'),
    
    # Integration Monitoring
    path('integrations/', views_admin.integration_monitor, name='integration_monitor'),
    
    # Audit Log
    path('audit/', views_admin.audit_log, name='audit_log'),
    
    # System Metrics
    path('metrics/', views_admin.system_metrics, name='system_metrics'),
    
    # Database Management
    path('database/', views_admin.database_backup, name='database_backup'),
]
