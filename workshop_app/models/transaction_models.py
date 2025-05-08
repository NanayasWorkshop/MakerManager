from django.db import models
from django.contrib.auth.models import User

class MaterialTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('withdrawal', 'Withdrawal'),
        ('return', 'Return'),
        ('adjustment', 'Adjustment'),
        ('purchase', 'Purchase'),
    ]
    
    # Using string reference to avoid circular import
    material = models.ForeignKey('workshop_app.Material', on_delete=models.CASCADE, related_name='transactions')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    transaction_date = models.DateTimeField(auto_now_add=True)
    job_reference = models.CharField(max_length=100)
    operator_name = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} of {self.quantity} - {self.material.name}"
    
    class Meta:
        ordering = ['-transaction_date']

class ScanHistory(models.Model):
    SCAN_TYPE_CHOICES = [
        ('job', 'Job'),
        ('material', 'Material'),
        ('machine', 'Machine'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scan_type = models.CharField(max_length=20, choices=SCAN_TYPE_CHOICES)
    code = models.CharField(max_length=100)
    item_id = models.CharField(max_length=100)
    item_name = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_scan_type_display()}: {self.item_id} by {self.user.username}"
    
    class Meta:
        verbose_name_plural = "Scan Histories"
        ordering = ['-timestamp']
