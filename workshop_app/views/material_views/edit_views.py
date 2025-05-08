"""
Views for creating and editing materials.
"""
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from workshop_app.models import (
    Material, MaterialCategory, MaterialType, MaterialTransaction,
    MaterialAttachment, AttachmentType
)
from workshop_app.forms import MaterialForm


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
