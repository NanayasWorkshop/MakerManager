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
            
            # Get the project type from the form
            project_type = request.POST.get('project_type', 'JOB')
            
            # Get the current year's last two digits
            current_year = timezone.now().year % 100
            
            # Find the highest job number for this project type and year
            # Format: J-XXX-YYYYRR where XXX is the project type, YYYY is a sequence number, and RR is the year
            # We need to find the max YYYY for the current type and year
            prefix = f"J-{project_type}-"
            suffix = f"{current_year}"
            
            # Find the highest job ID matching our pattern
            last_job_id = Job.objects.filter(
                job_id__startswith=prefix,
                job_id__endswith=suffix
            ).order_by('-job_id').first()
            
            if last_job_id:
                # Extract the sequence number from the last job ID
                try:
                    # Format: J-XXX-YYYYRR, we want to extract YYYY
                    sequence_str = last_job_id.job_id.split('-')[2][:-2]
                    sequence_num = int(sequence_str)
                    new_sequence = sequence_num + 1
                except (IndexError, ValueError):
                    # If parsing fails, start from 1
                    new_sequence = 1
            else:
                # No existing jobs of this type, start from 1
                new_sequence = 1
            
            # Format the new job ID
            # Sequence number padded to 4 digits
            job.job_id = f"{prefix}{new_sequence:04d}{suffix}"
            
            # Set creator to current user
            job.created_by = request.user
            
            # Set project type
            job.project_type = project_type
            
            # Set owner to current user
            job.owner = request.user
            
            # Set status_text from the selected status
            status_id = request.POST.get('status')
            if status_id:
                try:
                    status_obj = JobStatus.objects.get(id=status_id)
                    job.status_text = status_obj.name
                except JobStatus.DoesNotExist:
                    job.status_text = "New"
            else:
                job.status_text = "New"
            
            # Save the job
            job.save()
            
            # If job is personal type, set it as the user's personal job
            if job.project_type == 'PER':
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
            # Get the old project type for comparison
            old_project_type = job.project_type
            
            # Update job
            job = form.save(commit=False)
            
            # Directly query for status to get its name
            status_id = request.POST.get('status')
            if status_id:
                try:
                    status_obj = JobStatus.objects.get(id=status_id)
                    job.status_text = status_obj.name
                except JobStatus.DoesNotExist:
                    job.status_text = "Unknown"
            
            # Save the job
            job = form.save()
            
            # Update personal job reference if needed
            if job.project_type == 'PER' and old_project_type != 'PER':
                staff_settings, created = StaffSettings.objects.get_or_create(user=request.user)
                staff_settings.personal_job = job
                staff_settings.save()
            elif job.project_type != 'PER' and old_project_type == 'PER':
                # If it's no longer a personal job, remove it as the user's personal job
                staff_settings = StaffSettings.objects.filter(user=request.user, personal_job=job).first()
                if staff_settings:
                    staff_settings.personal_job = None
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
