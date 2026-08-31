from django.shortcuts import render, redirect
from ai_services.analyzer import get_trending_products

def index(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    # Redirect based on role
    if getattr(request.user, 'role', None) == 'CUSTOMER':
        return redirect('marketplace:product_list')
    elif getattr(request.user, 'role', None) == 'FARMER':
        return redirect('farmer:dashboard')
        
    trending_products = get_trending_products(limit=4)
    return render(request, 'core/index.html', {'trending_products': trending_products})
