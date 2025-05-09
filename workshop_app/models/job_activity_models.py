from django.db import models
from django.contrib.auth.models import User

class JobActivityLog(models.Model):
    """
    Model to track activity and updates related to a job.
    Provides a complete history of job actions.
    """
    job = models.ForeignKey('workshop_app.Job', on_delete=models.CASCADE, related_name='activity_logs')
    
    # Activity details
    activity_type = models.CharField(max_length=50, choices=[
        ('status_update', 'Status Update'),
        ('comment', 'Comment'),
        ('material_usage', 'Material Usage'),
        ('machine_usage', 'Machine Usage'),
        ('labor_tracking', 'Labor Tracking'),
        ('financial_update', 'Financial Update'),
        ('client_communication', 'Client Communication'),
        ('file_upload', 'File Upload'),
        ('milestone', 'Milestone'),
        ('system', 'System Event')
    ])
    
    activity_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    
    # Reference to who performed the activity
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    performed_by_name = models.CharField(max_length=100, blank=True)  # Denormalized name for historical record
    
    # Additional metadata
    metadata = models.JSONField(null=True, blank=True)  # Store any additional structured data
    
    # Optional: references to related objects
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.IntegerField(null=True, blank=True)
    
    # Visibility
    is_internal = models.BooleanField(default=False)  # For staff only vs visible to client
    is_system_generated = models.BooleanField(default=False)  # Was this automatically generated
    
    class Meta:
        ordering = ['-activity_date']
        indexes = [
            models.Index(fields=['job', 'activity_date']),
            models.Index(fields=['activity_type']),
        ]
    
    def __str__(self):
        return f"{self.get_activity_type_display()} on {self.activity_date.strftime('%Y-%m-%d %H:%M')}"
    
    @classmethod
    def log_activity(cls, job, activity_type, description, user=None, metadata=None, 
                    related_object_type=None, related_object_id=None, is_internal=False):
        """Helper method to easily create activity log entries"""
        activity = cls(
            job=job,
            activity_type=activity_type,
            description=description,
            performed_by=user,
            performed_by_name=user.get_full_name() if user else '',
            metadata=metadata,
            related_object_type=related_object_type,
            related_object_id=related_object_id,
            is_internal=is_internal,
            is_system_generated=user is None
        )
        activity.save()
        return activity
