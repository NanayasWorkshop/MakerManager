"""
Views for displaying job details.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from workshop_app.models import Job, JobMaterial, Machine, StaffSettings
from workshop_app.utils.barcode_utils import generate_qr_code

@login_required
def job_detail(request, job_id):
    """Display detail view for a specific job"""
    job = get_object_or_404(Job, job_id=job_id)
    
    # Get materials used for this job
    materials = JobMaterial.objects.filter(job=job).order_by('-date_used')
    
    # Get machines currently in use for this job
    current_machines = Machine.objects.filter(current_job=job)
    
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
