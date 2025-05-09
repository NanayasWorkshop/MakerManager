"""
Views for creating and editing jobs.
"""
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from workshop_app.models import Job, JobStatus, Client, ContactPerson, StaffSettings
from workshop_app.forms import JobForm

@login_required
def add_job(request):
    """Show form and handle adding a new job"""
    # Get job statuses for dropdowns
    job_statuses = JobStatus.objects.all().order_by('order')
    
    # Get clients for dropdowns
    clients = Client.objects.filter(status='active').order_by('name')
    
    if request.method == 'POST':
        # Process form submission
        form = JobForm(request.POST)
        if form.is_valid():
            # Save but don't commit to set additional fields
            job = form.save(commit=False)
            
            # Set default percent_complete if not provided
            if job.percent_complete is None:
                job.percent_complete = 0
            
            # Generate a unique job ID
            # Format: J-XXXXX where XXXXX is a 5-digit number
            # Find the highest job ID number and increment by 1
            last_job = Job.objects.order_by('-job_id').first()
            if last_job:
                # Extract number from job_id (format: J-XXXXX)
                match = re.search(r'J-(\d+)', last_job.job_id)
                if match:
                    last_number = int(match.group(1))
                    new_number = last_number + 1
                else:
                    new_number = 1
            else:
                new_number = 1
            
            # Create new job ID with 5 digits
            job.job_id = f"J-{new_number:05d}"
            
            # Set creator to current user
            job.created_by = request.user
            
            # Set is_general and is_personal flags
            job.is_general = 'is_general' in request.POST
            job.is_personal = 'is_personal' in request.POST
            
            # Set owner to current user
            job.owner = request.user
            
            # Set status_text from the selected status
            if job.status:
                job.status_text = job.status.name
            else:
                # Provide a default status text if needed
                job.status_text = "New"
            
            # Save the job
            job.save()
            
            # If job is personal, set it as the user's personal job
            if job.is_personal:
                staff_settings, created = StaffSettings.objects.get_or_create(user=request.user)
                staff_settings.personal_job = job
                staff_settings.save()
            
            messages.success(request, f'Job "{job.project_name}" has been added successfully')
            return redirect('job_detail', job_id=job.job_id)
        else:
            messages.error(request, 'Please correct the errors below')
            # Print form errors for debugging
            print(f"Form errors: {form.errors}")
    else:
        form = JobForm()
    
    context = {
        'form': form,
        'job_statuses': job_statuses,
        'clients': clients,
    }
    
    return render(request, 'jobs/add.html', context)

@login_required
def edit_job(request, job_id):
    """Show form and handle editing a job"""
    job = get_object_or_404(Job, job_id=job_id)
    
    # Get job statuses for dropdowns
    job_statuses = JobStatus.objects.all().order_by('order')
    
    # Get clients for dropdowns
    clients = Client.objects.filter(status='active').order_by('name')
    
    # Get contact persons for the selected client
    contact_persons = []
    if job.client:
        contact_persons = ContactPerson.objects.filter(client=job.client)
    
    if request.method == 'POST':
        # Process form submission
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            # Set is_general and is_personal flags
            job.is_general = 'is_general' in request.POST
            job.is_personal = 'is_personal' in request.POST
            
            # Make sure status_text is updated when status changes
            if job.status:
                job.status_text = job.status.name
            
            # Save the job
            job = form.save()
            
            # If job is personal, set it as the user's personal job
            if job.is_personal:
                staff_settings, created = StaffSettings.objects.get_or_create(user=request.user)
                staff_settings.personal_job = job
                staff_settings.save()
            
            messages.success(request, f'Job "{job.project_name}" has been updated')
            return redirect('job_detail', job_id=job.job_id)
        else:
            messages.error(request, 'Please correct the errors below')
            # Print form errors for debugging
            print(f"Form errors: {form.errors}")
    else:
        form = JobForm(instance=job)
    
    context = {
        'job': job,
        'form': form,
        'job_statuses': job_statuses,
        'clients': clients,
        'contact_persons': contact_persons,
    }
    
    return render(request, 'jobs/edit.html', context)
