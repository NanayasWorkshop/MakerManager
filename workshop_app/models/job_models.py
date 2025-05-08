
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from workshop_app.models.client_models import Client, ContactPerson

class JobStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    color_code = models.CharField(max_length=7)
    order = models.IntegerField()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Job Statuses"

class Job(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    job_id = models.CharField(max_length=15, unique=True)
    project_name = models.CharField(max_length=100)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    contact_person = models.ForeignKey(ContactPerson, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_jobs')
    created_date = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)
    description = models.TextField()
    end_date = models.DateField(null=True, blank=True)
    expected_completion = models.DateField(null=True, blank=True)
    is_general = models.BooleanField(default=False)
    is_personal = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_jobs')
    percent_complete = models.IntegerField(default=0)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    qr_code = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    status = models.ForeignKey(JobStatus, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.job_id} - {self.project_name}"
    
    def is_overdue(self):
        if self.deadline:
            return self.deadline < timezone.now().date() and self.status.name != 'Completed'
        return False
    
    def days_until_deadline(self):
        if self.deadline:
            days = (self.deadline - timezone.now().date()).days
            return days if days > 0 else 0
        return None

class JobMaterial(models.Model):
    RESULT_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('returned', 'Returned'),
        ('scrapped', 'Scrapped'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='materials')
    # Material is referenced as string to avoid circular import
    material = models.ForeignKey('workshop_app.Material', on_delete=models.CASCADE, related_name='job_uses')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_used = models.DateTimeField(auto_now_add=True)
    added_by = models.CharField(max_length=100)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.quantity} of {self.material.name} for {self.job.project_name}"
    
    @property
    def total_cost(self):
        if self.unit_price:
            return self.quantity * self.unit_price
        return None
