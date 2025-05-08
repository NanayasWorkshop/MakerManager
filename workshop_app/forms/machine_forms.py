"""
Forms for machine management.
"""
from django import forms
from django.core.exceptions import ValidationError
from workshop_app.models import Machine, MachineType, MachineUsage

class MachineFilterForm(forms.Form):
    """Form for filtering machines in list view"""
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Search by name, ID, or manufacturer...',
        'class': 'form-control'
    }))
    
    type = forms.ModelChoiceField(
        queryset=MachineType.objects.all(),
        required=False,
        empty_label="All Types",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    STATUS_CHOICES = (
        ('', 'All Statuses'),
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Maintenance'),
        ('out_of_order', 'Out of Order'),
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    operator = forms.BooleanField(
        required=False,
        label="Only show machines I'm certified for",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class MachineForm(forms.ModelForm):
    """Form for adding and editing machines"""
    class Meta:
        model = Machine
        fields = [
            'name', 'machine_type', 'manufacturer', 'model_number', 'serial_number',
            'location_in_workshop', 'purchase_date', 'purchase_price', 'supplier',
            'warranty_end_date', 'working_area', 'power_requirements', 'maximum_work_speed',
            'precision', 'hourly_rate', 'setup_time', 'setup_rate', 'cleanup_time',
            'cleanup_rate', 'status', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'machine_type': forms.Select(attrs={'class': 'form-select'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'model_number': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'location_in_workshop': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'warranty_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'working_area': forms.TextInput(attrs={'class': 'form-control'}),
            'power_requirements': forms.TextInput(attrs={'class': 'form-control'}),
            'maximum_work_speed': forms.TextInput(attrs={'class': 'form-control'}),
            'precision': forms.TextInput(attrs={'class': 'form-control'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'setup_time': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'setup_rate': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'cleanup_time': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'cleanup_rate': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        purchase_date = cleaned_data.get('purchase_date')
        warranty_end_date = cleaned_data.get('warranty_end_date')
        
        if purchase_date and warranty_end_date and purchase_date > warranty_end_date:
            raise ValidationError('Warranty end date cannot be earlier than purchase date')
        
        return cleaned_data

class MachineUsageForm(forms.Form):
    """Form for starting machine usage"""
    setup_time = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
        }),
        initial=15,
        help_text="Time needed to set up the machine (minutes)"
    )
    
    estimated_usage = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
        }),
        initial=60,
        help_text="Estimated usage time (minutes)"
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
        })
    )

class MachineStopUsageForm(forms.Form):
    """Form for stopping machine usage"""
    cleanup_time = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
        }),
        initial=10,
        help_text="Time needed to clean up the machine (minutes)"
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
        })
    )
