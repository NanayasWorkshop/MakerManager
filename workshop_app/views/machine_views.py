"""
Views for machine management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone

from workshop_app.models import Machine, StaffSettings

@login_required
@require_POST
def start_machine_usage(request, machine_id):
    """API endpoint to start using a machine"""
    machine = get_object_or_404(Machine, machine_id=machine_id)
    
    # Check if machine is available
    if machine.status != 'available':
        return JsonResponse({
            'success': False,
            'error': f'Machine is not available (current status: {machine.get_status_display()})'
        })
    
    # Check if user is certified for this machine
    try:
        operator = request.user.operator
        is_certified = operator.is_certified_for(machine)
        
        if not is_certified:
            return JsonResponse({
                'success': False,
                'error': 'You are not certified to use this machine'
            })
    except:
        return JsonResponse({
            'success': False,
            'error': 'Operator profile not found'
        })
    
    # Get active job
    try:
        staff_settings = StaffSettings.objects.get(user=request.user)
        active_job = staff_settings.active_job
        
        if not active_job:
            return JsonResponse({
                'success': False,
                'error': 'No active job set. Please activate a job first.'
            })
    except StaffSettings.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'No staff settings found'
        })
    
    # Get form data
    setup_time = request.POST.get('setup_time', 0)
    estimated_usage = request.POST.get('estimated_usage', 60)
    notes = request.POST.get('notes', '')
    
    try:
        # Update machine status
        machine.status = 'in_use'
        machine.current_job = active_job
        
        # Calculate reserved until time based on setup time and estimated usage
        reserved_minutes = int(setup_time) + int(estimated_usage)
        machine.reserved_until = timezone.now() + timezone.timedelta(minutes=reserved_minutes)
        
        machine.save()
        
        # Here you would log machine usage in a separate model
        # This is a placeholder for that functionality
        
        return JsonResponse({
            'success': True,
            'message': f'You are now using {machine.name}',
            'job_name': active_job.project_name
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@require_POST
def stop_machine_usage(request, machine_id):
    """API endpoint to stop using a machine"""
    machine = get_object_or_404(Machine, machine_id=machine_id)
    
    # Check if machine is in use
    if machine.status != 'in_use':
        return JsonResponse({
            'success': False,
            'error': f'Machine is not in use (current status: {machine.get_status_display()})'
        })
    
    # Check if machine is used by the active job of the current user
    try:
        staff_settings = StaffSettings.objects.get(user=request.user)
        active_job = staff_settings.active_job
        
        if not active_job or machine.current_job != active_job:
            return JsonResponse({
                'success': False,
                'error': 'This machine is not being used by your active job'
            })
    except StaffSettings.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'No staff settings found'
        })
    
    # Get form data
    cleanup_time = request.POST.get('cleanup_time', 0)
    notes = request.POST.get('notes', '')
    
    try:
        # Update machine status
        machine.status = 'available'
        machine.current_job = None
        machine.reserved_until = None
        machine.save()
        
        # Here you would finalize machine usage logging
        # This is a placeholder for that functionality
        
        return JsonResponse({
            'success': True,
            'message': f'You have stopped using {machine.name}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
