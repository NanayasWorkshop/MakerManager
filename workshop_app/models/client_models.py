from django.db import models

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
