from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from accounts.models import FarmerProfile

from ai_services.analyzer import get_ai_product_recommendations

def product_list(request):
    products = Product.objects.filter(is_active=True).select_related('farmer', 'category').order_by('-created_at')
    categories = Category.objects.all()
    ai_recommendations = get_ai_product_recommendations(limit=4)
    return render(request, 'marketplace/product_list.html', {
        'products': products,
        'categories': categories,
        'ai_recommendations': ai_recommendations,
        'title': 'Fresh Farm Products'
    })

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'marketplace/category_list.html', {'categories': categories, 'title': 'Categories'})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'marketplace/product_detail.html', {'product': product, 'title': product.name})

def farmer_list(request):
    farmers = FarmerProfile.objects.all().order_by('farm_name')
    return render(request, 'marketplace/farmer_list.html', {'farmers': farmers, 'title': 'Our Farmers'})
