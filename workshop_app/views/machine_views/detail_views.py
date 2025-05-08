"""
Views for displaying machine details and history.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from workshop_app.models import Machine, MachineUsage, StaffSettings
from workshop_app.utils.barcode_utils import generate_qr_code

@login_required
def machine_detail(request, machine_id):
    """Display detail view for a specific machine"""
    machine = get_object_or_404(Machine, machine_id=machine_id)
    
    # Get recent usage history
    usage_history = MachineUsage.objects.filter(
        machine=machine
    ).order_by('-start_time')[:10]
    
    # Check if user is certified for this machine
    is_certified = False
    try:
        operator = request.user.operator
        is_certified = operator.is_certified_for(machine)
    except:
        pass
    
    # Get active job for association
    try:
        settings = StaffSettings.objects.get(user=request.user)
        active_job = settings.active_job
    except StaffSettings.DoesNotExist:
        active_job = None
    
    context = {
        'machine': machine,
        'usage_history': usage_history,
        'is_certified': is_certified,
        'active_job': active_job,
    }
    
    return render(request, 'machines/detail.html', context)

@login_required
def machine_usage_history(request, machine_id):
    """Display complete usage history for a machine"""
    machine = get_object_or_404(Machine, machine_id=machine_id)
    
    # Get all usage for this machine
    usage_history = MachineUsage.objects.filter(
        machine=machine
    ).order_by('-start_time')
    
    context = {
        'machine': machine,
        'usage_history': usage_history
    }
    
    return render(request, 'machines/usage_history.html', context)

@login_required
def get_machine_qr_code(request, machine_id):
    """Generate and return QR code for a machine"""
    machine = get_object_or_404(Machine, machine_id=machine_id)
    
    # Generate QR code
    qr_code_url = generate_qr_code(machine.machine_id)
    
    return JsonResponse({
        'success': True,
        'machine_name': machine.name,
        'qr_code_url': qr_code_url
    })
