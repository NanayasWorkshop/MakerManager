"""
Views for displaying job details.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages

from workshop_app.models import Job, JobMaterial, Machine, StaffSettings
from workshop_app.models.job_time_tracking import JobTimeTracking
from workshop_app.utils.barcode_utils import generate_qr_code

@login_required
def job_detail(request, job_id):
    """Display detail view for a specific job"""
    job = get_object_or_404(Job, job_id=job_id)
    
    # Get materials used for this job
    materials = JobMaterial.objects.filter(job=job).order_by('-date_used')
    
    # Get machines currently in use for this job
    current_machines = Machine.objects.filter(current_job=job)
    
    # Get time logs for this job
    time_logs = JobTimeTracking.objects.filter(job=job).order_by('-start_time')
    
    # Calculate total time spent on this job
    total_seconds = sum(log.duration.total_seconds() for log in time_logs)
    total_hours = total_seconds / 3600
    
    # Check if this is the active job for the current user
    try:
        staff_settings = StaffSettings.objects.get(user=request.user)
        is_active_job = staff_settings.active_job == job if staff_settings.active_job else False
    except StaffSettings.DoesNotExist:
        is_active_job = False
    
    context = {
        'job': job,
        'materials': materials,
        'current_machines': current_machines,
        'is_active_job': is_active_job,
        'time_logs': time_logs,
        'total_hours': round(total_hours, 2),
    }
    
    return render(request, 'jobs/detail.html', context)

@login_required
def job_detail_by_pk(request, pk):
    """Display detail view for a job using its primary key (database ID)"""
    job = get_object_or_404(Job, pk=pk)
    
    # Get materials used for this job
    materials = JobMaterial.objects.filter(job=job).order_by('-date_used')
    
    # Get machines currently in use for this job
    current_machines = Machine.objects.filter(current_job=job)
    
    # Get time logs for this job
    time_logs = JobTimeTracking.objects.filter(job=job).order_by('-start_time')
    
    # Calculate total time spent on this job
    total_seconds = sum(log.duration.total_seconds() for log in time_logs)
    total_hours = total_seconds / 3600
    
    # Check if this is the active job for the current user
    try:
        staff_settings = StaffSettings.objects.get(user=request.user)
        is_active_job = staff_settings.active_job == job if staff_settings.active_job else False
    except StaffSettings.DoesNotExist:
        is_active_job = False
    
    context = {
        'job': job,
        'materials': materials,
        'current_machines': current_machines,
        'is_active_job': is_active_job,
        'time_logs': time_logs,
        'total_hours': round(total_hours, 2),
    }
    
    return render(request, 'jobs/detail.html', context)

@login_required
def get_job_qr_code(request, job_id):
    """Generate and return QR code for a job"""
    job = get_object_or_404(Job, job_id=job_id)
    
    # Generate QR code
    qr_code_url = generate_qr_code(job.job_id)
    
    return JsonResponse({
        'success': True,
        'job_name': job.project_name,
        'qr_code_url': qr_code_url
    })
