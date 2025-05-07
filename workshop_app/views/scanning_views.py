"""
Views for handling scanning functionality
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone

from workshop_app.models import Job, Material, Machine, StaffSettings, ScanHistory
from workshop_app.utils.barcode_utils import determine_code_type, parse_code
from workshop_app.forms import ManualEntryForm

@login_required
def scan_view(request):
    """Main scanning interface"""
    # Get the preferred scan type from user settings
    try:
        settings = StaffSettings.objects.get(user=request.user)
        default_scan_type = settings.default_scan_for
    except StaffSettings.DoesNotExist:
        default_scan_type = 'job'
    
    # Get recent scans
    recent_scans = ScanHistory.objects.filter(user=request.user).order_by('-timestamp')[:5]
    
    context = {
        'default_scan_type': default_scan_type,
        'recent_scans': recent_scans,
        'form': ManualEntryForm(initial={'entry_type': default_scan_type})
    }
    
    return render(request, 'scanning/scan.html', context)

@login_required
@require_POST
def process_scan(request):
    """Process a scanned code"""
    code = request.POST.get('code', '')
    scan_type = request.POST.get('scan_type', 'auto')
    
    if not code:
        return JsonResponse({'success': False, 'error': 'No code provided'})
    
    # Parse the code to extract ID
    parsed_code = parse_code(code)
    
    # If scan type is auto, try to determine from the code
    if scan_type == 'auto':
        scan_type = determine_code_type(parsed_code)
    
    # Process based on scan type
    if scan_type == 'job':
        return process_job_scan(request, parsed_code)
    elif scan_type == 'material':
        return process_material_scan(request, parsed_code)
    elif scan_type == 'machine':
        return process_machine_scan(request, parsed_code)
    else:
        return JsonResponse({'success': False, 'error': 'Unknown scan type'})

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
            'error': f'No job found with ID {job_id}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error processing job scan: {str(e)}'
        })

def process_material_scan(request, material_id):
    """Process a material code scan"""
    try:
        # Look up material by ID
        material = Material.objects.get(material_id=material_id)
        
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
        
    except Material.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'No material found with ID {material_id}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error processing material scan: {str(e)}'
        })

def process_machine_scan(request, machine_id):
    """Process a machine code scan"""
    try:
        # Look up machine by ID
        machine = Machine.objects.get(machine_id=machine_id)
        
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
        
    except Machine.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'No machine found with ID {machine_id}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error processing machine scan: {str(e)}'
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
        'active_job': active_job
    }
    return render(request, 'scanning/result.html', context)

@login_required
def manual_entry(request):
    """Handle manual entry when scanning fails"""
    if request.method == 'POST':
        form = ManualEntryForm(request.POST)
        if form.is_valid():
            entry_type = form.cleaned_data['entry_type']
            item_id = form.cleaned_data['item_id']
            
            # Process based on entry type
            if entry_type == 'job':
                return process_job_scan(request, item_id)
            elif entry_type == 'material':
                return process_material_scan(request, item_id)
            elif entry_type == 'machine':
                return process_machine_scan(request, item_id)
    else:
        form = ManualEntryForm()
    
    context = {
        'form': form
    }
    return render(request, 'scanning/manual.html', context)
