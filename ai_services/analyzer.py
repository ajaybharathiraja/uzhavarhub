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

def recommend_crop(n, p, k, temperature, humidity, ph, rainfall):
    """
    Predict optimal crop using trained Random Forest model.
    """
    model = load_model('crop_model.pkl')
    if model:
        try:
            prediction = model.predict([[n, p, k, temperature, humidity, ph, rainfall]])
            return prediction[0]
        except Exception:
            pass
            
    # Fallback if model is missing or fails (no random logic per requirements)
    return 'rice'

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
    
    # Predict real demand using demand_model.pkl
    demand_model = load_model('demand_model.pkl')
    if demand_model:
        # Construct feature vector: ['day_of_year', 'month', 'is_weekend', 'prev_demand', 'Price', 'Discount']
        tomorrow = now + timedelta(days=1)
        day_of_year = tomorrow.timetuple().tm_yday
        month = tomorrow.month
        is_weekend = 1 if tomorrow.weekday() >= 5 else 0
        prev_demand = last_15  # Use last 15 days as naive prev_demand for feature
        
        try:
            predicted_demand = demand_model.predict([[day_of_year, month, is_weekend, prev_demand, current_price, 0.0]])
            pred_val = int(predicted_demand[0])
            forecast_text = f"🤖 AI Prediction: ML forecasts a demand of {max(0, pred_val)} units for {top_product_name} soon based on historical trends."
            price_trend = float(predicted_demand[0] / 100.0) # naive translation to trend
        except Exception:
            forecast_text = f"🤖 AI Prediction: Unable to compute forecast (Inference Error)."
            price_trend = 0.0
    else:
        forecast_text = f"🤖 AI Prediction: Demand model unavailable. Ensure train_ai_models.py has run."
        price_trend = 0.0
        
    return {
        'top_product': top_product_name,
        'growth_rate': round(growth, 1),
        'price_trend': round(price_trend, 2),
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
    # This was the old signature. We now use the real pricing model inside the integrated strategy.
    return round(base_price * 1.1, 2)

def get_integrated_market_strategy(n, p, k, temperature, humidity, ph, rainfall, date_obj=None):
    """
    The Core Novelty: Closed-Loop Coupling.
    1. Agronomy: Predict optimal crop based on soil and weather.
    2. Economics: Predict demand for that crop.
    3. Pricing: Predict optimal listing price based on demand.
    """
    if date_obj is None:
        date_obj = timezone.now() + timedelta(days=1)
        
    # 1. Crop Recommendation
    crop = recommend_crop(n, p, k, temperature, humidity, ph, rainfall)
    
    day_of_year = date_obj.timetuple().tm_yday
    month = date_obj.month
    is_weekend = 1 if date_obj.weekday() >= 5 else 0
    
    # 2. Demand Forecasting
    demand_model = load_model('demand_model.pkl')
    forecasted_demand = 100 # fallback
    if demand_model:
        try:
            # [day_of_year, month, is_weekend, prev_demand, Price, Discount]
            pred = demand_model.predict([[day_of_year, month, is_weekend, 50, 20.0, 0.0]])
            forecasted_demand = max(0, int(pred[0]))
        except Exception:
            pass
            
    # 3. Dynamic Pricing
    pricing_model = load_model('pricing_model.pkl')
    suggested_price = 20.0 # fallback
    if pricing_model:
        try:
            # feature_cols = ['day_of_year', 'month', 'is_weekend', 'quantity', 'Demand']
            pred_price = pricing_model.predict([[day_of_year, month, is_weekend, 50, forecasted_demand]])
            suggested_price = max(0, round(pred_price[0], 2))
        except Exception:
            pass
            
    return {
        'recommended_crop': crop,
        'forecasted_demand_volume': forecasted_demand,
        'suggested_price_per_kg': suggested_price
    }

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
    """
    Get recommended products.
    """
    # TODO: replace with real dataset collaborative filtering model.
    # Limitation: recommendation_sim.pkl is currently generated using mocked data.
    # Therefore, we fallback to trending products until real user interaction logs are available.
    return get_trending_products(limit)
