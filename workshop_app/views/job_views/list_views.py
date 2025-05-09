"""
Views for job listing and filtering.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from workshop_app.models import Job, JobStatus, StaffSettings

@login_required
def job_list(request):
    """List jobs with search and filter capabilities"""
    # Get filter parameters from request
    search_query = request.GET.get('search', '')
    status_id = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    
    # Start with all jobs
    jobs = Job.objects.all()
    
    # Apply search filter
    if search_query:
        jobs = jobs.filter(
            Q(project_name__icontains=search_query) |
            Q(job_id__icontains=search_query) |
            Q(client__name__icontains=search_query)
        )
    
    # Apply status filter
    if status_id:
        jobs = jobs.filter(status_id=status_id)
    
    # Apply priority filter
    if priority_filter:
        jobs = jobs.filter(priority=priority_filter)
    
    # Get job statuses for filter dropdowns
    job_statuses = JobStatus.objects.all().order_by('order')
    
    # Check if user has active job
    try:
        staff_settings = StaffSettings.objects.get(user=request.user)
        active_job_id = staff_settings.active_job.id if staff_settings.active_job else None
    except StaffSettings.DoesNotExist:
        active_job_id = None
    
    context = {
        'jobs': jobs,
        'job_statuses': job_statuses,
        'active_job_id': active_job_id,
    }
    
    return render(request, 'jobs/list.html', context)
