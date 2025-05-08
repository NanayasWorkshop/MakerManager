"""
Views for handling scanning functionality
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from workshop_app.models import Job, Material, Machine, StaffSettings, ScanHistory
from workshop_app.utils.barcode_utils import determine_code_type, parse_code
from workshop_app.forms import ManualEntryForm

@login_required
def scan_view(request):
    """Main scanning interface"""
    # Get recent scans
    recent_scans = ScanHistory.objects.filter(user=request.user).order_by('-timestamp')[:5]
    
    context = {
        'recent_scans': recent_scans
    }
    
    return render(request, 'scanning/scan.html', context)

@login_required
@require_POST
def process_scan(request):
    """Process a scanned code"""
    code = request.POST.get('code', '')
    
    if not code:
        return JsonResponse({'success': False, 'error': 'No code provided'})
    
    # Parse the code to extract ID
    parsed_code = parse_code(code)
    
    # Attempt to determine the code type based on format
    scan_type = determine_code_type(parsed_code)
    
    # Process based on scan type
    if scan_type == 'job':
        return process_job_scan(request, parsed_code)
    elif scan_type == 'material':
        return process_material_scan(request, parsed_code)
    elif scan_type == 'machine':
        return process_machine_scan(request, parsed_code)
    else:
        # If the code type is unknown, try to find it in the database
        # by checking serial numbers and supplier SKUs
        return process_unknown_scan(request, parsed_code)

def process_unknown_scan(request, code):
    """
    Process a code that doesn't match our internal format patterns.
    Try to find it in the database as a serial number or supplier code.
    """
    # Try to find it as a material serial number or supplier SKU
    try:
        material = Material.objects.filter(
            Q(serial_number=code) | Q(supplier_sku=code)
        ).first()
        
        if material:
            # Record scan in history
            ScanHistory.objects.create(
                user=request.user,
                scan_type='material',
                code=code,
                item_id=material.material_id,
                item_name=material.name
            )
            
            # Return material details and redirect URL
            return JsonResponse({
                'success': True,
                'type': 'material',
                'id': material.material_id,
                'name': material.name,
                'redirect_url': f'/scan/material/{material.material_id}/'
            })
    except Exception as e:
        pass  # Continue to machine check if material lookup fails
    
    # Try to find it as a machine serial number
    try:
        machine = Machine.objects.filter(serial_number=code).first()
        
        if machine:
            # Record scan in history
            ScanHistory.objects.create(
                user=request.user,
                scan_type='machine',
                code=code,
                item_id=machine.machine_id,
                item_name=machine.name
            )
            
            # Return machine details and redirect URL
            return JsonResponse({
                'success': True,
                'type': 'machine',
                'id': machine.machine_id,
                'name': machine.name,
                'redirect_url': f'/scan/machine/{machine.machine_id}/'
            })
    except Exception as e:
        pass  # Continue to error response if machine lookup fails
    
    # If we get here, we couldn't find the code in our database
    return JsonResponse({
        'success': False,
        'error': 'Unrecognized code. This doesn\'t match any known job, material, or machine.',
        'scanned_code': code  # Add the scanned code to the response
    })

def process_job_scan(request, job_id):
    """Process a job code scan"""
    try:
        # Look up job by ID
        job = Job.objects.get(job_id=job_id)
        
        # Record scan in history
        ScanHistory.objects.create(
            user=request.user,
            scan_type='job',
            code=job_id,
            item_id=job.job_id,
            item_name=job.project_name
        )
        
        # Return job details and redirect URL
        return JsonResponse({
            'success': True,
            'type': 'job',
            'id': job.job_id,
            'name': job.project_name,
            'redirect_url': f'/scan/job/{job.job_id}/'
        })
        
    except Job.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'No job found with ID {job_id}',
            'scanned_code': job_id  # Add the scanned code
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error processing job scan: {str(e)}',
            'scanned_code': job_id  # Add the scanned code
        })

def process_material_scan(request, material_id):
    """Process a material code scan"""
    try:
        # First try to look up material by our internal ID
        material = Material.objects.filter(material_id=material_id).first()
        
        # If not found, try serial number or supplier SKU
        if not material:
            material = Material.objects.filter(
                Q(serial_number=material_id) | Q(supplier_sku=material_id)
            ).first()
        
        if not material:
            return JsonResponse({
                'success': False,
                'error': f'No material found with ID or serial number {material_id}',
                'scanned_code': material_id  # Add the scanned code
            })
        
        # Record scan in history
        ScanHistory.objects.create(
            user=request.user,
            scan_type='material',
            code=material_id,
            item_id=material.material_id,
            item_name=material.name
        )
        
        # Return material details and redirect URL
        return JsonResponse({
            'success': True,
            'type': 'material',
            'id': material.material_id,
            'name': material.name,
            'redirect_url': f'/scan/material/{material.material_id}/'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error processing material scan: {str(e)}',
            'scanned_code': material_id  # Add the scanned code
        })

def process_machine_scan(request, machine_id):
    """Process a machine code scan"""
    try:
        # First try to look up machine by our internal ID
        machine = Machine.objects.filter(machine_id=machine_id).first()
        
        # If not found, try serial number
        if not machine:
            machine = Machine.objects.filter(serial_number=machine_id).first()
        
        if not machine:
            return JsonResponse({
                'success': False,
                'error': f'No machine found with ID or serial number {machine_id}',
                'scanned_code': machine_id  # Add the scanned code
            })
        
        # Record scan in history
        ScanHistory.objects.create(
            user=request.user,
            scan_type='machine',
            code=machine_id,
            item_id=machine.machine_id,
            item_name=machine.name
        )
        
        # Return machine details and redirect URL
        return JsonResponse({
            'success': True,
            'type': 'machine',
            'id': machine.machine_id,
            'name': machine.name,
            'redirect_url': f'/scan/machine/{machine.machine_id}/'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error processing machine scan: {str(e)}',
            'scanned_code': machine_id  # Add the scanned code
        })

@login_required
def scan_history(request):
    """View scan history"""
    scans = ScanHistory.objects.filter(user=request.user).order_by('-timestamp')[:20]
    context = {
        'scans': scans
    }
    return render(request, 'scanning/history.html', context)

@login_required
def manual_entry(request):
    """Handle manual entry when scanning fails"""
    if request.method == 'POST':
        item_id = request.POST.get('item_id', '')
        
        if not item_id:
            messages.error(request, 'Please enter an item ID')
            return redirect('scan')
        
        # Auto-detect the code type
        code_type = determine_code_type(item_id)
        
        # Process based on code type
        if code_type == 'job':
            try:
                job = Job.objects.get(job_id=item_id)
                return redirect('scanned_job', job_id=job.job_id)
            except Job.DoesNotExist:
                messages.error(request, f'No job found with ID {item_id}')
                return render(request, 'scanning/result.html', {'scanned_code': item_id})
        elif code_type == 'material':
            try:
                # Try internal ID first
                material = Material.objects.filter(material_id=item_id).first()
                
                # If not found, try serial number or supplier SKU
                if not material:
                    material = Material.objects.filter(
                        Q(serial_number=item_id) | Q(supplier_sku=item_id)
                    ).first()
                
                if material:
                    return redirect('scanned_material', material_id=material.material_id)
                else:
                    return render(request, 'scanning/result.html', {'scanned_code': item_id})
            except Exception:
                return render(request, 'scanning/result.html', {'scanned_code': item_id})
        elif code_type == 'machine':
            try:
                # Try internal ID first
                machine = Machine.objects.filter(machine_id=item_id).first()
                
                # If not found, try serial number
                if not machine:
                    machine = Machine.objects.filter(serial_number=item_id).first()
                
                if machine:
                    return redirect('scanned_machine', machine_id=machine.machine_id)
                else:
                    return render(request, 'scanning/result.html', {'scanned_code': item_id})
            except Exception:
                return render(request, 'scanning/result.html', {'scanned_code': item_id})
        else:
            # Unknown code type - try to find it in the database
            try:
                # Try as material serial number or supplier SKU
                material = Material.objects.filter(
                    Q(serial_number=item_id) | Q(supplier_sku=item_id)
                ).first()
                
                if material:
                    return redirect('scanned_material', material_id=material.material_id)
                
                # Try as machine serial number
                machine = Machine.objects.filter(serial_number=item_id).first()
                
                if machine:
                    return redirect('scanned_machine', machine_id=machine.machine_id)
                
                # If we got here, couldn't find it
                return render(request, 'scanning/result.html', {'scanned_code': item_id})
            except Exception:
                return render(request, 'scanning/result.html', {'scanned_code': item_id})
        
        return redirect('scan')
    
    # For GET requests, show the manual entry form
    return render(request, 'scanning/manual.html')

@login_required
def scanned_job(request, job_id):
    """Handle a scanned job"""
    job = get_object_or_404(Job, job_id=job_id)
    
    # If POST, set as active job
    if request.method == 'POST':
        try:
            settings, created = StaffSettings.objects.get_or_create(user=request.user)
            settings.set_active_job(job)
            messages.success(request, f'Job "{job.project_name}" has been set as your active job')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error setting active job: {str(e)}')
    
    context = {
        'job': job
    }
    return render(request, 'scanning/result.html', context)

@login_required
def scanned_material(request, material_id):
    """Handle a scanned material"""
    material = get_object_or_404(Material, material_id=material_id)
    
    # Get user's active job for association
    try:
        settings = StaffSettings.objects.get(user=request.user)
        active_job = settings.active_job
    except StaffSettings.DoesNotExist:
        active_job = None
    
    context = {
        'material': material,
        'active_job': active_job
    }
    return render(request, 'scanning/result.html', context)

@login_required
def scanned_machine(request, machine_id):
    """Handle a scanned machine"""
    machine = get_object_or_404(Machine, machine_id=machine_id)
    
    # Check if user is certified for this machine
    is_certified = False
    try:
        operator = request.user.operator
        is_certified = operator.is_certified_for(machine)
    except:
        pass
    
    # Get user's active job for association
    try:
        settings = StaffSettings.objects.get(user=request.user)
        active_job = settings.active_job
    except StaffSettings.DoesNotExist:
        active_job = None
    
    context = {
        'machine': machine,
        'is_certified': is_certified,
        'active_job': active_job,
        'js_file': 'machine_detail.js'
    }
    return render(request, 'scanning/result.html', context)

@login_required
def not_found_view(request):
    """Handle case when scanned item is not found"""
    scanned_code = request.GET.get('code', '')
    
    context = {
        'scanned_code': scanned_code
    }
    
    return render(request, 'scanning/result.html', context)
