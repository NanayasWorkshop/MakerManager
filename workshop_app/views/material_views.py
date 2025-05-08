from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.db.models import Q
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db import transaction, connection
from django.conf import settings
import os
from decimal import Decimal

from workshop_app.models import (
    Material, MaterialCategory, MaterialType, 
    MaterialTransaction, JobMaterial, StaffSettings,
    MaterialAttachment, AttachmentType
)
from workshop_app.forms import MaterialForm, MaterialFilterForm, MaterialTransactionForm

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
    
    # Get material images directly using raw SQL - filter for attachment_type_id = 3 (Product)
    material_images = {}
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ma.material_id, ma.file 
            FROM workshop_app_materialattachment ma 
            WHERE ma.attachment_type_id = 3 
            ORDER BY ma.upload_date DESC
        """)
        rows = cursor.fetchall()
        
        for material_id, file_path in rows:
            if file_path:
                # Create a full URL for the image using MEDIA_URL
                media_url = settings.MEDIA_URL.rstrip('/')
                full_url = f"{media_url}/{file_path}"
                material_images[material_id] = full_url
    
    context = {
        'materials': materials,
        'categories': categories,
        'material_types': material_types,
        'material_images': material_images,
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
        form = MaterialForm(request.POST)
        if form.is_valid():
            # Save but don't commit to set additional fields
            material = form.save(commit=False)
            
            # Generate a unique material ID
            material_type = material.material_type
            category_code = material_type.category.code
            type_code = material_type.code
            
            # Count existing materials of this type + 1
            count = Material.objects.filter(
                material_type__category__code=category_code,
                material_type__code=type_code
            ).count() + 1
            
            # Generate ID as CATEG-TYPE-XXXXX
            material.material_id = f"{category_code}-{type_code}-{count:05d}"
            
            # Set creator
            material.created_by = request.user
            
            # Check if minimum stock level is set for alert
            if material.minimum_stock_level and material.current_stock <= material.minimum_stock_level:
                material.minimum_stock_alert = True
            
            # Save the material
            material.save()
            
            # Record initial stock as a purchase transaction
            if material.current_stock > 0:
                MaterialTransaction.objects.create(
                    material=material,
                    quantity=material.current_stock,
                    transaction_type='purchase',
                    transaction_date=timezone.now(),
                    job_reference='Initial Stock',
                    operator_name=request.user.get_full_name() or request.user.username,
                    notes='Initial stock on creation'
                )
            
            messages.success(request, f'Material "{material.name}" has been added successfully')
            return redirect('material_detail', material_id=material.material_id)
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = MaterialForm()
    
    context = {
        'form': form,
        'categories': categories,
        'material_types': material_types,
    }
    
    return render(request, 'materials/add.html', context)

@login_required
def edit_material(request, material_id):
    """Show form and handle editing a material"""
    material = get_object_or_404(Material, material_id=material_id)
    
    # Get categories and types for dropdowns
    categories = MaterialCategory.objects.all().order_by('name')
    material_types = MaterialType.objects.all().order_by('name')
    
    # Get attachment types for dropdowns
    attachment_types = AttachmentType.objects.all().order_by('name')
    
    # Get existing attachments
    attachments = MaterialAttachment.objects.filter(material=material).order_by('-upload_date')
    
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            # Check if stock has changed
            old_stock = material.current_stock
            
            # Save the form
            material = form.save()
            
            # Update minimum stock alert status
            if material.minimum_stock_level and material.current_stock <= material.minimum_stock_level:
                material.minimum_stock_alert = True
            else:
                material.minimum_stock_alert = False
            material.save()
            
            # If stock has changed, record an adjustment transaction
            new_stock = material.current_stock
            if old_stock != new_stock:
                change = new_stock - old_stock
                MaterialTransaction.objects.create(
                    material=material,
                    quantity=abs(change),
                    transaction_type='adjustment',
                    transaction_date=timezone.now(),
                    job_reference='Manual Adjustment',
                    operator_name=request.user.get_full_name() or request.user.username,
                    notes=f'Manual stock adjustment from {old_stock} to {new_stock}'
                )
            
            # Handle attachment upload if present
            attachment_type_id = request.POST.get('attachment_type')
            attachment_description = request.POST.get('attachment_description', '')
            attachment_file = request.FILES.get('attachment_file')
            custom_type = request.POST.get('custom_type', '')
            
            if attachment_type_id and attachment_file:
                try:
                    # If custom type is selected, use None for attachment_type
                    if attachment_type_id == 'custom':
                        attachment_type = None
                    else:
                        attachment_type = AttachmentType.objects.get(id=attachment_type_id)
                    
                    # Create new attachment
                    attachment = MaterialAttachment.objects.create(
                        material=material,
                        attachment_type=attachment_type,
                        custom_type=custom_type if attachment_type_id == 'custom' else '',
                        description=attachment_description,
                        file=attachment_file,
                        uploaded_by=request.user
                    )
                    
                    messages.success(request, f'Material "{material.name}" has been updated with new attachment')
                except Exception as e:
                    messages.error(request, f'Error adding attachment: {str(e)}')
            else:
                messages.success(request, f'Material "{material.name}" has been updated')
            
            return redirect('material_detail', material_id=material.material_id)
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = MaterialForm(instance=material)
    
    context = {
        'material': material,
        'form': form,
        'categories': categories,
        'material_types': material_types,
        'attachment_types': attachment_types,
        'attachments': attachments,
        'is_edit': True
    }
    
    return render(request, 'materials/edit.html', context)

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
def get_material_qr_code(request, material_id):
    """Generate and return QR code for a material"""
    material = get_object_or_404(Material, material_id=material_id)
    
    # Generate QR code
    from workshop_app.utils.barcode_utils import generate_qr_code
    qr_code_url = generate_qr_code(material.material_id)
    
    return JsonResponse({
        'success': True,
        'material_name': material.name,
        'qr_code_url': qr_code_url
    })

@login_required
def material_history(request, material_id):
    """Display complete transaction history for a material"""
    material = get_object_or_404(Material, material_id=material_id)
    
    # Get all transactions for this material
    transactions = MaterialTransaction.objects.filter(
        material=material
    ).order_by('-transaction_date')
    
    # Get job uses for this material
    job_uses = JobMaterial.objects.filter(
        material=material
    ).order_by('-date_used')
    
    context = {
        'material': material,
        'transactions': transactions,
        'job_uses': job_uses
    }
    
    return render(request, 'materials/history.html', context)

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

@login_required
def delete_material_attachment(request, material_id, attachment_id):
    """Delete a material attachment"""
    material = get_object_or_404(Material, material_id=material_id)
    attachment = get_object_or_404(MaterialAttachment, id=attachment_id, material=material)
    
    try:
        # Delete the file from storage
        if attachment.file:
            if os.path.isfile(attachment.file.path):
                os.remove(attachment.file.path)
        
        # Delete the database record
        attachment.delete()
        
        messages.success(request, 'Attachment deleted successfully')
    except Exception as e:
        messages.error(request, f'Error deleting attachment: {str(e)}')
    
    return redirect('edit_material', material_id=material_id)
