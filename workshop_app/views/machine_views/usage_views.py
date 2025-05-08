"""
Views for machine usage tracking.
"""
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal

from workshop_app.models import Machine, MachineUsage, StaffSettings

@login_required
@require_POST
def start_machine_usage(request, machine_id):
    """Start using a machine and associate with active job"""
    machine = get_object_or_404(Machine, machine_id=machine_id)
    
    # Check if machine is available
    if machine.status != 'available':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': f'Machine is not available (current status: {machine.get_status_display()})'
            })
        messages.error(request, f'Machine is not available (current status: {machine.get_status_display()})')
        return redirect('machine_detail', machine_id=machine_id)
    
    # Check if user is certified for this machine
    try:
        operator = request.user.operator
        is_certified = operator.is_certified_for(machine)
        
        if not is_certified:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'You are not certified to use this machine'
                })
            messages.error(request, 'You are not certified to use this machine')
            return redirect('machine_detail', machine_id=machine_id)
    except:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Operator profile not found'
            })
        messages.error(request, 'Operator profile not found')
        return redirect('machine_detail', machine_id=machine_id)
    
    # Get active job
    try:
        staff_settings = StaffSettings.objects.get(user=request.user)
        active_job = staff_settings.active_job
        
        if not active_job:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'No active job set. Please activate a job first.'
                })
            messages.error(request, 'No active job set. Please activate a job first.')
            return redirect('machine_detail', machine_id=machine_id)
    except StaffSettings.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'No staff settings found'
            })
        messages.error(request, 'No staff settings found')
        return redirect('machine_detail', machine_id=machine_id)
    
    # Get form data
    setup_time = int(request.POST.get('setup_time', 15))
    estimated_usage = int(request.POST.get('estimated_usage', 60))
    notes = request.POST.get('notes', '')
    
    try:
        # Create usage record
        usage = MachineUsage(
            machine=machine,
            start_time=timezone.now(),
            setup_time=setup_time,
            job_reference=active_job.job_id,
            operator_name=request.user.get_full_name() or request.user.username,
            notes=notes
        )
        
        # Calculate costs if rates are set
        if machine.setup_rate:
            usage.setup_cost = Decimal(setup_time / 60) * machine.setup_rate
        
        usage.save()
        
        # Update machine status
        machine.status = 'in_use'
        machine.current_job = active_job
        
        # Calculate reserved until time based on setup time and estimated usage
        reserved_minutes = setup_time + estimated_usage
        machine.reserved_until = timezone.now() + timezone.timedelta(minutes=reserved_minutes)
        
        machine.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'You are now using {machine.name}',
                'job_name': active_job.project_name
            })
            
        messages.success(request, f'You are now using {machine.name}')
        return redirect('machine_detail', machine_id=machine_id)
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
            
        messages.error(request, f'Error starting machine usage: {str(e)}')
        return redirect('machine_detail', machine_id=machine_id)

@login_required
@require_POST
def stop_machine_usage(request, machine_id):
    """Stop using a machine and record time and costs"""
    machine = get_object_or_404(Machine, machine_id=machine_id)
    
    # Check if machine is in use
    if machine.status != 'in_use':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': f'Machine is not in use (current status: {machine.get_status_display()})'
            })
        messages.error(request, f'Machine is not in use (current status: {machine.get_status_display()})')
        return redirect('machine_detail', machine_id=machine_id)
    
    # Get form data
    cleanup_time = int(request.POST.get('cleanup_time', 10))
    notes = request.POST.get('notes', '')
    
    try:
        # Find active usage record
        usage = MachineUsage.objects.filter(
            machine=machine,
            end_time__isnull=True
        ).latest('start_time')
        
        # Update usage record
        usage.end_time = timezone.now()
        usage.cleanup_time = cleanup_time
        
        # Calculate operation time in minutes
        operation_minutes = (usage.end_time - usage.start_time).total_seconds() / 60
        
        # Update notes if provided
        if notes:
            usage.notes += f"\n\nStop notes: {notes}"
        
        # Calculate costs if rates are set
        if machine.hourly_rate:
            usage.operation_cost = Decimal(operation_minutes / 60) * machine.hourly_rate
            
        if machine.cleanup_rate:
            usage.cleanup_cost = Decimal(cleanup_time / 60) * machine.cleanup_rate
            
        # Calculate total cost
        usage.total_cost = (usage.setup_cost or 0) + (usage.operation_cost or 0) + (usage.cleanup_cost or 0)
        
        usage.save()
        
        # Update machine status
        machine.status = 'available'
        machine.current_job = None
        machine.reserved_until = None
        machine.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'You have stopped using {machine.name}',
                'total_time': f'{int(operation_minutes)} minutes',
                'total_cost': f'${usage.total_cost:.2f}' if usage.total_cost else 'Not calculated'
            })
            
        messages.success(request, f'You have stopped using {machine.name}')
        return redirect('machine_detail', machine_id=machine_id)
            
    except MachineUsage.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'No active usage record found for this machine'
            })
            
        messages.error(request, 'No active usage record found for this machine')
        return redirect('machine_detail', machine_id=machine_id)
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
            
        messages.error(request, f'Error stopping machine usage: {str(e)}')
        return redirect('machine_detail', machine_id=machine_id)
