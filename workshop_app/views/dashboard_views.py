from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from workshop_app.models import Job, Machine, Material, StaffSettings
from django.db.models import Q

@login_required
def dashboard(request):
    """Display the main dashboard"""
    
    # Get the active job for the current user
    try:
        staff_settings = StaffSettings.objects.get(user=request.user)
        active_job = staff_settings.active_job
    except StaffSettings.DoesNotExist:
        active_job = None
        
    # Get recent jobs for the user
    recent_jobs = Job.objects.filter(
        Q(created_by=request.user) | Q(owner=request.user)
    ).order_by('-created_date')[:5]
    
    # Get available machines
    available_machines = Machine.objects.filter(status='available')[:5]
    
    # Get low stock materials
    low_stock_materials = Material.objects.filter(minimum_stock_alert=True)[:5]
    
    context = {
        'active_job': active_job,
        'recent_jobs': recent_jobs,
        'available_machines': available_machines,
        'low_stock_materials': low_stock_materials,
    }
    
    return render(request, 'dashboard/index.html', context)
