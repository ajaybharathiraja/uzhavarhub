import pandas as pd
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from orders.models import OrderItem
from marketplace.models import Product

def get_trending_products(limit=4):
    """
    Returns the top 'limit' fast-moving products in the last 30 days based on quantity sold.
    """
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Aggregate sales using Django ORM (which is faster than loading all into pandas for simple aggregation)
    trending_qs = OrderItem.objects.filter(order__created_at__gte=thirty_days_ago) \
        .values('product_id') \
        .annotate(total_sold=Sum('quantity')) \
        .order_by('-total_sold')[:limit]
        
    trending_product_ids = [item['product_id'] for item in trending_qs]
    
    # Fetch the actual product objects, keeping the sorted order
    products = Product.objects.filter(id__in=trending_product_ids)
    
    # Sort them in Python to match the query order
    products_dict = {p.id: p for p in products}
    sorted_products = [products_dict[pid] for pid in trending_product_ids if pid in products_dict]
    
    return sorted_products

def get_market_insights(farmer):
    """
    Uses Pandas to analyze a farmer's sales data and predict trends.
    """
    # Fetch all order items for this farmer
    items = OrderItem.objects.filter(farmer=farmer).values(
        'product__name', 'quantity', 'order__created_at'
    )
    
    if not items:
        return {
            'top_product': 'Not enough data',
            'growth_rate': 0,
            'forecast': 'Need more sales data to forecast.'
        }
        
    # Load into pandas DataFrame
    df = pd.DataFrame(items)
    
    # Convert 'order__created_at' to datetime
    df['date'] = pd.to_datetime(df['order__created_at'])
    
    # Calculate Total Quantity Sold per Product
    product_sales = df.groupby('product__name')['quantity'].sum().reset_index()
    top_product_row = product_sales.loc[product_sales['quantity'].idxmax()]
    top_product_name = top_product_row['product__name']
    
    # Calculate simple growth rate: Compare last 15 days vs previous 15 days
    now = timezone.now()
    last_15 = df[df['date'] >= (now - timedelta(days=15))]['quantity'].sum()
    prev_15 = df[(df['date'] >= (now - timedelta(days=30))) & (df['date'] < (now - timedelta(days=15)))]['quantity'].sum()
    
    if prev_15 > 0:
        growth = ((last_15 - prev_15) / prev_15) * 100
    else:
        growth = 100 if last_15 > 0 else 0
        
    # Generate Forecast text
    if growth > 10:
        forecast_text = f"High demand expected for {top_product_name}. Consider increasing stock by 20%."
    elif growth < -10:
        forecast_text = f"Demand is cooling down. Focus on marketing {top_product_name}."
    else:
        forecast_text = f"Demand is stable. Maintain current stock levels for {top_product_name}."
        
    return {
        'top_product': top_product_name,
        'growth_rate': round(growth, 1),
        'forecast': forecast_text
    }
