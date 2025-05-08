"""
Views for creating and editing machines.
"""
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from workshop_app.models import Machine, MachineType
from workshop_app.forms import MachineForm
from workshop_app.utils.barcode_utils import generate_qr_code

@login_required
def add_machine(request):
    """Show form and handle adding a new machine"""
    # Get machine types for dropdowns
    machine_types = MachineType.objects.all().order_by('name')
    
    if request.method == 'POST':
        # Process form submission
        form = MachineForm(request.POST)
        if form.is_valid():
            # Save but don't commit to set additional fields
            machine = form.save(commit=False)
            
            # Generate a unique machine ID
            machine_type = machine.machine_type
            type_code = machine_type.code
            
            # Count existing machines of this type + 1
            count = Machine.objects.filter(
                machine_type__code=type_code
            ).count() + 1
            
            # Generate ID as MC-TYPE-XXXXX
            machine.machine_id = f"MC-{type_code}-{count:05d}"
            
            # Generate QR code
            machine.qr_code = generate_qr_code(machine.machine_id)
            
            # Save the machine
            machine.save()
            
            messages.success(request, f'Machine "{machine.name}" has been added successfully')
            return redirect('machine_detail', machine_id=machine.machine_id)
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = MachineForm()
    
    context = {
        'form': form,
        'machine_types': machine_types,
    }
    
    return render(request, 'machines/add.html', context)

@login_required
def edit_machine(request, machine_id):
    """Show form and handle editing a machine"""
    machine = get_object_or_404(Machine, machine_id=machine_id)
    
    # Get machine types for dropdowns
    machine_types = MachineType.objects.all().order_by('name')
    
    if request.method == 'POST':
        form = MachineForm(request.POST, instance=machine)
        if form.is_valid():
            # Save the form
            machine = form.save()
            
            messages.success(request, f'Machine "{machine.name}" has been updated')
            return redirect('machine_detail', machine_id=machine.machine_id)
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = MachineForm(instance=machine)
    
    context = {
        'machine': machine,
        'form': form,
        'machine_types': machine_types,
        'is_edit': True
    }
    
    return render(request, 'machines/edit.html', context)
