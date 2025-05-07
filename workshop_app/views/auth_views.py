from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html')

def logout_view(request):
    """Handle user logout"""
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    """Display user profile"""
    try:
        operator = request.user.operator
        context = {
            'operator': operator,
            'certified_machines': operator.certified_machines.all()
        }
    except:
        # Handle case where user doesn't have an associated operator profile
        context = {}
    
    return render(request, 'auth/profile.html', context)
