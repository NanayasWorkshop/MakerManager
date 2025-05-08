from django.db import models
from django.contrib.auth.models import User

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

class AttachmentType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

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

class MaterialAttachment(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='attachments')
    attachment_type = models.ForeignKey(AttachmentType, on_delete=models.CASCADE)  # Required field
    custom_type = models.CharField(max_length=50)  # Already matches the DB
    description = models.CharField(max_length=100)
    file = models.FileField(upload_to='material_attachments/')
    upload_date = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.material.name} - {self.get_type_display()}"
    
    def get_type_display(self):
        if self.attachment_type:
            return self.attachment_type.name
        return self.custom_type or "Unknown"
