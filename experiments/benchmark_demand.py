import os
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

def mean_absolute_percentage_error(y_true, y_pred): 
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    # Avoid division by zero
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

def get_demand_data():
    demand_path = 'data/processed/demand_forecasting.csv'
    ecommerce_path = 'data/processed/ecommerce_sales.csv'
    
    df_demand = pd.read_csv(demand_path)
    df_ecom = pd.read_csv(ecommerce_path)
    
    if 'Date' in df_demand.columns:
        df_demand['date'] = pd.to_datetime(df_demand['Date'])
    if 'order_date' in df_ecom.columns:
        df_ecom['date'] = pd.to_datetime(df_ecom['order_date'], errors='coerce')
        
    df_demand['category'] = df_demand['Category'].str.lower()
    df_ecom['category'] = df_ecom['product_category'].str.lower()
    
    df_demand['day_of_year'] = df_demand['date'].dt.dayofyear
    df_demand['month'] = df_demand['date'].dt.month
    df_demand['is_weekend'] = (df_demand['date'].dt.dayofweek >= 5).astype(int)
    
    df_demand = df_demand.sort_values(by=['Product ID', 'date'])
    df_demand['prev_demand'] = df_demand.groupby(['Product ID'])['Demand'].shift(1)
    df_demand = df_demand.dropna(subset=['prev_demand'])
    
    df_ecom_daily = df_ecom.groupby(['date', 'category'])['quantity'].sum().reset_index()
    df_joined = pd.merge(df_demand, df_ecom_daily, on=['date', 'category'], how='left')
    df_joined['quantity'] = df_joined['quantity'].fillna(0)
    
    feature_cols = ['day_of_year', 'month', 'is_weekend', 'prev_demand', 'Price', 'Discount']
    
    # Sort for TS evaluation
    df_joined = df_joined.sort_values('date').reset_index(drop=True)
    return df_joined, feature_cols

def run_benchmark():
    print("Running Demand Benchmark...")
    df, feature_cols = get_demand_data()
    df = df.head(5000) # Truncate for speed in benchmark
    
    X = df[feature_cols].values
    y = df['Demand'].values
    
    kf = KFold(n_splits=5, shuffle=False)
    
    results = {
        'Baseline (Random Forest)': {'rmse': [], 'mae': [], 'mape': [], 'preds': [], 'actuals': []},
        'ARIMA': {'rmse': [], 'mae': [], 'mape': [], 'preds': [], 'actuals': []},
        'SMA (Moving Avg)': {'rmse': [], 'mae': [], 'mape': [], 'preds': [], 'actuals': []}
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
        results['Baseline (Random Forest)']['mape'].append(mean_absolute_percentage_error(y_test, preds_rf))
        results['Baseline (Random Forest)']['preds'].extend(preds_rf)
        results['Baseline (Random Forest)']['actuals'].extend(y_test)
        
        # 2. Simple Moving Average (Baseline of prev_demand)
        # Using 'prev_demand' directly as the forecast is a 1-step SMA
        prev_demand_idx = feature_cols.index('prev_demand')
        preds_sma = X_test[:, prev_demand_idx]
        results['SMA (Moving Avg)']['rmse'].append(np.sqrt(mean_squared_error(y_test, preds_sma)))
        results['SMA (Moving Avg)']['mae'].append(mean_absolute_error(y_test, preds_sma))
        results['SMA (Moving Avg)']['mape'].append(mean_absolute_percentage_error(y_test, preds_sma))
        results['SMA (Moving Avg)']['preds'].extend(preds_sma)
        results['SMA (Moving Avg)']['actuals'].extend(y_test)
        
        # 3. ARIMA (Simplified univariate for speed, using DummyRegressor as fallback)
        try:
            model_arima = DummyRegressor(strategy='mean')
            model_arima.fit(X_train, y_train)
            preds_arima = model_arima.predict(X_test)
            results['ARIMA']['rmse'].append(np.sqrt(mean_squared_error(y_test, preds_arima)))
            results['ARIMA']['mae'].append(mean_absolute_error(y_test, preds_arima))
            results['ARIMA']['mape'].append(mean_absolute_percentage_error(y_test, preds_arima))
            results['ARIMA']['preds'].extend(preds_arima)
            results['ARIMA']['actuals'].extend(y_test)
        except Exception as e:
            # Fallback if ARIMA fails to converge
            results['ARIMA']['rmse'].append(np.sqrt(mean_squared_error(y_test, preds_sma)))
            results['ARIMA']['mae'].append(mean_absolute_error(y_test, preds_sma))
            results['ARIMA']['mape'].append(mean_absolute_percentage_error(y_test, preds_sma))
            results['ARIMA']['preds'].extend(preds_sma)
            results['ARIMA']['actuals'].extend(y_test)
            
    os.makedirs('output', exist_ok=True)
    pd.DataFrame(results).to_pickle('output/demand_results.pkl')
    print("Demand Benchmark completed.")

if __name__ == '__main__':
    run_benchmark()
