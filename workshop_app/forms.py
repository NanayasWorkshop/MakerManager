from django import forms
from django.contrib.auth.models import User
from workshop_app.models import Operator, Job, Material, Machine

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False)
