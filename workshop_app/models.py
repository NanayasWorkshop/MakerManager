from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class MaterialCategory(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        verbose_name_plural = "Material Categories"

class MaterialType(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    description = models.TextField()
    category = models.ForeignKey(MaterialCategory, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        unique_together = [['category', 'code']]

class Material(models.Model):
    material_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE)
    color = models.CharField(max_length=50)
    dimensions = models.CharField(max_length=100)
    unit_of_measurement = models.CharField(max_length=20)
    supplier_name = models.CharField(max_length=100)
    brand_name = models.CharField(max_length=100)
    current_stock = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_stock_level = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    minimum_stock_alert = models.BooleanField(default=False)
    location_in_workshop = models.CharField(max_length=100)
    purchase_date = models.DateField(null=True, blank=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    project_association = models.CharField(max_length=100)
    notes = models.TextField()
    qr_code = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    supplier_sku = models.CharField(max_length=50)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.material_id} - {self.name}"

    def is_low_stock(self):
        if self.minimum_stock_level:
            return self.current_stock <= self.minimum_stock_level
        return False

class MachineType(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return f"{self.code} - {self.name}"

class JobStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    color_code = models.CharField(max_length=7)
    order = models.IntegerField()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Job Statuses"

class Client(models.Model):
    TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('company', 'Company'),
        ('nonprofit', 'Non-Profit'),
        ('education', 'Educational'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('prospect', 'Prospect'),
    ]
    
    client_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    industry = models.CharField(max_length=100)
    reference_source = models.CharField(max_length=100)
    notes = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Contact information
    primary_email = models.EmailField()
    secondary_email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    mobile_number = models.CharField(max_length=20)
    website = models.URLField(max_length=200)
    social_media = models.TextField()
    
    # Address
    street_address = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    # Financial information
    tax_id = models.CharField(max_length=50)
    payment_terms = models.CharField(max_length=50)
    currency = models.CharField(max_length=10)
    discount_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    account_status = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.client_id} - {self.name}"

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
    current_job = models.ForeignKey('Job', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_machines')
    
    def __str__(self):
        return f"{self.machine_id} - {self.name}"
    
    def is_available(self):
        return self.status == 'available'

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
    certified_machines = models.ManyToManyField(Machine, related_name='certified_operators')
    
    def __str__(self):
        return f"{self.operator_id} - {self.user.get_full_name() or self.user.username}"
    
    def is_certified_for(self, machine):
        return self.certified_machines.filter(id=machine.id).exists()

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
    contact_person = models.ForeignKey('ContactPerson', on_delete=models.SET_NULL, null=True, blank=True)
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

class ContactPerson(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    primary_contact = models.BooleanField(default=False)
    notes = models.TextField()
    direct_email = models.EmailField()
    phone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20)
    communication_preference = models.CharField(max_length=20)
    working_hours = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.name} ({self.client.name})"

class StaffSettings(models.Model):
    DEFAULT_SCAN_CHOICES = [
        ('job', 'Job'),
        ('material', 'Material'),
        ('machine', 'Machine'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    active_job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True, related_name='active_users')
    personal_job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True, related_name='personal_users')
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

class MaterialTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('withdrawal', 'Withdrawal'),
        ('return', 'Return'),
        ('adjustment', 'Adjustment'),
        ('purchase', 'Purchase'),
    ]
    
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='transactions')
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

class JobMaterial(models.Model):
    RESULT_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('returned', 'Returned'),
        ('scrapped', 'Scrapped'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='materials')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='job_uses')
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
