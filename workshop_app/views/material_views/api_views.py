"""
API endpoints for material management.
"""
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone

from workshop_app.models import StaffSettings


@login_required
def get_active_job(request):
    """API endpoint to get the user's active job"""
    try:
        settings = StaffSettings.objects.get(user=request.user)
        active_job = settings.active_job
        
        if active_job:
            return JsonResponse({
                'has_active_job': True,
                'job_id': active_job.job_id,
                'job_name': active_job.project_name
            })
        else:
            return JsonResponse({
                'has_active_job': False
            })
    except StaffSettings.DoesNotExist:
        return JsonResponse({
            'has_active_job': False
        })


@login_required
@require_POST
def clear_active_job(request):
    """API endpoint to clear the user's active job and set personal job as active"""
    try:
        settings = StaffSettings.objects.get(user=request.user)
        
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
        
        # Here you would implement actual time tracking logic
        # This is a placeholder implementation
        
        # Update the job
        active_job.start_date = active_job.start_date or timezone.now().date()
        active_job.save()
        
        return JsonResponse({
            'success': True,
            'job_name': active_job.project_name,
            'message': f'Timer started for job: {active_job.project_name}'
        })
    except StaffSettings.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'No active job found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
