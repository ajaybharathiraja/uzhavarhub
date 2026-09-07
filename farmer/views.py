from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from marketplace.models import Product
from ai_services.analyzer import get_market_insights
from .forms import ProductForm

def is_farmer(user):
    return user.is_authenticated and user.role == 'FARMER'

@login_required
def dashboard(request):
    if not is_farmer(request.user):
        raise PermissionDenied("Only farmers can access this portal.")
    
    products_count = Product.objects.filter(farmer=request.user.farmer_profile).count()
    insights = get_market_insights(request.user)
    
    return render(request, 'farmer/dashboard.html', {
        'products_count': products_count,
        'insights': insights
    })

@login_required
def product_list(request):
    if not is_farmer(request.user):
        raise PermissionDenied("Only farmers can access this portal.")
    
    products = Product.objects.filter(farmer=request.user.farmer_profile)
    return render(request, 'farmer/product_list.html', {'products': products})

@login_required
def add_product(request):
    if not is_farmer(request.user):
        raise PermissionDenied("Only farmers can access this portal.")
    
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = request.user.farmer_profile
            product.save()
            return redirect('farmer:product_list')
    else:
        form = ProductForm()
        
    return render(request, 'farmer/add_product.html', {'form': form})

@login_required
def edit_product(request, pk):
    if not is_farmer(request.user):
        raise PermissionDenied("Only farmers can access this portal.")
        
    product = get_object_or_404(Product, pk=pk, farmer=request.user.farmer_profile)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('farmer:product_list')
    else:
        form = ProductForm(instance=product)
        
    return render(request, 'farmer/edit_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, pk):
    if not is_farmer(request.user):
        raise PermissionDenied("Only farmers can access this portal.")
        
    product = get_object_or_404(Product, pk=pk, farmer=request.user.farmer_profile)
    
    if request.method == 'POST':
        product.delete()
        return redirect('farmer:product_list')
        
    return render(request, 'farmer/delete_product.html', {'product': product})

@login_required
def order_management(request):
    if not is_farmer(request.user):
        raise PermissionDenied("Only farmers can access this portal.")
        
    from orders.models import OrderItem
    # Get all items ordered from this farmer
    items = OrderItem.objects.filter(farmer=request.user).select_related('order', 'product').order_by('-order__created_at')
    
    return render(request, 'farmer/orders.html', {'items': items})

@login_required
def update_order_status(request, item_id):
    if not is_farmer(request.user):
        raise PermissionDenied("Only farmers can access this portal.")
        
    from orders.models import OrderItem
    item = get_object_or_404(OrderItem, id=item_id, farmer=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED']:
            item.status = new_status
            item.save()
            
    return redirect('farmer:orders')

@login_required
def farmer_earnings(request):
    if not is_farmer(request.user):
        raise PermissionDenied("Only farmers can access this portal.")
        
    from payments.models import Transaction
    from orders.models import OrderItem
    from django.db.models import Sum
    
    # In a real system, you'd calculate this by grouping OrderItems by farmer, 
    # matching them to Transactions. For simplicity here, we approximate:
    # A farmer's total earnings is the sum of their sold items in PAID orders, minus 5% fee.
    
    sold_items = OrderItem.objects.filter(
        farmer=request.user, 
        order__status__in=['PAID', 'DELIVERED', 'SHIPPED', 'COMPLETED']
    )
    
    total_sales_volume = sum(item.quantity * item.price_at_purchase for item in sold_items)
    platform_fees = float(total_sales_volume) * 0.05
    net_earnings = float(total_sales_volume) - platform_fees
    
    context = {
        'total_sales_volume': total_sales_volume,
        'platform_fees': platform_fees,
        'net_earnings': net_earnings,
        'sold_items': sold_items.order_by('-order__created_at')[:20] # recent 20
    }
    
    return render(request, 'farmer/earnings.html', context)

@login_required
def farmer_settings(request):
    if not is_farmer(request.user):
        raise PermissionDenied("Only farmers can access this portal.")
        
    from accounts.models import FarmerProfile
    profile, created = FarmerProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        farm_name = request.POST.get('farm_name')
        location = request.POST.get('location')
        email = request.POST.get('email')
        
        if farm_name and location:
            profile.farm_name = farm_name
            profile.location = location
            profile.save()
            
        if email:
            request.user.email = email
            request.user.save()
            
        from django.contrib import messages
        messages.success(request, "Your profile settings have been updated.")
        return redirect('farmer:settings')
        
    return render(request, 'farmer/settings.html', {'profile': profile})

@login_required
def crop_recommendation_view(request):
    if not is_farmer(request.user):
        raise PermissionDenied("Only farmers can access this portal.")
        
    recommendation = None
    if request.method == 'POST':
        try:
            n = float(request.POST.get('n', 0))
            p = float(request.POST.get('p', 0))
            k = float(request.POST.get('k', 0))
            temperature = float(request.POST.get('temperature', 0))
            humidity = float(request.POST.get('humidity', 0))
            ph = float(request.POST.get('ph', 0))
            rainfall = float(request.POST.get('rainfall', 0))
            
            from ai_services.analyzer import recommend_crop
            recommendation = recommend_crop(n, p, k, temperature, humidity, ph, rainfall)
        except Exception as e:
            recommendation = f"Error processing inputs: {str(e)}"
    return render(request, 'farmer/crop_recommendation.html', {'recommendation': recommendation})

@login_required
def market_demand(request):
    if not is_farmer(request.user):
        raise PermissionDenied("Only farmers can access this portal.")
        
    from orders.models import OrderItem
    from django.db.models import Sum
    from django.utils import timezone
    from datetime import timedelta
    
    products = Product.objects.filter(is_active=True).select_related('category')
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    sales_data = OrderItem.objects.filter(order__created_at__gte=thirty_days_ago)\
        .values('product_id')\
        .annotate(total_sold=Sum('quantity'))
        
    sales_dict = {item['product_id']: item['total_sold'] for item in sales_data}
    
    product_demand_list = []
    for product in products:
        total_sold = sales_dict.get(product.id, 0)
        
        if total_sold > 50:
            demand_level = 'High'
            demand_color = 'success' # green
        elif total_sold > 10:
            demand_level = 'Medium'
            demand_color = 'warning' # yellow
        else:
            demand_level = 'Low'
            demand_color = 'danger' # red
            
        product_demand_list.append({
            'product': product,
            'total_sold': total_sold,
            'demand_level': demand_level,
            'demand_color': demand_color
        })
        
    # Sort by total sold descending
    product_demand_list.sort(key=lambda x: x['total_sold'], reverse=True)
        
    return render(request, 'farmer/market_demand.html', {'product_demand_list': product_demand_list})
