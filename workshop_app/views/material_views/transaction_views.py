"""
Views for material transactions (withdrawals and returns).
"""
from decimal import Decimal
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction

from workshop_app.models import Material, MaterialTransaction, JobMaterial, StaffSettings


@login_required
@require_POST
def withdraw_material(request, material_id):
    """Process material withdrawal"""
    material = get_object_or_404(Material, material_id=material_id)
    
    # Get form data
    try:
        quantity = float(request.POST.get('quantity', 0))
        notes = request.POST.get('notes', '')
    except ValueError:
        messages.error(request, 'Invalid quantity provided')
        return redirect('material_detail', material_id=material_id)
    
    # Validate quantity
    if quantity <= 0:
        messages.error(request, 'Quantity must be greater than zero')
        return redirect('material_detail', material_id=material_id)
    
    if quantity > material.current_stock:
        messages.error(request, f'Not enough stock available. Current stock: {material.current_stock} {material.unit_of_measurement}')
        return redirect('material_detail', material_id=material_id)
    
    # Get active job
    try:
        staff_settings = StaffSettings.objects.get(user=request.user)
        active_job = staff_settings.active_job
    except StaffSettings.DoesNotExist:
        messages.error(request, 'No active job set. Please activate a job before withdrawing material.')
        return redirect('material_detail', material_id=material_id)
    
    if not active_job:
        messages.error(request, 'No active job set. Please activate a job before withdrawing material.')
        return redirect('material_detail', material_id=material_id)
    
    try:
        # Start transaction to ensure consistency
        with transaction.atomic():
            # Update material stock - Convert float to Decimal to prevent type errors
            material.current_stock -= Decimal(str(quantity))
            
            # Check if we need to set minimum stock alert
            if material.minimum_stock_level and material.current_stock <= material.minimum_stock_level:
                material.minimum_stock_alert = True
            
            material.save()
            
            # Create transaction record
            transaction_record = MaterialTransaction.objects.create(
                material=material,
                quantity=quantity,
                transaction_type='withdrawal',
                transaction_date=timezone.now(),
                job_reference=active_job.job_id,
                operator_name=request.user.get_full_name() or request.user.username,
                notes=notes
            )
            
            # Associate with job
            job_material = JobMaterial.objects.create(
                job=active_job,
                material=material,
                quantity=quantity,
                unit_price=material.price_per_unit,
                date_used=timezone.now(),
                added_by=request.user.get_full_name() or request.user.username,
                result='active',  # or other appropriate status
                notes=notes
            )
            
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Successfully withdrew {quantity} {material.unit_of_measurement} of {material.name}',
                'job_reference': active_job.job_id,
                'operator_name': request.user.get_full_name() or request.user.username
            })
            
        messages.success(request, f'Successfully withdrew {quantity} {material.unit_of_measurement} of {material.name}')
        return redirect('material_detail', material_id=material_id)
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
            
        messages.error(request, f'Error processing withdrawal: {str(e)}')
        return redirect('material_detail', material_id=material_id)


@login_required
@require_POST
def return_material(request, material_id):
    """Process material return"""
    material = get_object_or_404(Material, material_id=material_id)
    
    # Get form data
    try:
        quantity = float(request.POST.get('quantity', 0))
        notes = request.POST.get('notes', '')
    except ValueError:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Invalid quantity provided'
            })
        messages.error(request, 'Invalid quantity provided')
        return redirect('material_detail', material_id=material_id)
    
    # Validate quantity
    if quantity <= 0:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Quantity must be greater than zero'
            })
        messages.error(request, 'Quantity must be greater than zero')
        return redirect('material_detail', material_id=material_id)
    
    # Get active job (optional for returns)
    try:
        staff_settings = StaffSettings.objects.get(user=request.user)
        active_job = staff_settings.active_job
    except StaffSettings.DoesNotExist:
        active_job = None
    
    try:
        # Start transaction to ensure consistency
        with transaction.atomic():
            # Update material stock - Convert float to Decimal to prevent type errors
            material.current_stock += Decimal(str(quantity))
            
            # Check if we need to clear minimum stock alert
            if material.minimum_stock_level and material.current_stock > material.minimum_stock_level:
                material.minimum_stock_alert = False
            
            material.save()
            
            # Create transaction record
            transaction_record = MaterialTransaction.objects.create(
                material=material,
                quantity=quantity,
                transaction_type='return',
                transaction_date=timezone.now(),
                job_reference=active_job.job_id if active_job else 'N/A',
                operator_name=request.user.get_full_name() or request.user.username,
                notes=notes
            )
            
            # If there's an active job, we can create a negative job material entry
            if active_job:
                job_material = JobMaterial.objects.create(
                    job=active_job,
                    material=material,
                    quantity=-quantity,  # Negative to indicate return
                    unit_price=material.price_per_unit,
                    date_used=timezone.now(),
                    added_by=request.user.get_full_name() or request.user.username,
                    result='returned',
                    notes=notes
                )
            
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Successfully returned {quantity} {material.unit_of_measurement} of {material.name}',
                'job_reference': active_job.job_id if active_job else 'N/A',
                'operator_name': request.user.get_full_name() or request.user.username
            })
            
        messages.success(request, f'Successfully returned {quantity} {material.unit_of_measurement} of {material.name}')
        return redirect('material_detail', material_id=material_id)
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
            
        messages.error(request, f'Error processing return: {str(e)}')
        return redirect('material_detail', material_id=material_id)
