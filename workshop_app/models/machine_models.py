from django.db import models
from django.contrib.auth.models import User

class MachineType(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return f"{self.code} - {self.name}"

class Machine(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Maintenance'),
        ('out_of_order', 'Out of Order'),
    ]
    
    machine_id = models.CharField(max_length=15, unique=True)
    machine_type = models.ForeignKey(MachineType, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100)
    location_in_workshop = models.CharField(max_length=100)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    supplier = models.CharField(max_length=100)
    warranty_end_date = models.DateField(null=True, blank=True)
    working_area = models.CharField(max_length=100)
    power_requirements = models.CharField(max_length=100)
    maximum_work_speed = models.CharField(max_length=50)
    precision = models.CharField(max_length=50)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    setup_time = models.IntegerField(null=True, blank=True)
    setup_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cleanup_time = models.IntegerField(null=True, blank=True)
    cleanup_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    reserved_until = models.DateTimeField(null=True, blank=True)
    qr_code = models.CharField(max_length=100)
    notes = models.TextField()
    # This will be set after Job model is defined using string reference
    current_job = models.ForeignKey('workshop_app.Job', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_machines')
    
    def __str__(self):
        return f"{self.machine_id} - {self.name}"
    
    def is_available(self):
        return self.status == 'available'
