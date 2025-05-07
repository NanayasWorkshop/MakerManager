from django import forms
from django.core.exceptions import ValidationError
from workshop_app.models import Material, MaterialCategory, MaterialType

class MaterialFilterForm(forms.Form):
    """Form for filtering materials in list view"""
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Search by name, ID, or supplier...',
        'class': 'form-control'
    }))
    
    category = forms.ModelChoiceField(
        queryset=MaterialCategory.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    type = forms.ModelChoiceField(
        queryset=MaterialType.objects.all(),
        required=False,
        empty_label="All Types",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    STOCK_CHOICES = (
        ('', 'All Stock Levels'),
        ('low', 'Low Stock'),
        ('out', 'Out of Stock'),
        ('available', 'In Stock'),
    )
    
    stock = forms.ChoiceField(
        choices=STOCK_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class MaterialForm(forms.ModelForm):
    """Form for adding and editing materials"""
    class Meta:
        model = Material
        fields = [
            'name', 'material_type', 'color', 'dimensions', 'unit_of_measurement',
            'supplier_name', 'brand_name', 'current_stock', 'minimum_stock_level',
            'location_in_workshop', 'purchase_date', 'price_per_unit', 'expiration_date',
            'project_association', 'notes', 'serial_number', 'supplier_sku',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'material_type': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'dimensions': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_of_measurement': forms.Select(attrs={'class': 'form-select'}),
            'supplier_name': forms.TextInput(attrs={'class': 'form-control'}),
            'brand_name': forms.TextInput(attrs={'class': 'form-control'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'minimum_stock_level': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'location_in_workshop': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'price_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'expiration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'project_association': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier_sku': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        purchase_date = cleaned_data.get('purchase_date')
        expiration_date = cleaned_data.get('expiration_date')
        
        if purchase_date and expiration_date and purchase_date > expiration_date:
            raise ValidationError('Expiration date cannot be earlier than purchase date')
        
        return cleaned_data

class MaterialTransactionForm(forms.Form):
    """Form for material withdrawals and returns"""
    quantity = forms.DecimalField(
        min_value=0.01,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0.01',
            'step': '0.01',
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
        })
    )
