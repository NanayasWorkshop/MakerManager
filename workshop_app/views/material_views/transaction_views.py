# workshop_app/views/material_views/transaction_views.py

"""
Views for material transactions (withdrawals, returns, and restocks).
"""
from decimal import Decimal, InvalidOperation
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction

from workshop_app.models import Material, MaterialTransaction, JobMaterial, StaffSettings
from workshop_app.forms import MaterialRestockForm
from workshop_app.utils.price_utils import calculate_weighted_average_price


@login_required
@require_POST
def withdraw_material(request, material_id):
    """Process material withdrawal using raw SQL where needed"""
    material = get_object_or_404(Material, material_id=material_id)
    
    # Get form data
    try:
        quantity = Decimal(request.POST.get('quantity', '0'))  # Convert directly to Decimal
        notes = request.POST.get('notes', '')
    except (ValueError, InvalidOperation):  # Handle Decimal conversion errors
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
    
    if quantity > material.current_stock:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': f'Not enough stock available. Current stock: {material.current_stock} {material.unit_of_measurement}'
            })
        messages.error(request, f'Not enough stock available. Current stock: {material.current_stock} {material.unit_of_measurement}')
        return redirect('material_detail', material_id=material_id)
    
    # Get active job
    try:
        staff_settings = StaffSettings.objects.get(user=request.user)
        active_job = staff_settings.active_job
    except StaffSettings.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'No active job set. Please activate a job before withdrawing material.'
            })
        messages.error(request, 'No active job set. Please activate a job before withdrawing material.')
        return redirect('material_detail', material_id=material_id)
    
    if not active_job:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'No active job set. Please activate a job before withdrawing material.'
            })
        messages.error(request, 'No active job set. Please activate a job before withdrawing material.')
        return redirect('material_detail', material_id=material_id)
    
    try:
        # Start transaction to ensure consistency
        with transaction.atomic():
            # Update material stock - Already using Decimal type from conversion above
            material.current_stock -= quantity
            
            # Check if we need to set minimum stock alert
            if material.minimum_stock_level and material.current_stock <= material.minimum_stock_level:
                material.minimum_stock_alert = True
            
            material.save()
            
            # Create transaction record - using only the fields that exist in your database
            transaction_record = MaterialTransaction.objects.create(
                material=material,
                quantity=quantity,
                transaction_type='withdrawal',
                transaction_date=timezone.now(),
                job_reference=active_job.job_id,
                operator_name=request.user.get_full_name() or request.user.username,
                notes=notes
            )
            
            # Use raw SQL to create the JobMaterial record
            # This bypasses Django's model validation
            from django.db import connection
            with connection.cursor() as cursor:
                # Get next ID value (PostgreSQL would use SERIAL, SQLite is different)
                cursor.execute("SELECT MAX(id) FROM workshop_app_jobmaterial")
                max_id = cursor.fetchone()[0]
                new_id = (max_id or 0) + 1
                
                # Format date_used for SQL
                date_used = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Format unit_price for SQL (None handling)
                unit_price_str = f"'{material.price_per_unit}'" if material.price_per_unit is not None else "NULL"
                
                # Execute the INSERT with known columns
                sql = f"""
                INSERT INTO workshop_app_jobmaterial (
                    id, job_id, material_id, quantity, date_used, added_by, 
                    result, notes, unit_price, usage_status
                ) VALUES (
                    {new_id}, {active_job.id}, {material.id}, '{quantity}', '{date_used}', 
                    '{request.user.get_full_name() or request.user.username}', 'active', 
                    '{notes.replace("'", "''")}', {unit_price_str}, 'active'
                )
                """
                cursor.execute(sql)
            
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
    """Process material return using raw SQL where needed"""
    material = get_object_or_404(Material, material_id=material_id)
    
    # Get form data
    try:
        quantity = Decimal(request.POST.get('quantity', '0'))  # Convert directly to Decimal
        notes = request.POST.get('notes', '')
    except (ValueError, InvalidOperation):  # Handle Decimal conversion errors
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
            # Update material stock - Already using Decimal type from conversion above
            material.current_stock += quantity
            
            # Check if we need to clear minimum stock alert
            if material.minimum_stock_level and material.current_stock > material.minimum_stock_level:
                material.minimum_stock_alert = False
            
            material.save()
            
            # Create transaction record - using only the fields that exist in your database
            transaction_record = MaterialTransaction.objects.create(
                material=material,
                quantity=quantity,
                transaction_type='return',
                transaction_date=timezone.now(),
                job_reference=active_job.job_id if active_job else 'N/A',
                operator_name=request.user.get_full_name() or request.user.username,
                notes=notes
            )
            
            # If there's an active job, create a negative job material entry using raw SQL
            if active_job:
                from django.db import connection
                with connection.cursor() as cursor:
                    # Get next ID value
                    cursor.execute("SELECT MAX(id) FROM workshop_app_jobmaterial")
                    max_id = cursor.fetchone()[0]
                    new_id = (max_id or 0) + 1
                    
                    # Format date_used for SQL
                    date_used = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Format unit_price for SQL (None handling)
                    unit_price_str = f"'{material.price_per_unit}'" if material.price_per_unit is not None else "NULL"
                    
                    # Execute the INSERT
                    sql = f"""
                    INSERT INTO workshop_app_jobmaterial (
                        id, job_id, material_id, quantity, date_used, added_by, 
                        result, notes, unit_price, usage_status
                    ) VALUES (
                        {new_id}, {active_job.id}, {material.id}, '{-quantity}', '{date_used}', 
                        '{request.user.get_full_name() or request.user.username}', 'returned', 
                        '{notes.replace("'", "''")}', {unit_price_str}, 'returned'
                    )
                    """
                    cursor.execute(sql)
            
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
def restock_material_form(request, material_id):
    """Show form for restocking material"""
    material = get_object_or_404(Material, material_id=material_id)
    
    if request.method == 'POST':
        form = MaterialRestockForm(request.POST, request.FILES)
        if form.is_valid():
            return process_restock(request, material, form)
    else:
        # Pre-fill with material's current info
        initial_data = {
            'supplier_name': material.supplier_name,
            'purchase_date': timezone.now().date(),
        }
        form = MaterialRestockForm(initial=initial_data)
    
    context = {
        'material': material,
        'form': form,
    }
    
    return render(request, 'materials/restock.html', context)


@login_required
@require_POST
def restock_material(request, material_id):
    """Process material restock from modal form"""
    material = get_object_or_404(Material, material_id=material_id)
    
    # Get form data
    try:
        quantity = Decimal(request.POST.get('quantity', '0'))
        purchase_price = Decimal(request.POST.get('purchase_price', '0'))
        supplier_name = request.POST.get('supplier_name', '')
        purchase_date_str = request.POST.get('purchase_date', '')
        notes = request.POST.get('notes', '')
        
        # Optional update fields
        update_location = request.POST.get('update_location') == 'on'
        new_location = request.POST.get('new_location', '')
        update_min_stock = request.POST.get('update_min_stock') == 'on'
        new_min_stock = request.POST.get('new_min_stock', '')
        
        # Validate required fields
        if quantity <= 0:
            raise ValueError('Quantity must be greater than zero')
        
        if purchase_price <= 0:
            raise ValueError('Purchase price must be greater than zero')
            
        if not supplier_name:
            raise ValueError('Supplier name is required')
            
        # Get purchase date
        if purchase_date_str:
            from datetime import datetime
            purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
        else:
            purchase_date = timezone.now().date()
            
    except (ValueError, TypeError, InvalidOperation) as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
        messages.error(request, f'Invalid data provided: {str(e)}')
        return redirect('material_detail', material_id=material_id)
    
    try:
        # Start database transaction
        with transaction.atomic():
            # Calculate new weighted average price
            old_price = material.price_per_unit or Decimal('0.00')
            new_avg_price = calculate_weighted_average_price(
                material.current_stock,
                old_price,
                quantity,
                purchase_price
            )
            
            # Update material stock
            material.current_stock += quantity
            
            # Update price per unit with weighted average
            material.price_per_unit = new_avg_price
            
            # Update location if requested
            if update_location and new_location:
                material.location_in_workshop = new_location
                
            # Update minimum stock level if requested
            if update_min_stock and new_min_stock:
                try:
                    min_stock = Decimal(new_min_stock)
                    material.minimum_stock_level = min_stock
                    
                    # Update minimum stock alert status
                    if material.current_stock <= min_stock:
                        material.minimum_stock_alert = True
                    else:
                        material.minimum_stock_alert = False
                except:
                    pass
            else:
                # Check minimum stock alert with existing threshold
                if material.minimum_stock_level and material.current_stock > material.minimum_stock_level:
                    material.minimum_stock_alert = False
            
            material.save()
            
            # Create transaction record - using only the fields that exist in your database schema
            transaction_record = MaterialTransaction.objects.create(
                material=material,
                quantity=quantity,
                transaction_type='restock',
                transaction_date=timezone.now(),
                job_reference='Inventory Restock',
                operator_name=request.user.get_full_name() or request.user.username,
                notes=f"Purchased at ${purchase_price} per unit from {supplier_name} on {purchase_date}. {notes}"
            )
            
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Successfully restocked {quantity} {material.unit_of_measurement} of {material.name}',
                'new_stock': str(material.current_stock),
                'new_price': str(material.price_per_unit)
            })
            
        messages.success(request, f'Successfully restocked {quantity} {material.unit_of_measurement} of {material.name}')
        return redirect('material_detail', material_id=material_id)
            
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
            
        messages.error(request, f'Error processing restock: {str(e)}')
        return redirect('material_detail', material_id=material_id)


def process_restock(request, material, form):
    """Process form-based material restock"""
    try:
        # Extract data from form
        quantity = form.cleaned_data['quantity']
        purchase_price = form.cleaned_data['purchase_price']
        supplier_name = form.cleaned_data['supplier_name']
        purchase_date = form.cleaned_data['purchase_date']
        notes = form.cleaned_data['notes']
        invoice = form.cleaned_data.get('invoice')
        update_location = form.cleaned_data.get('update_location', False)
        new_location = form.cleaned_data.get('new_location', '')
        update_min_stock = form.cleaned_data.get('update_min_stock', False)
        new_min_stock = form.cleaned_data.get('new_min_stock')
        
        # Start database transaction
        with transaction.atomic():
            # Calculate new weighted average price
            old_price = material.price_per_unit or Decimal('0.00')
            new_avg_price = calculate_weighted_average_price(
                material.current_stock,
                old_price,
                quantity,
                purchase_price
            )
            
            # Update material stock
            material.current_stock += quantity
            
            # Update price per unit with weighted average
            material.price_per_unit = new_avg_price
            
            # Update location if requested
            if update_location and new_location:
                material.location_in_workshop = new_location
                
            # Update minimum stock level if requested
            if update_min_stock and new_min_stock:
                material.minimum_stock_level = new_min_stock
                
                # Update minimum stock alert status
                if material.current_stock <= new_min_stock:
                    material.minimum_stock_alert = True
                else:
                    material.minimum_stock_alert = False
            else:
                # Check minimum stock alert with existing threshold
                if material.minimum_stock_level and material.current_stock > material.minimum_stock_level:
                    material.minimum_stock_alert = False
            
            material.save()
            
            # Create transaction record - including only the fields that exist in your schema
            transaction_record = MaterialTransaction.objects.create(
                material=material,
                quantity=quantity,
                transaction_type='restock',
                transaction_date=timezone.now(),
                job_reference='Inventory Restock',
                operator_name=request.user.get_full_name() or request.user.username,
                notes=f"Purchased at ${purchase_price} per unit from {supplier_name} on {purchase_date}. {notes}"
            )
            
        messages.success(request, f'Successfully restocked {quantity} {material.unit_of_measurement} of {material.name}')
        return redirect('material_detail', material_id=material.material_id)
            
    except Exception as e:
        messages.error(request, f'Error processing restock: {str(e)}')
        return redirect('restock_material_form', material_id=material.material_id)
