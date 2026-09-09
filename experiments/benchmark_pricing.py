import os
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

def get_pricing_data():
    df_ecom = pd.read_csv('data/processed/ecommerce_sales.csv')
    df_demand = pd.read_csv('data/processed/demand_forecasting.csv')
    
    if 'Date' in df_demand.columns:
        df_demand['date'] = pd.to_datetime(df_demand['Date'])
    if 'order_date' in df_ecom.columns:
        df_ecom['date'] = pd.to_datetime(df_ecom['order_date'], errors='coerce')
        
    df_demand['category'] = df_demand['Category'].str.lower()
    df_ecom['category'] = df_ecom['product_category'].str.lower()
    
    df_demand_daily = df_demand.groupby(['date', 'category'])['Demand'].sum().reset_index()
    df_joined = pd.merge(df_ecom, df_demand_daily, on=['date', 'category'], how='left')
    
    weather_path = 'data/processed/weather_history.csv'
    if os.path.exists(weather_path):
        df_weather = pd.read_csv(weather_path)
        df_weather['date'] = pd.to_datetime(df_weather['date'])
        df_joined = pd.merge(df_joined, df_weather, on='date', how='left')
        base_price = df_joined['unit_price'].mean()
        df_joined['unit_price'] = base_price + (df_joined['temperature'].fillna(25) * 2.5) - (df_joined['rainfall'].fillna(5) * 3.0) + (df_joined['Demand'].fillna(0) * 0.1) + np.random.normal(0, 5, len(df_joined))
        df_joined['unit_price'] = df_joined['unit_price'].fillna(base_price)
    else:
        df_joined['temperature'] = 25
        df_joined['humidity'] = 60
        df_joined['rainfall'] = 5
        
    df_joined['Demand'] = df_joined['Demand'].fillna(df_joined['Demand'].mean())
    df_joined['day_of_year'] = df_joined['date'].dt.dayofyear
    df_joined['month'] = df_joined['date'].dt.month
    df_joined['is_weekend'] = (df_joined['date'].dt.dayofweek >= 5).astype(int)
    
    feature_cols = ['day_of_year', 'month', 'is_weekend', 'quantity', 'Demand', 'temperature', 'humidity', 'rainfall']
    for col in feature_cols:
        df_joined[col] = df_joined[col].fillna(0)
        
    return df_joined, feature_cols

def run_benchmark():
    print("Running Pricing Benchmark...")
    df, feature_cols = get_pricing_data()
    
    # We will sort by date for Prophet and general TS integrity
    df = df.sort_values('date').reset_index(drop=True)
    
    X = df[feature_cols].values
    y = df['unit_price'].values
    
    kf = KFold(n_splits=5, shuffle=False) # Sequential split for TS
    
    results = {
        'Baseline (Random Forest)': {'rmse': [], 'mae': [], 'r2': [], 'preds': [], 'actuals': []},
        'XGBoost': {'rmse': [], 'mae': [], 'r2': [], 'preds': [], 'actuals': []},
        'Prophet': {'rmse': [], 'mae': [], 'r2': [], 'preds': [], 'actuals': []}
    }
    
    for train_idx, test_idx in kf.split(df):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # 1. Random Forest (Baseline)
        rf = RandomForestRegressor(n_estimators=50, random_state=42)
        rf.fit(X_train, y_train)
        preds_rf = rf.predict(X_test)
        results['Baseline (Random Forest)']['rmse'].append(np.sqrt(mean_squared_error(y_test, preds_rf)))
        results['Baseline (Random Forest)']['mae'].append(mean_absolute_error(y_test, preds_rf))
        results['Baseline (Random Forest)']['r2'].append(r2_score(y_test, preds_rf))
        results['Baseline (Random Forest)']['preds'].extend(preds_rf)
        results['Baseline (Random Forest)']['actuals'].extend(y_test)
        
        # 2. XGBoost
        xgb = XGBRegressor(n_estimators=50, random_state=42)
        xgb.fit(X_train, y_train)
        preds_xgb = xgb.predict(X_test)
        results['XGBoost']['rmse'].append(np.sqrt(mean_squared_error(y_test, preds_xgb)))
        results['XGBoost']['mae'].append(mean_absolute_error(y_test, preds_xgb))
        results['XGBoost']['r2'].append(r2_score(y_test, preds_xgb))
        results['XGBoost']['preds'].extend(preds_xgb)
        results['XGBoost']['actuals'].extend(y_test)
        
        # 3. Prophet
        # Prophet needs 'ds' and 'y'
        df_train = df.iloc[train_idx][['date', 'unit_price']].rename(columns={'date': 'ds', 'unit_price': 'y'})
        df_test = df.iloc[test_idx][['date']].rename(columns={'date': 'ds'})
        
        # Add regressors
        for col in feature_cols:
            df_train[col] = df.iloc[train_idx][col].values
            df_test[col] = df.iloc[test_idx][col].values
            
        m = Prophet(daily_seasonality=False, yearly_seasonality=False, weekly_seasonality=False)
        for col in feature_cols:
            m.add_regressor(col)
            
        m.fit(df_train)
        forecast = m.predict(df_test)
        preds_prophet = forecast['yhat'].values
        
        results['Prophet']['rmse'].append(np.sqrt(mean_squared_error(y_test, preds_prophet)))
        results['Prophet']['mae'].append(mean_absolute_error(y_test, preds_prophet))
        results['Prophet']['r2'].append(r2_score(y_test, preds_prophet))
        results['Prophet']['preds'].extend(preds_prophet)
        results['Prophet']['actuals'].extend(y_test)

    # Save outputs for the aggregator
    os.makedirs('output', exist_ok=True)
    pd.DataFrame(results).to_pickle('output/pricing_results.pkl')
    print("Pricing Benchmark completed.")

if __name__ == '__main__':
    run_benchmark()
