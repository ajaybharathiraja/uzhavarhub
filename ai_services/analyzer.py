import os
import random
import joblib
import pandas as pd
import numpy as np
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

# --- NEW ADVANCED AI FEATURES (Q1 JOURNAL) ---

def load_model(filename):
    model_path = os.path.join(settings.BASE_DIR, 'ai_services', 'models', filename)
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

def predict_optimal_price(base_price, competitor_price, shelf_life, seasonality_index=1.0):
    model = load_model('pricing_model.pkl')
    if model:
        prediction = model.predict([[base_price, seasonality_index, competitor_price, shelf_life]])
        return round(prediction[0], 2)
    # Fallback mock
    return round(base_price * 1.1, 2)

def predict_crop_yield(area_acres, soil_quality, rainfall_mm, fertilizer_kg):
    model = load_model('yield_model.pkl')
    if model:
        prediction = model.predict([[area_acres, soil_quality, rainfall_mm, fertilizer_kg]])
        return round(prediction[0], 2)
    return round(area_acres * 1.5, 2)

def analyze_reviews_sentiment(reviews_text_list):
    if not reviews_text_list:
        return {"positive": 0, "neutral": 0, "negative": 0}
        
    model_data = load_model('sentiment_model.pkl')
    if model_data:
        vectorizer, model = model_data
        X = vectorizer.transform(reviews_text_list)
        predictions = model.predict(X)
        
        counts = {2: 0, 1: 0, 0: 0}
        for p in predictions:
            counts[p] += 1
            
        total = len(reviews_text_list)
        return {
            "positive": round(counts[2] / total * 100, 1),
            "neutral": round(counts[1] / total * 100, 1),
            "negative": round(counts[0] / total * 100, 1)
        }
    return {"positive": 80, "neutral": 15, "negative": 5}

def get_ai_product_recommendations(limit=4):
    # For now, just return random top products, as the similarity matrix needs user context.
    # In a full app, we would use the matrix in recommendation_sim.pkl
    return get_trending_products(limit)
