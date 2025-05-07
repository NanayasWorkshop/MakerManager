from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.db.models import Q
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db import transaction

from workshop_app.models import (
    Material, MaterialCategory, MaterialType, 
    MaterialTransaction, JobMaterial, StaffSettings
)

@login_required
def material_list(request):
    """List materials with search and filter capabilities"""
    # Get filter parameters from request
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    type_id = request.GET.get('type', '')
    stock_filter = request.GET.get('stock', '')
    sort_param = request.GET.get('sort', 'name')
    
    # Start with all materials
    materials = Material.objects.all()
    
    # Apply search filter
    if search_query:
        materials = materials.filter(
            Q(name__icontains=search_query) |
            Q(material_id__icontains=search_query) |
            Q(supplier_name__icontains=search_query) |
            Q(brand_name__icontains=search_query) |
            Q(location_in_workshop__icontains=search_query)
        )
    
    # Apply category filter
    if category_id:
        materials = materials.filter(material_type__category_id=category_id)
    
    # Apply type filter
    if type_id:
        materials = materials.filter(material_type_id=type_id)
    
    # Apply stock filter
    if stock_filter == 'low':
        materials = materials.filter(minimum_stock_alert=True)
    elif stock_filter == 'out':
        materials = materials.filter(current_stock__lte=0)
    elif stock_filter == 'available':
        materials = materials.filter(current_stock__gt=0)
    
    # Apply sorting
    if sort_param == 'name':
        materials = materials.order_by('name')
    elif sort_param == 'id':
        materials = materials.order_by('material_id')
    elif sort_param == 'stock':
        materials = materials.order_by('current_stock')
    elif sort_param == 'category':
        materials = materials.order_by('material_type__category__name', 'material_type__name')
    elif sort_param == 'location':
        materials = materials.order_by('location_in_workshop')
    
    # Get categories and types for filter dropdowns
    categories = MaterialCategory.objects.all().order_by('name')
    material_types = MaterialType.objects.all().order_by('name')
    
    context = {
        'materials': materials,
        'categories': categories,
        'material_types': material_types,
    }
    
    return render(request, 'materials/list.html', context)

@login_required
def material_detail(request, material_id):
    """Display detail view for a specific material"""
    material = get_object_or_404(Material, material_id=material_id)
    
    # Get transaction history
    transactions = MaterialTransaction.objects.filter(
        material=material
    ).order_by('-transaction_date')[:10]
    
    # Get active job for association
    try:
        settings = StaffSettings.objects.get(user=request.user)
        active_job = settings.active_job
    except StaffSettings.DoesNotExist:
        active_job = None
    
    context = {
        'material': material,
        'transactions': transactions,
        'active_job': active_job,
    }
    
    return render(request, 'materials/detail.html', context)

@login_required
def add_material(request):
    """Show form and handle adding a new material"""
    # Get categories and types for dropdowns
    categories = MaterialCategory.objects.all().order_by('name')
    material_types = MaterialType.objects.all().order_by('name')
    
    if request.method == 'POST':
        # Process form submission
        # (Will be implemented in detail when we create the form)
        pass
    
    context = {
        'categories': categories,
        'material_types': material_types,
    }
    
    return render(request, 'materials/add.html', context)

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
            # Update material stock
            material.current_stock -= quantity
            
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
            
        messages.success(request, f'Successfully withdrew {quantity} {material.unit_of_measurement} of {material.name}')
        return redirect('material_detail', material_id=material_id)
            
    except Exception as e:
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
        messages.error(request, 'Invalid quantity provided')
        return redirect('material_detail', material_id=material_id)
    
    # Validate quantity
    if quantity <= 0:
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
            # Update material stock
            material.current_stock += quantity
            
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
            
        messages.success(request, f'Successfully returned {quantity} {material.unit_of_measurement} of {material.name}')
        return redirect('material_detail', material_id=material_id)
            
    except Exception as e:
        messages.error(request, f'Error processing return: {str(e)}')
        return redirect('material_detail', material_id=material_id)

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
