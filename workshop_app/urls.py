from django.urls import path
from workshop_app.views import auth_views, dashboard_views, scanning_views, material_views

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
    
    # Material URLs
    path('materials/', material_views.material_list, name='material_list'),
    path('materials/add/', material_views.add_material, name='add_material'),  # Move this above the detail view
    path('materials/<str:material_id>/', material_views.material_detail, name='material_detail'),
    path('materials/<str:material_id>/withdraw/', material_views.withdraw_material, name='withdraw_material'),
    path('materials/<str:material_id>/return/', material_views.return_material, name='return_material'),
    
    # API endpoints
    path('api/active-job/', material_views.get_active_job, name='api_active_job'),
]
