from django.urls import path
from workshop_app.views import auth_views, dashboard_views, scanning_views, material_views, machine_views

urlpatterns = [
    # Authentication URLs
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('profile/', auth_views.profile_view, name='profile'),
    
    # Dashboard URL
    path('', dashboard_views.dashboard, name='dashboard'),
    path('activate-job/', dashboard_views.activate_job_by_id, name='activate_job_by_id'),
    
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
    path('materials/add/', material_views.add_material, name='add_material'),
    path('materials/<str:material_id>/', material_views.material_detail, name='material_detail'),
    path('materials/<str:material_id>/withdraw/', material_views.withdraw_material, name='withdraw_material'),
    path('materials/<str:material_id>/return/', material_views.return_material, name='return_material'),
    path('materials/<str:material_id>/qr-code/', material_views.get_material_qr_code, name='material_qr_code'),
    path('materials/<str:material_id>/history/', material_views.material_history, name='material_history'),
    path('materials/<str:material_id>/edit/', material_views.edit_material, name='edit_material'),
    
    # Machine URLs
    path('machines/<str:machine_id>/start-usage/', machine_views.start_machine_usage, name='start_machine_usage'),
    path('machines/<str:machine_id>/stop-usage/', machine_views.stop_machine_usage, name='stop_machine_usage'),
    
    # API endpoints
    path('api/active-job/', material_views.get_active_job, name='api_active_job'),
    path('api/clear-active-job/', material_views.clear_active_job, name='clear_active_job'),
    path('api/start-timer/', material_views.start_timer, name='start_timer'),
]

