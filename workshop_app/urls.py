# workshop_app/urls.py

from django.urls import path
from workshop_app.views import auth_views, dashboard_views, scanning_views, material_views
from workshop_app.views.machine_views import (
    machine_list,
    machine_detail,
    machine_usage_history,
    get_machine_qr_code,
    add_machine,
    edit_machine,
    start_machine_usage,
    stop_machine_usage
)

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
    path('scan/not-found/', scanning_views.not_found_view, name='scan_not_found'),
    
    # Material URLs
    path('materials/', material_views.material_list, name='material_list'),
    path('materials/add/', material_views.add_material, name='add_material'),
    path('materials/<str:material_id>/', material_views.material_detail, name='material_detail'),
    path('materials/<str:material_id>/withdraw/', material_views.withdraw_material, name='withdraw_material'),
    path('materials/<str:material_id>/return/', material_views.return_material, name='return_material'),
    path('materials/<str:material_id>/restock/', material_views.restock_material_form, name='restock_material_form'),
    path('materials/<str:material_id>/restock-action/', material_views.restock_material, name='restock_material'),
    path('materials/<str:material_id>/qr-code/', material_views.get_material_qr_code, name='material_qr_code'),
    path('materials/<str:material_id>/history/', material_views.material_history, name='material_history'),
    path('materials/<str:material_id>/edit/', material_views.edit_material, name='edit_material'),
    path('materials/<str:material_id>/attachments/<int:attachment_id>/delete/', 
         material_views.delete_material_attachment, 
         name='delete_material_attachment'),
    
    # Machine URLs
    path('machines/', machine_list, name='machine_list'),
    path('machines/add/', add_machine, name='add_machine'),
    path('machines/<str:machine_id>/', machine_detail, name='machine_detail'),
    path('machines/<str:machine_id>/edit/', edit_machine, name='edit_machine'),
    path('machines/<str:machine_id>/usage-history/', machine_usage_history, name='machine_usage_history'),
    path('machines/<str:machine_id>/start-usage/', start_machine_usage, name='start_machine_usage'),
    path('machines/<str:machine_id>/stop-usage/', stop_machine_usage, name='stop_machine_usage'),
    path('machines/<str:machine_id>/qr-code/', get_machine_qr_code, name='machine_qr_code'),
    
    # API endpoints
    path('api/active-job/', material_views.get_active_job, name='api_active_job'),
    path('api/clear-active-job/', material_views.clear_active_job, name='clear_active_job'),
    path('api/start-timer/', material_views.start_timer, name='start_timer'),
]
