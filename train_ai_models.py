import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uzhavarhub.settings')
django.setup()

evaluation_results = {}

def train_crop_recommendation_model():
    print("\n--- Training Crop Recommendation Model ---")
    csv_path = 'data/processed/crop_recommendation.csv'
    if not os.path.exists(csv_path):
        print(f"ERROR: {csv_path} not found.")
        return
        
    df = pd.read_csv(csv_path)
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = df['label']
    
    # 80/20 stratified split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    
    # Baseline 1: Logistic Regression
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)
    lr_preds = lr.predict(X_test)
    lr_acc = accuracy_score(y_test, lr_preds)
    
    # Baseline 2: KNN
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_train, y_train)
    knn_preds = knn.predict(X_test)
    knn_acc = accuracy_score(y_test, knn_preds)
    
    # Advanced Model: Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    
    acc = accuracy_score(y_test, rf_preds)
    prec = precision_score(y_test, rf_preds, average='macro', zero_division=0)
    rec = recall_score(y_test, rf_preds, average='macro', zero_division=0)
    f1 = f1_score(y_test, rf_preds, average='macro', zero_division=0)
    cm = confusion_matrix(y_test, rf_preds).tolist()
    
    evaluation_results['Crop_Recommendation'] = {
        'Baseline_LR_Accuracy': float(lr_acc),
        'Baseline_KNN_Accuracy': float(knn_acc),
        'RF_Accuracy': float(acc),
        'RF_Precision_Macro': float(prec),
        'RF_Recall_Macro': float(rec),
        'RF_F1_Macro': float(f1),
        'Confusion_Matrix': cm
    }
    
    os.makedirs('ai_services/models', exist_ok=True)
    joblib.dump(rf, 'ai_services/models/crop_model.pkl')
    print("Crop model saved. Metrics logged.")


def train_demand_forecasting_model():
    print("\n--- Training Demand Forecasting Model ---")
    demand_path = 'data/processed/demand_forecasting.csv'
    ecommerce_path = 'data/processed/ecommerce_sales.csv'
    
    if not os.path.exists(demand_path) or not os.path.exists(ecommerce_path):
        print("ERROR: Demand or Ecommerce processed datasets not found.")
        return
        
    df_demand = pd.read_csv(demand_path)
    df_ecom = pd.read_csv(ecommerce_path)
    
    # Preprocess demand date
    if 'Date' in df_demand.columns:
        df_demand['date'] = pd.to_datetime(df_demand['Date'])
    
    # Preprocess ecom date
    if 'order_date' in df_ecom.columns:
        df_ecom['date'] = pd.to_datetime(df_ecom['order_date'], errors='coerce')
        
    # Standardize category names for join
    df_demand['category'] = df_demand['Category'].str.lower()
    df_ecom['category'] = df_ecom['product_category'].str.lower()
    
    # Extract date features
    df_demand['day_of_year'] = df_demand['date'].dt.dayofyear
    df_demand['month'] = df_demand['date'].dt.month
    df_demand['is_weekend'] = (df_demand['date'].dt.dayofweek >= 5).astype(int)
    
    # Sort and shift for lag on 'Demand'
    df_demand = df_demand.sort_values(by=['Product ID', 'date'])
    df_demand['prev_demand'] = df_demand.groupby(['Product ID'])['Demand'].shift(1)
    df_demand = df_demand.dropna(subset=['prev_demand'])
    
    # Join with ecommerce data aggregated by date and category
    df_ecom_daily = df_ecom.groupby(['date', 'category'])['quantity'].sum().reset_index()
    df_joined = pd.merge(df_demand, df_ecom_daily, on=['date', 'category'], how='left')
    df_joined['quantity'] = df_joined['quantity'].fillna(0)
    
    # Features and Target
    feature_cols = ['day_of_year', 'month', 'is_weekend', 'prev_demand', 'Price', 'Discount']
    X = df_joined[feature_cols]
    y = df_joined['Demand']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    evaluation_results['Demand_Forecasting'] = {
        'Model_Type': 'LinearRegression',
        'Test_RMSE': float(rmse),
        'Test_MAE': float(mae),
        'Test_R2': float(r2)
    }
    
    joblib.dump(model, 'ai_services/models/demand_model.pkl')
    print("Demand forecasting model saved. Metrics logged.")


if __name__ == '__main__':
    train_crop_recommendation_model()
    train_demand_forecasting_model()
    
    os.makedirs('ai_services/models', exist_ok=True)
    with open('ai_services/models/evaluation_results.json', 'w') as f:
        json.dump(evaluation_results, f, indent=4)
    print("\nSaved evaluation metrics to ai_services/models/evaluation_results.json")
