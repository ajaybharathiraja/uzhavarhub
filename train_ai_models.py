import os
import django
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression

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


if __name__ == '__main__':
    train_crop_recommendation_model()
    train_demand_forecasting_model()
