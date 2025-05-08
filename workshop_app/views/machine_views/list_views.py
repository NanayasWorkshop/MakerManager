"""
Views for machine listing and filtering.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from workshop_app.models import Machine, MachineType
from workshop_app.forms import MachineFilterForm

@login_required
def machine_list(request):
    """List machines with search and filter capabilities"""
    # Get filter parameters from request
    search_query = request.GET.get('search', '')
    type_id = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')
    operator_filter = request.GET.get('operator', '') 
    sort_param = request.GET.get('sort', 'name')
    
    # Start with all machines
    machines = Machine.objects.all()
    
    # Apply search filter
    if search_query:
        machines = machines.filter(
            Q(name__icontains=search_query) |
            Q(machine_id__icontains=search_query) |
            Q(manufacturer__icontains=search_query) |
            Q(model_number__icontains=search_query) |
            Q(location_in_workshop__icontains=search_query)
        )
    
    # Apply type filter
    if type_id:
        machines = machines.filter(machine_type_id=type_id)
    
    # Apply status filter
    if status_filter:
        machines = machines.filter(status=status_filter)
    
    # Apply operator filter - only show machines the operator is certified for
    if operator_filter and request.user.is_authenticated:
        try:
            operator = request.user.operator
            machines = machines.filter(certified_operators=operator)
        except:
            # If user doesn't have an operator profile, ignore this filter
            pass
    
    # Apply sorting
    if sort_param == 'name':
        machines = machines.order_by('name')
    elif sort_param == 'id':
        machines = machines.order_by('machine_id')
    elif sort_param == 'type':
        machines = machines.order_by('machine_type__name')
    elif sort_param == 'status':
        machines = machines.order_by('status')
    elif sort_param == 'location':
        machines = machines.order_by('location_in_workshop')
    
    # Get machine types for filter dropdowns
    machine_types = MachineType.objects.all().order_by('name')
    
    # Initialize filter form
    filter_form = MachineFilterForm(request.GET)
    
    # Check if user is certified for each machine
    certification_status = {}
    if request.user.is_authenticated:
        try:
            operator = request.user.operator
            for machine in machines:
                certification_status[machine.id] = operator.is_certified_for(machine)
        except:
            # If user doesn't have an operator profile, all machines are uncertified
            for machine in machines:
                certification_status[machine.id] = False
    
    context = {
        'machines': machines,
        'machine_types': machine_types,
        'filter_form': filter_form,
        'certification_status': certification_status,
    }
    
    return render(request, 'machines/list.html', context)
