from django.db import models
from django.utils import timezone

class JobFinancial(models.Model):
    """
    Model to track financial aspects of a job including
    costs, pricing, and payment status.
    """
    job = models.ForeignKey('workshop_app.Job', on_delete=models.CASCADE, related_name='financials')
    
    # Basic pricing
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quoted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Payment details
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid in Full'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deposit_date = models.DateField(null=True, blank=True)
    
    # Additional fields
    payment_due_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    invoice_number = models.CharField(max_length=50, null=True, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    
    # Cost tracking
    material_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    machine_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    overhead_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Additional costs
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Notes
    financial_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Financial for {self.job.project_name} ({self.job.job_id})"
    
    @property
    def total_cost(self):
        """Calculate the total cost from all cost components"""
        total = 0
        for field in [self.material_cost, self.labor_cost, self.machine_cost, 
                      self.overhead_cost, self.shipping_cost, self.tax_amount]:
            if field is not None:
                total += field
        
        # Subtract discount if present
        if self.discount_amount is not None:
            total -= self.discount_amount
            
        return total
    
    @property
    def amount_due(self):
        """Calculate the amount still due"""
        if self.final_price is None:
            return None
        
        paid = self.deposit_amount or 0
        return self.final_price - paid
    
    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        if self.payment_due_date and self.payment_status not in ['paid', 'cancelled']:
            return self.payment_due_date < timezone.now().date()
        return False
