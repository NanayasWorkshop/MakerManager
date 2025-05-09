from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Operator(models.Model):
    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    operator_id = models.CharField(max_length=15, unique=True)
    specialization = models.CharField(max_length=100)
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVEL_CHOICES)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    special_skills = models.TextField()
    productivity_factor = models.DecimalField(max_digits=10, decimal_places=2)
    # Using string reference to avoid circular import
    certified_machines = models.ManyToManyField('workshop_app.Machine', related_name='certified_operators')
    
    def __str__(self):
        return f"{self.operator_id} - {self.user.get_full_name() or self.user.username}"
    
    def is_certified_for(self, machine):
        return self.certified_machines.filter(id=machine.id).exists()

class StaffSettings(models.Model):
    DEFAULT_SCAN_CHOICES = [
        ('job', 'Job'),
        ('material', 'Material'),
        ('machine', 'Machine'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Changed from SET_NULL to CASCADE
    active_job = models.ForeignKey('workshop_app.Job', on_delete=models.CASCADE, null=True, blank=True, related_name='active_users')
    # Changed from SET_NULL to CASCADE
    personal_job = models.ForeignKey('workshop_app.Job', on_delete=models.CASCADE, null=True, blank=True, related_name='personal_users')
    active_since = models.DateTimeField(null=True, blank=True)
    show_active_job_banner = models.BooleanField(default=True)
    default_scan_for = models.CharField(max_length=10, choices=DEFAULT_SCAN_CHOICES, default='job')
    last_activity = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Settings for {self.user.username}"
    
    def set_active_job(self, job):
        self.active_job = job
        self.active_since = timezone.now()
        self.save()
    
    def clear_active_job(self):
        self.active_job = None
        self.active_since = None
        self.save()
