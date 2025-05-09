"""
API endpoints for material management.
"""
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone

from workshop_app.models import StaffSettings
from workshop_app.models.job_time_tracking import JobTimeTracking


@login_required
def get_active_job(request):
    """API endpoint to get the user's active job"""
    try:
        settings = StaffSettings.objects.get(user=request.user)
        active_job = settings.active_job
        
        # Get active time tracking info if available
        active_time_tracking = JobTimeTracking.get_active_entry(request.user)
        is_tracking = active_time_tracking is not None and active_time_tracking.job == active_job
        
        if active_job:
            return JsonResponse({
                'has_active_job': True,
                'job_id': active_job.job_id,
                'job_name': active_job.project_name,
                'is_tracking': is_tracking,
                'tracking_elapsed': active_time_tracking.elapsed_time if is_tracking else None
            })
        else:
            return JsonResponse({
                'has_active_job': False,
                'is_tracking': False
            })
    except StaffSettings.DoesNotExist:
        return JsonResponse({
            'has_active_job': False,
            'is_tracking': False
        })


@login_required
@require_POST
def clear_active_job(request):
    """API endpoint to clear the user's active job and set personal job as active"""
    try:
        settings = StaffSettings.objects.get(user=request.user)
        
        # Stop any active time tracking for the current job
        active_time_tracking = JobTimeTracking.get_active_entry(request.user)
        if active_time_tracking:
            active_time_tracking.end_time = timezone.now()
            active_time_tracking.notes += "\nAuto-stopped when clearing active job."
            active_time_tracking.save()
        
        # If personal job exists, set it as active
        if settings.personal_job:
            settings.active_job = settings.personal_job
            settings.active_since = timezone.now()
            settings.save()
            return JsonResponse({
                'success': True,
                'message': 'Active job set to your personal job',
                'job_name': settings.personal_job.project_name
            })
        # Otherwise, just clear the active job
        else:
            settings.clear_active_job()
            return JsonResponse({
                'success': True,
                'message': 'Active job cleared successfully',
                'no_personal_job': True
            })
    except StaffSettings.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'No staff settings found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_POST
def start_timer(request):
    """API endpoint to start time tracking for the active job"""
    try:
        settings = StaffSettings.objects.get(user=request.user)
        active_job = settings.active_job
        
        if not active_job:
            return JsonResponse({
                'success': False,
                'error': 'No active job found'
            })
        
        # Check if already tracking
        active_tracking = JobTimeTracking.get_active_entry(request.user)
        if active_tracking and active_tracking.job == active_job:
            return JsonResponse({
                'success': True,
                'message': 'Already tracking time for this job',
                'tracking_id': active_tracking.id,
                'job_name': active_job.project_name,
                'start_time': active_tracking.start_time.isoformat(),
                'elapsed_time': active_tracking.elapsed_time
            })
        
        # Start new time tracking
        notes = request.POST.get('notes', '')
        time_entry = JobTimeTracking.start_tracking(
            job=active_job,
            user=request.user,
            notes=notes
        )
        
        # Update the job's start date if not set
        if not active_job.start_date:
            active_job.start_date = timezone.now().date()
            active_job.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Timer started for job: {active_job.project_name}',
            'tracking_id': time_entry.id,
            'job_name': active_job.project_name,
            'start_time': time_entry.start_time.isoformat(),
            'elapsed_time': '0m 0s'
        })
    except StaffSettings.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'No staff settings found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_POST
def stop_timer(request):
    """API endpoint to stop time tracking for the current job"""
    try:
        # Get active time tracking
        active_tracking = JobTimeTracking.get_active_entry(request.user)
        
        if not active_tracking:
            return JsonResponse({
                'success': False,
                'error': 'No active time tracking found'
            })
        
        # Get notes from the form
        notes = request.POST.get('notes', '')
        
        # Stop time tracking with improved notes
        if notes:
            # Store the work notes instead of generic messages
            active_tracking = JobTimeTracking.stop_tracking(request.user, notes)
        else:
            # If no notes provided, use a generic message
            active_tracking = JobTimeTracking.stop_tracking(request.user, "Stopped from dashboard")
        
        # Calculate duration
        duration = active_tracking.duration
        hours = duration.total_seconds() / 3600
        
        return JsonResponse({
            'success': True,
            'message': f'Timer stopped for job: {active_tracking.job.project_name}',
            'tracking_id': active_tracking.id,
            'job_name': active_tracking.job.project_name,
            'start_time': active_tracking.start_time.isoformat(),
            'end_time': active_tracking.end_time.isoformat(),
            'duration': active_tracking.elapsed_time,
            'hours_worked': round(hours, 2)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_POST
def edit_time_tracking_notes(request, tracking_id):
    """API endpoint to edit notes for a completed time tracking entry"""
    try:
        # Get the time tracking entry
        time_entry = JobTimeTracking.objects.get(id=tracking_id, user=request.user)
        
        # Check if this entry belongs to the current user
        if time_entry.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'You do not have permission to edit this time entry'
            })
            
        # Check if the entry is completed (has end time)
        if not time_entry.end_time:
            return JsonResponse({
                'success': False,
                'error': 'Cannot edit notes for active time tracking entries'
            })
        
        # Update the notes
        new_notes = request.POST.get('notes', '')
        time_entry.notes = new_notes
        time_entry.save()
        
        # Format notes for display with line breaks
        formatted_notes = new_notes.replace('\n', '<br>') if new_notes else '-'
        
        return JsonResponse({
            'success': True,
            'message': 'Time tracking notes updated successfully',
            'tracking_id': time_entry.id,
            'updated_notes': formatted_notes
        })
    except JobTimeTracking.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Time tracking entry not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
