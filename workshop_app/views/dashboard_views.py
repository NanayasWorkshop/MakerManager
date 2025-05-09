from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q

from workshop_app.models import Job, Machine, Material, StaffSettings, JobStatus
from workshop_app.models.job_time_tracking import JobTimeTracking

@login_required
def dashboard(request):
    """Display the main dashboard"""
    
    # Get the active job for the current user
    try:
        staff_settings = StaffSettings.objects.get(user=request.user)
        active_job = staff_settings.active_job
        personal_job = staff_settings.personal_job
        
        # Get active time tracking if any
        active_time_tracking = None
        if active_job:
            active_time_tracking = JobTimeTracking.get_active_entry(request.user)
        
        # If no personal job exists, create one now
        if not personal_job:
            # Get a default status
            status = JobStatus.objects.filter(name='Personal').first()
            if not status:
                status = JobStatus.objects.first()
                
            # Create a System Personal Account
            personal_job = Job.objects.create(
                job_id=f"PER-{request.user.username.upper()}",
                project_name=f"Personal Account - {request.user.get_full_name() or request.user.username}",
                project_type='PER',  # Use personal type
                description="System account for unassigned work and materials",
                priority='low',
                status=status,
                status_text=status.name if status else "New",
                created_by=request.user,
                owner=request.user,
                created_date=timezone.now(),
                percent_complete=0
            )
            
            # Update staff settings
            staff_settings.personal_job = personal_job
            staff_settings.save()
            
    except StaffSettings.DoesNotExist:
        active_job = None
        personal_job = None
        active_time_tracking = None
        
        # Create staff settings
        StaffSettings.objects.create(user=request.user)
        # Reload the page to get the new settings with personal job
        return redirect('dashboard')
        
    # Get recent jobs for the user
    recent_jobs = Job.objects.filter(
        Q(created_by=request.user) | Q(owner=request.user)
    ).order_by('-created_date')[:5]
    
    # Get available machines the user is certified for
    available_machines = []
    try:
        # If user has an operator profile, show machines they're certified for
        operator = request.user.operator
        available_machines = Machine.objects.filter(
            status='available',
            certified_operators=operator
        )[:5]
    except:
        # If no operator profile, just show available machines
        available_machines = Machine.objects.filter(status='available')[:5]
    
    # Get low stock materials
    low_stock_materials = Material.objects.filter(minimum_stock_alert=True)[:5]
    
    context = {
        'active_job': active_job,
        'personal_job': personal_job,
        'recent_jobs': recent_jobs,
        'available_machines': available_machines,
        'low_stock_materials': low_stock_materials,
        'active_time_tracking': active_time_tracking,
    }
    
    return render(request, 'dashboard/index.html', context)

@login_required
@require_POST
def activate_job_by_id(request):
    """Handle activation of a job by manually entering its ID"""
    job_id = request.POST.get('job_id', '').strip()
    
    if not job_id:
        messages.error(request, 'Please enter a job ID.')
        return redirect('dashboard')
    
    try:
        # Find the job
        job = get_object_or_404(Job, job_id=job_id)
        
        # Set the job as active
        staff_settings, created = StaffSettings.objects.get_or_create(user=request.user)
        staff_settings.set_active_job(job)
        
        messages.success(request, f'Job "{job.project_name}" has been set as your active job.')
    except Job.DoesNotExist:
        messages.error(request, f'No job found with ID {job_id}')
    except Exception as e:
        messages.error(request, f'Error activating job: {str(e)}')
    
    return redirect('dashboard')

@login_required
@require_POST
def activate_personal_job(request):
    """Handle activation of the user's personal job"""
    try:
        staff_settings = StaffSettings.objects.get(user=request.user)
        personal_job = staff_settings.personal_job
        
        if personal_job:
            staff_settings.set_active_job(personal_job)
            message = f'Personal job "{personal_job.project_name}" has been set as active.'
            success = True
        else:
            message = "You don't have a personal job configured."
            success = False
            
        return {
            'success': success,
            'message': message
        }
    except StaffSettings.DoesNotExist:
        return {
            'success': False,
            'error': 'Staff settings not found'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
