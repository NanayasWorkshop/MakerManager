"""
Views for displaying material details and history.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from workshop_app.models import Material, MaterialTransaction, JobMaterial, StaffSettings
from workshop_app.utils.barcode_utils import generate_qr_code


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
def get_material_qr_code(request, material_id):
    """Generate and return QR code for a material"""
    material = get_object_or_404(Material, material_id=material_id)
    
    # Generate QR code
    qr_code_url = generate_qr_code(material.material_id)
    
    return JsonResponse({
        'success': True,
        'material_name': material.name,
        'qr_code_url': qr_code_url
    })
