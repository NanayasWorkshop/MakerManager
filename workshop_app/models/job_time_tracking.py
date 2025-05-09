"""
Models for job time tracking
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.utils.functional import cached_property

class JobTimeTracking(models.Model):
    """Track time spent by users working on jobs"""
    job = models.ForeignKey('workshop_app.Job', on_delete=models.CASCADE, related_name='time_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_logs')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def duration(self):
        """Calculate duration of the time entry"""
        if self.end_time:
            return self.end_time - self.start_time
        elif self.is_active:
            return timezone.now() - self.start_time
        return timedelta(seconds=0)
    
    @property
    def is_active(self):
        """Check if this time entry is currently active"""
        return self.end_time is None
    
    @cached_property
    def elapsed_time(self):
        """Return formatted elapsed time"""
        seconds = self.duration.total_seconds()
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{int(hours)}h {int(minutes)}m"
        else:
            return f"{int(minutes)}m {int(seconds)}s"
            
    def __str__(self):
        status = "Active" if self.is_active else "Completed"
        return f"{self.job.job_id} - {self.user.username} - {status}"
    
    class Meta:
        ordering = ['-start_time']
        verbose_name = "Job Time Entry"
        verbose_name_plural = "Job Time Entries"
        indexes = [
            models.Index(fields=['job', 'user', 'start_time']),
            models.Index(fields=['user', 'start_time']),
        ]

    @classmethod
    def get_active_entry(cls, user):
        """Get the currently active time entry for a user, if any"""
        return cls.objects.filter(user=user, end_time__isnull=True).first()
    
    @classmethod
    def start_tracking(cls, job, user, notes=""):
        """Start time tracking for a job"""
        # Check if user already has an active tracking
        active_tracking = cls.get_active_entry(user)
        if active_tracking:
            # If active tracking is for a different job, stop it first
            if active_tracking.job != job:
                active_tracking.end_time = timezone.now()
                active_tracking.save()
            else:
                # Already tracking this job
                return active_tracking
        
        # Create a new time entry
        return cls.objects.create(
            job=job,
            user=user,
            start_time=timezone.now(),
            notes=notes
        )
    
    @classmethod
    def stop_tracking(cls, user, notes=None):
        """Stop any active time tracking for a user"""
        active_tracking = cls.get_active_entry(user)
        if active_tracking:
            active_tracking.end_time = timezone.now()
            if notes:
                # Set the notes directly instead of appending to previous notes
                active_tracking.notes = notes
            active_tracking.save()
            return active_tracking
        return None
