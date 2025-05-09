from django.db import migrations

def add_job_statuses(apps, schema_editor):
    JobStatus = apps.get_model('workshop_app', 'JobStatus')
    
    # Get the current highest order value
    max_order = JobStatus.objects.all().order_by('-order').values_list('order', flat=True).first() or 0
    
    # Add new statuses (adjust colors as needed)
    statuses = [
        {'name': 'Personal', 'description': 'Personal project', 'color_code': '#9C27B0', 'order': max_order + 1},
        {'name': 'Active', 'description': 'Active job being worked on', 'color_code': '#4CAF50', 'order': max_order + 2},
        {'name': 'Pause', 'description': 'Job temporarily paused', 'color_code': '#FF9800', 'order': max_order + 3},
        {'name': 'InChange', 'description': 'Job requirements being changed', 'color_code': '#F44336', 'order': max_order + 4},
    ]
    
    for status_data in statuses:
        # Only add if it doesn't exist
        if not JobStatus.objects.filter(name=status_data['name']).exists():
            JobStatus.objects.create(**status_data)

def remove_job_statuses(apps, schema_editor):
    JobStatus = apps.get_model('workshop_app', 'JobStatus')
    JobStatus.objects.filter(name__in=['Personal', 'Active', 'Pause', 'InChange']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('workshop_app', '0009_alter_machine_current_job_and_more'),
    ]

    operations = [
        migrations.RunPython(add_job_statuses, remove_job_statuses),
    ]
