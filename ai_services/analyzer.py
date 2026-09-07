import os
import joblib
import pandas as pd
import numpy as np
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from orders.models import OrderItem
from marketplace.models import Product
from django.conf import settings

# Load models safely
def get_model_path(filename):
    return os.path.join(settings.BASE_DIR, 'ai_services', 'models', filename)

def recommend_crop(n, p, k, temperature, humidity, ph, rainfall):
    """
    Uses the trained RandomForestClassifier to recommend a crop based on soil and weather metrics.
    """
    model_path = get_model_path('crop_model.pkl')
    if not os.path.exists(model_path):
        return "Model not found. Please train models first."
        
    try:
        model = joblib.load(model_path)
        # Create DataFrame with exact same column names used in training
        input_data = pd.DataFrame(
            [[n, p, k, temperature, humidity, ph, rainfall]], 
            columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        )
        prediction = model.predict(input_data)
        return prediction[0]
    except Exception as e:
        return f"Error making prediction: {str(e)}"

def get_trending_products(limit=4):
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
    Uses the trained LinearRegression model to forecast next week's sales for the farmer's top product.
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
        
    df = pd.DataFrame(items)
    df['date'] = pd.to_datetime(df['order__created_at'])
    df['price_at_purchase'] = df['price_at_purchase'].astype(float)
    
    product_sales = df.groupby('product__name')['quantity'].sum().reset_index()
    top_product_row = product_sales.loc[product_sales['quantity'].idxmax()]
    top_product_name = top_product_row['product__name']
    
    # Calculate simple growth rate for display
    now = timezone.now()
    last_15 = df[df['date'] >= (now - timedelta(days=15))]['quantity'].sum()
    prev_15 = df[(df['date'] >= (now - timedelta(days=30))) & (df['date'] < (now - timedelta(days=15)))]['quantity'].sum()
    growth = ((last_15 - prev_15) / prev_15) * 100 if prev_15 > 0 else (100 if last_15 > 0 else 0)
    
    # Calculate price trend for top product
    top_product_data = df[df['product__name'] == top_product_name]
    last_15_price_data = top_product_data[top_product_data['date'] >= (now - timedelta(days=15))]
    prev_15_price_data = top_product_data[(top_product_data['date'] >= (now - timedelta(days=30))) & (top_product_data['date'] < (now - timedelta(days=15)))]
    
    avg_price_last_15 = last_15_price_data['price_at_purchase'].mean() if not last_15_price_data.empty else (top_product_data['price_at_purchase'].mean() if not top_product_data.empty else 0)
    avg_price_prev_15 = prev_15_price_data['price_at_purchase'].mean() if not prev_15_price_data.empty else avg_price_last_15
    
    if avg_price_prev_15 > 0:
        price_trend = ((avg_price_last_15 - avg_price_prev_15) / avg_price_prev_15) * 100
    else:
        price_trend = 0
    
    # Advanced Forecasting using ML Model
    model_path = get_model_path('demand_model.pkl')
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            
            # Predict sales for tomorrow
            tomorrow = now + timedelta(days=1)
            day_of_year = tomorrow.timetuple().tm_yday
            month = tomorrow.month
            is_weekend = 1 if tomorrow.weekday() >= 5 else 0
            
            # Use last_15 average as a rough prev_sales proxy for prediction
            prev_sales = last_15 / 15 if last_15 > 0 else 50
            
            # Create DataFrame with exact column names used in training
            input_data = pd.DataFrame(
                [[day_of_year, month, is_weekend, prev_sales]],
                columns=['day_of_year', 'month', 'is_weekend', 'prev_sales']
            )
            
            predicted_sales = model.predict(input_data)[0]
            
            # Generate ML-backed forecast text
            if predicted_sales > (prev_sales * 1.2):
                forecast_text = f"🤖 AI Prediction: High demand spike expected for {top_product_name}. Recommend stocking ~{int(predicted_sales)} units."
            elif predicted_sales < (prev_sales * 0.8):
                forecast_text = f"🤖 AI Prediction: Demand for {top_product_name} is projected to dip. Consider offering discounts."
            else:
                forecast_text = f"🤖 AI Prediction: Stable demand forecasted for {top_product_name} (~{int(predicted_sales)} units daily)."
                
        except Exception as e:
            forecast_text = f"Model error: {str(e)}"
    else:
        forecast_text = f"Demand is stable for {top_product_name}."
        
    return {
        'top_product': top_product_name,
        'growth_rate': round(growth, 1),
        'price_trend': round(price_trend, 1),
        'current_price': round(avg_price_last_15, 2),
        'forecast': forecast_text
    }
