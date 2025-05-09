"""
Forms for job management.
"""
from django import forms
from django.core.exceptions import ValidationError
from workshop_app.models import Job, JobStatus, Client, ContactPerson

class JobFilterForm(forms.Form):
    """Form for filtering jobs in list view"""
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Search by name, ID, or client...',
        'class': 'form-control'
    }))
    
    status = forms.ModelChoiceField(
        queryset=JobStatus.objects.all(),
        required=False,
        empty_label="All Statuses",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    PRIORITY_CHOICES = (
        ('', 'All Priorities'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class JobForm(forms.ModelForm):
    """Form for adding and editing jobs"""
    # Override description field to make it not required
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        required=False  # Make description optional
    )
    
    # Override percent_complete field to make it not required
    percent_complete = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
        required=False,  # Make percent_complete optional
        initial=0  # Default to 0% complete
    )
    
    class Meta:
        model = Job
        fields = [
            'project_name', 'client', 'contact_person', 'status',
            'priority', 'description', 'start_date', 'expected_completion',
            'deadline', 'percent_complete'
        ]
        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'contact_person': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_completion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        expected_completion = cleaned_data.get('expected_completion')
        deadline = cleaned_data.get('deadline')
        
        # Set default percent_complete if not provided
        if cleaned_data.get('percent_complete') is None:
            cleaned_data['percent_complete'] = 0
        
        # Validate that expected_completion is not before start_date
        if start_date and expected_completion and start_date > expected_completion:
            raise ValidationError('Expected completion date cannot be earlier than start date')
        
        # Validate that deadline is not before start_date
        if start_date and deadline and start_date > deadline:
            raise ValidationError('Deadline cannot be earlier than start date')
        
        return cleaned_data
