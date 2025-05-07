from django.urls import path
from workshop_app.views import auth_views, dashboard_views, scanning_views

urlpatterns = [
    # Authentication URLs
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('profile/', auth_views.profile_view, name='profile'),
    
    # Dashboard URL
    path('', dashboard_views.dashboard, name='dashboard'),
    
    # Scanning URLs
    path('scan/', scanning_views.scan_view, name='scan'),
    path('scan/process/', scanning_views.process_scan, name='process_scan'),
    path('scan/history/', scanning_views.scan_history, name='scan_history'),
    path('scan/manual/', scanning_views.manual_entry, name='manual_entry'),
    path('scan/job/<str:job_id>/', scanning_views.scanned_job, name='scanned_job'),
    path('scan/material/<str:material_id>/', scanning_views.scanned_material, name='scanned_material'),
    path('scan/machine/<str:machine_id>/', scanning_views.scanned_machine, name='scanned_machine'),
]
