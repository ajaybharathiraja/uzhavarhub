import os
import random
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from orders.models import OrderItem
from marketplace.models import Product
from django.conf import settings

def recommend_crop(n, p, k, temperature, humidity, ph, rainfall):
    """
    Mocked crop recommendation function.
    """
    crops = ['rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas',
             'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate',
             'banana', 'mango', 'grapes', 'watermelon', 'muskmelon', 'apple',
             'orange', 'papaya', 'coconut', 'cotton', 'jute', 'coffee']
    # Use input sum to seed the random choice so it's deterministic for the same inputs
    seed = sum([n, p, k, temperature, humidity, ph, rainfall])
    random.seed(seed)
    return random.choice(crops)

def get_trending_products(limit=4):
    """
    Get actual trending products based on order quantities (No ML required).
    """
    thirty_days_ago = timezone.now() - timedelta(days=30)
    trending_qs = OrderItem.objects.filter(order__created_at__gte=thirty_days_ago) \
        .values('product_id') \
        .annotate(total_sold=Sum('quantity')) \
        .order_by('-total_sold')[:limit]
        
    trending_product_ids = [item['product_id'] for item in trending_qs]
    products = Product.objects.filter(id__in=trending_product_ids)
    
    products_dict = {p.id: p for p in products}
    sorted_products = [products_dict[pid] for pid in trending_product_ids if pid in products_dict]
    
    return sorted_products

def get_market_insights(farmer):
    """
    Mocked market insights without using pandas or joblib.
    """
    items = OrderItem.objects.filter(farmer=farmer).values(
        'product__name', 'quantity', 'order__created_at', 'price_at_purchase'
    )
    
    if not items:
        return {
            'top_product': 'Not enough data',
            'growth_rate': 0,
            'price_trend': 0,
            'current_price': 0,
            'forecast': 'Need more sales data to forecast using ML.'
        }
    
    # Simple Python-based aggregation
    product_sales = {}
    for item in items:
        name = item['product__name']
        if name not in product_sales:
            product_sales[name] = 0
        product_sales[name] += item['quantity']
        
    top_product_name = max(product_sales, key=product_sales.get)
    
    now = timezone.now()
    last_15 = 0
    prev_15 = 0
    avg_price_last_15_sum = 0
    avg_price_last_15_count = 0
    
    for item in items:
        item_date = item['order__created_at']
        if item_date >= (now - timedelta(days=15)):
            last_15 += item['quantity']
            if item['product__name'] == top_product_name:
                avg_price_last_15_sum += float(item['price_at_purchase'])
                avg_price_last_15_count += 1
        elif (now - timedelta(days=30)) <= item_date < (now - timedelta(days=15)):
            prev_15 += item['quantity']

    growth = ((last_15 - prev_15) / prev_15) * 100 if prev_15 > 0 else (100 if last_15 > 0 else 0)
    current_price = (avg_price_last_15_sum / avg_price_last_15_count) if avg_price_last_15_count > 0 else 0
    
    # Generate mock forecast text
    forecast_text = f"🤖 AI Prediction: Stable demand forecasted for {top_product_name} (~{int(last_15 / 15 if last_15 > 0 else 50)} units daily)."
        
    return {
        'top_product': top_product_name,
        'growth_rate': round(growth, 1),
        'price_trend': random.choice([5.0, -2.5, 10.0, 0.0]), # Mock trend
        'current_price': round(current_price, 2),
        'forecast': forecast_text
    }
