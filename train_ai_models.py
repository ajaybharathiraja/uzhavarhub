import os
import django
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics.pairwise import cosine_similarity

# Setup Django environment so we can query database if needed later
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uzhavarhub.settings')
django.setup()

def train_crop_recommendation_model():
    print("Training Crop Recommendation Model...")
    
    # Generate Synthetic Dataset for Tamil Nadu crops
    # N, P, K, temperature, humidity, ph, rainfall -> crop
    np.random.seed(42)
    
    # Crops: Rice, Mango, Coconut, Turmeric, Carrot, Egg (mock)
    # We will simulate standard optimal ranges for these
    data = []
    
    # Rice (Thanjavur Ponni Rice): High NPK, High Temp, High Rainfall
    for _ in range(200):
        data.append([
            np.random.randint(60, 100), np.random.randint(35, 60), np.random.randint(35, 55),
            np.random.uniform(20, 35), np.random.uniform(75, 95), np.random.uniform(5.5, 7.5),
            np.random.uniform(150, 250), 'Rice'
        ])
        
    # Mango (Salem Mangoes): Mod NPK, High Temp, Mod Rainfall
    for _ in range(200):
        data.append([
            np.random.randint(20, 40), np.random.randint(15, 35), np.random.randint(25, 45),
            np.random.uniform(25, 40), np.random.uniform(45, 65), np.random.uniform(5.0, 7.0),
            np.random.uniform(70, 100), 'Mango'
        ])
        
    # Coconut (Pollachi Coconuts): Mod N, High K, Mod Temp, High Rainfall
    for _ in range(200):
        data.append([
            np.random.randint(20, 40), np.random.randint(10, 30), np.random.randint(50, 80),
            np.random.uniform(25, 35), np.random.uniform(80, 95), np.random.uniform(5.2, 8.0),
            np.random.uniform(120, 220), 'Coconut'
        ])
        
    # Turmeric (Erode Turmeric): Mod NPK, Mod Temp, Mod Rainfall
    for _ in range(200):
        data.append([
            np.random.randint(30, 60), np.random.randint(30, 60), np.random.randint(30, 60),
            np.random.uniform(20, 35), np.random.uniform(60, 80), np.random.uniform(5.5, 7.5),
            np.random.uniform(100, 150), 'Turmeric'
        ])
        
    # Carrot (Ooty Carrots): Mod NPK, Low Temp, Mod Rainfall
    for _ in range(200):
        data.append([
            np.random.randint(10, 30), np.random.randint(30, 60), np.random.randint(20, 40),
            np.random.uniform(10, 20), np.random.uniform(50, 70), np.random.uniform(5.5, 7.0),
            np.random.uniform(80, 120), 'Carrot'
        ])

    df = pd.DataFrame(data, columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'crop'])
    
    X = df.drop('crop', axis=1)
    y = df['crop']
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Save model
    os.makedirs('ai_services/models', exist_ok=True)
    joblib.dump(model, 'ai_services/models/crop_model.pkl')
    print("Crop Recommendation Model trained and saved successfully.")


def train_demand_forecasting_model():
    print("Training Demand Forecasting Model...")
    # Generate Synthetic Historical Sales Data
    # Features: day_of_year, month, is_weekend, previous_day_sales -> today_sales
    
    np.random.seed(42)
    days = 365
    
    # Base trend + seasonality (e.g. higher in certain months) + random noise
    X = []
    y = []
    
    # Let's create a simple time series
    for i in range(1, days):
        day_of_year = i % 365
        month = (i // 30) % 12 + 1
        is_weekend = 1 if (i % 7) >= 5 else 0
        
        # Artificial sales calculation
        base_sales = 50
        seasonality = np.sin(2 * np.pi * day_of_year / 365) * 20
        weekend_boost = 15 if is_weekend else 0
        noise = np.random.normal(0, 5)
        
        today_sales = max(10, base_sales + seasonality + weekend_boost + noise)
        
        if i > 1:
            X.append([day_of_year, month, is_weekend, prev_sales])
            y.append(today_sales)
            
        prev_sales = today_sales

    model = LinearRegression()
    model.fit(X, y)
    
    joblib.dump(model, 'ai_services/models/demand_model.pkl')
    print("Demand Forecasting Model trained and saved successfully.")


def train_dynamic_pricing_model():
    print("Training Dynamic Pricing Model...")
    np.random.seed(42)
    # Features: base_market_price, seasonality_index, competitor_price, shelf_life_days -> optimal_price
    X = []
    y = []
    for _ in range(500):
        base_price = np.random.uniform(20, 200)
        seasonality = np.random.uniform(0.8, 1.5) # 1.0 is normal, 1.5 is high demand
        competitor = base_price * np.random.uniform(0.9, 1.2)
        shelf_life = np.random.randint(1, 30)
        
        # Optimal price drops if shelf life is low, increases if high demand or competitor is high
        optimal_price = base_price * seasonality
        if shelf_life < 5:
            optimal_price *= 0.8 # discount to sell fast
        optimal_price = (optimal_price + competitor) / 2
        
        X.append([base_price, seasonality, competitor, shelf_life])
        y.append(optimal_price)
        
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)
    joblib.dump(model, 'ai_services/models/pricing_model.pkl')
    print("Dynamic Pricing Model trained and saved.")

def train_yield_prediction_model():
    print("Training Yield Prediction Model...")
    np.random.seed(42)
    # Features: area_acres, soil_quality_index(1-10), rainfall_mm, fertilizer_kg -> yield_tons
    X = []
    y = []
    for _ in range(500):
        area = np.random.uniform(1, 50)
        soil = np.random.uniform(1, 10)
        rain = np.random.uniform(50, 300)
        fert = area * np.random.uniform(10, 50)
        
        # Yield is roughly proportional to area, boosted by soil and rain (up to a point)
        yield_tons = area * (soil / 5) * (rain / 100) * 1.5
        yield_tons += np.random.normal(0, yield_tons * 0.1) # noise
        yield_tons = max(0.1, yield_tons)
        
        X.append([area, soil, rain, fert])
        y.append(yield_tons)
        
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)
    joblib.dump(model, 'ai_services/models/yield_model.pkl')
    print("Yield Prediction Model trained and saved.")

def train_review_sentiment_model():
    print("Training Review Sentiment Model...")
    # Very basic sentiment dataset
    reviews = [
        "This rice is amazing, very fresh and good quality.",
        "Loved the mangoes, sweet and delivered on time.",
        "Excellent packaging and great taste.",
        "Okay product, nothing special.",
        "Average quality, could be better.",
        "It was decent, but price is high.",
        "Terrible quality, completely rotten.",
        "Very bad experience, eggs were broken.",
        "Do not buy this, waste of money."
    ]
    # 2: Positive, 1: Neutral, 0: Negative
    sentiments = [2, 2, 2, 1, 1, 1, 0, 0, 0]
    
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(reviews)
    model = MultinomialNB()
    model.fit(X, sentiments)
    
    joblib.dump((vectorizer, model), 'ai_services/models/sentiment_model.pkl')
    print("Sentiment Model trained and saved.")

def train_product_recommendation_model():
    print("Training Product Recommendation Model (Content-Based mock)...")
    # In a real app, this would query the DB. We'll just create a mock similarity matrix.
    # Features: Category, Price range, Organic flag
    mock_products = pd.DataFrame({
        'id': range(1, 11),
        'category_id': [1, 1, 2, 2, 3, 3, 4, 4, 1, 2],
        'is_organic': [1, 0, 1, 1, 0, 0, 1, 0, 1, 0],
        'price': [50, 40, 120, 150, 30, 25, 200, 180, 60, 130]
    })
    
    # Simple similarity based on same category and organic flag
    features = mock_products[['category_id', 'is_organic', 'price']]
    # Normalize price
    features['price'] = features['price'] / features['price'].max()
    
    similarity_matrix = cosine_similarity(features)
    joblib.dump(similarity_matrix, 'ai_services/models/recommendation_sim.pkl')
    print("Recommendation similarity matrix saved.")


if __name__ == '__main__':
    train_crop_recommendation_model()
    train_demand_forecasting_model()
    train_dynamic_pricing_model()
    train_yield_prediction_model()
    train_review_sentiment_model()
    train_product_recommendation_model()

