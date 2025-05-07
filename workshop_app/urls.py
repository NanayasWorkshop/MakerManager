from django.urls import path
from workshop_app.views import auth_views, dashboard_views

urlpatterns = [
    # Authentication URLs
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('profile/', auth_views.profile_view, name='profile'),
    
    # Dashboard URL
    path('', dashboard_views.dashboard, name='dashboard'),
]
