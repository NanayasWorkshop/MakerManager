from django import forms
from django.contrib.auth.models import User
from workshop_app.models import Operator, Job, Material, Machine

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False)

class ManualEntryForm(forms.Form):
    ENTRY_TYPE_CHOICES = [
        ('job', 'Job'),
        ('material', 'Material'),
        ('machine', 'Machine'),
    ]
    
    entry_type = forms.ChoiceField(
        choices=ENTRY_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    item_id = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter ID (e.g., J-12345, M-12345, MC-12345)'
        })
    )
