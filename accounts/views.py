from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.cache import never_cache
from .forms import CustomUserCreationForm
from .models import CustomerProfile, FarmerProfile

@never_cache
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create corresponding profile based on role
            if user.role == 'CUSTOMER':
                CustomerProfile.objects.create(user=user)
            elif user.role == 'FARMER':
                FarmerProfile.objects.create(user=user)
            login(request, user)
            return redirect('core:index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

@never_cache
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('core:index')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST' or request.method == 'GET':
        logout(request)
        return redirect('core:index')
