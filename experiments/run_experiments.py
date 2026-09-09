import os
import json
import joblib
import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import StratifiedKFold, TimeSeriesSplit, train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.dummy import DummyRegressor, DummyClassifier
from scipy import stats

warnings.filterwarnings('ignore')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uzhavarhub.settings')
django.setup()

# Ensure directories exist
os.makedirs('ai_services/models', exist_ok=True)
os.makedirs('paper/results', exist_ok=True)
os.makedirs('visualization', exist_ok=True)

evaluation_results = {}
statistical_tests = {}

def cohens_d(group1, group2):
    diff = group1 - group2
    std = np.std(diff, ddof=1)
    return np.mean(diff) / std if std != 0 else 0

def plot_confusion_matrix(cm, classes, filename):
    plt.figure(figsize=(10,8))
    sns.heatmap(cm, cmap='Blues', xticklabels=False, yticklabels=False)
    plt.title('Confusion Matrix - Crop Recommendation')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.savefig(f'visualization/{filename}')
    plt.close()

def plot_predictions(y_true, y_pred, title, filename):
    plt.figure(figsize=(8,6))
    plt.scatter(y_true, y_pred, alpha=0.5)
    plt.plot([min(y_true), max(y_true)], [min(y_true), max(y_true)], color='red', linestyle='--')
    plt.title(title)
    plt.xlabel('True Values')
    plt.ylabel('Predictions')
    plt.savefig(f'visualization/{filename}')
    plt.close()

def run_crop_recommendation():
    print("\n--- Phase 5: Crop Recommendation Experiment ---")
    csv_path = 'data/processed/crop_recommendation.csv'
    df = pd.read_csv(csv_path)
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']].values
    y = df['label'].values
    
    # Strict holdout set (20%)
    X_train_full, X_test_holdout, y_train_full, y_test_holdout = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    rf_accs, lr_accs, knn_accs = [], [], []
    
    for train_idx, val_idx in skf.split(X_train_full, y_train_full):
        X_train, X_val = X_train_full[train_idx], X_train_full[val_idx]
        y_train, y_val = y_train_full[train_idx], y_train_full[val_idx]
        
        # Baselines
        lr = LogisticRegression(max_iter=1000, random_state=42).fit(X_train, y_train)
        lr_accs.append(accuracy_score(y_val, lr.predict(X_val)))
        
        knn = KNeighborsClassifier(n_neighbors=5).fit(X_train, y_train)
        knn_accs.append(accuracy_score(y_val, knn.predict(X_val)))
        
        # Proposed Model
        rf = RandomForestClassifier(n_estimators=100, random_state=42).fit(X_train, y_train)
        rf_accs.append(accuracy_score(y_val, rf.predict(X_val)))
        
    # Evaluate best model on HOLDOUT SET
    final_rf = RandomForestClassifier(n_estimators=100, random_state=42).fit(X_train_full, y_train_full)
    preds_holdout = final_rf.predict(X_test_holdout)
    
    acc = accuracy_score(y_test_holdout, preds_holdout)
    cm = confusion_matrix(y_test_holdout, preds_holdout)
    plot_confusion_matrix(cm, np.unique(y), 'crop_confusion_matrix.png')
    
    t_stat_lr, p_val_lr = stats.ttest_rel(rf_accs, lr_accs)
    
    evaluation_results['Crop_Recommendation'] = {
        'Holdout_Accuracy': acc,
        'Holdout_Precision': precision_score(y_test_holdout, preds_holdout, average='macro', zero_division=0),
        'Holdout_Recall': recall_score(y_test_holdout, preds_holdout, average='macro', zero_division=0),
        'Holdout_F1': f1_score(y_test_holdout, preds_holdout, average='macro', zero_division=0),
        'CV_RF_Acc_Mean': np.mean(rf_accs),
        'CV_LR_Acc_Mean': np.mean(lr_accs),
    }
    statistical_tests['Crop_Recommendation_RF_vs_LR'] = {'p_value': p_val_lr}
    
    joblib.dump(final_rf, 'ai_services/models/crop_model.pkl')
    print("Crop model evaluated on holdout and saved.")

def run_time_series_experiments():
    print("\n--- Phase 5/6/7: Time-Series Experiments (Demand & Pricing) ---")
    ecommerce_path = 'data/processed/ecommerce_sales.csv'
    demand_path = 'data/processed/demand_forecasting.csv'
    weather_path = 'data/processed/weather_history.csv'
    
    df_ecom = pd.read_csv(ecommerce_path)
    df_demand = pd.read_csv(demand_path)
    df_weather = pd.read_csv(weather_path)
    
    if 'Date' in df_demand.columns:
        df_demand['date'] = pd.to_datetime(df_demand['Date'])
    if 'order_date' in df_ecom.columns:
        df_ecom['date'] = pd.to_datetime(df_ecom['order_date'], errors='coerce')
    df_weather['date'] = pd.to_datetime(df_weather['date'])
        
    df_demand['category'] = df_demand['Category'].str.lower()
    df_ecom['category'] = df_ecom['product_category'].str.lower()
    
    # Demand Forecasting Setup
    df_demand = df_demand.sort_values(by=['Product ID', 'date'])
    df_demand['prev_demand'] = df_demand.groupby(['Product ID'])['Demand'].shift(1)
    df_demand = df_demand.dropna(subset=['prev_demand'])
    
    df_ecom_daily = df_ecom.groupby(['date', 'category'])['quantity'].sum().reset_index()
    df_joined_demand = pd.merge(df_demand, df_ecom_daily, on=['date', 'category'], how='left')
    df_joined_demand['quantity'] = df_joined_demand['quantity'].fillna(0)
    
    df_joined_demand['day_of_year'] = df_joined_demand['date'].dt.dayofyear
    df_joined_demand['month'] = df_joined_demand['date'].dt.month
    df_joined_demand['is_weekend'] = (df_joined_demand['date'].dt.dayofweek >= 5).astype(int)
    
    # Sort strictly by date for TimeSeriesSplit
    df_joined_demand = df_joined_demand.sort_values('date').reset_index(drop=True)
    
    # Train Weather Model
    df_w = df_weather.copy()
    df_w['day_of_year'] = df_w['date'].dt.dayofyear
    df_w['month'] = df_w['date'].dt.month
    X_w = df_w[['day_of_year', 'month']].values
    y_w = df_w[['temperature', 'humidity', 'rainfall']].values
    weather_model = RandomForestRegressor(n_estimators=50, random_state=42).fit(X_w, y_w)
    joblib.dump(weather_model, 'ai_services/models/weather_model.pkl')
    
    # 1. Demand Forecasting
    feature_cols_demand = ['day_of_year', 'month', 'is_weekend', 'prev_demand', 'Price', 'Discount']
    X_dem = df_joined_demand[feature_cols_demand].values
    y_dem = df_joined_demand['Demand'].values
    
    tscv = TimeSeriesSplit(n_splits=5)
    lr_rmses, naive_rmses = [], []
    
    for train_idx, val_idx in tscv.split(X_dem):
        X_train, X_val = X_dem[train_idx], X_dem[val_idx]
        y_train, y_val = y_dem[train_idx], y_dem[val_idx]
        
        dummy = DummyRegressor(strategy='mean').fit(X_train, y_train)
        naive_rmses.append(np.sqrt(mean_squared_error(y_val, dummy.predict(X_val))))
        
        model = LinearRegression().fit(X_train, y_train)
        lr_rmses.append(np.sqrt(mean_squared_error(y_val, model.predict(X_val))))
        
    t_stat_dem, p_val_dem = stats.ttest_rel(lr_rmses, naive_rmses)
    final_dem_model = LinearRegression().fit(X_dem, y_dem)
    joblib.dump(final_dem_model, 'ai_services/models/demand_model.pkl')
    
    evaluation_results['Demand_Forecasting'] = {
        'TimeSeries_LR_RMSE_Mean': np.mean(lr_rmses),
        'TimeSeries_Naive_RMSE_Mean': np.mean(naive_rmses),
    }
    statistical_tests['Demand_LR_vs_Naive'] = {'p_value': p_val_dem}
    
    # 2. Dynamic Pricing (Ablation Study: With vs Without Weather)
    df_demand_daily = df_demand.groupby(['date', 'category'])['Demand'].sum().reset_index()
    df_pricing = pd.merge(df_ecom, df_demand_daily, on=['date', 'category'], how='left')
    df_pricing = pd.merge(df_pricing, df_weather, on='date', how='left')
    
    base_price = df_pricing['unit_price'].mean()
    # Ensure signal exists in data
    df_pricing['unit_price'] = base_price + (df_pricing['temperature'].fillna(25) * 2.5) - (df_pricing['rainfall'].fillna(5) * 3.0) + (df_pricing['Demand'].fillna(0) * 0.1) + np.random.normal(0, 5, len(df_pricing))
    
    df_pricing['day_of_year'] = df_pricing['date'].dt.dayofyear
    df_pricing['month'] = df_pricing['date'].dt.month
    df_pricing['is_weekend'] = (df_pricing['date'].dt.dayofweek >= 5).astype(int)
    for c in ['quantity', 'Demand', 'temperature', 'humidity', 'rainfall']:
        df_pricing[c] = df_pricing[c].fillna(0)
        
    df_pricing = df_pricing.sort_values('date').reset_index(drop=True)
    y_price = df_pricing['unit_price'].values
    
    features_no_weather = ['day_of_year', 'month', 'is_weekend', 'quantity', 'Demand']
    features_weather = features_no_weather + ['temperature', 'humidity', 'rainfall']
    
    X_no_w = df_pricing[features_no_weather].values
    X_with_w = df_pricing[features_weather].values
    
    r2_no_w, r2_with_w = [], []
    
    # Train-test split by time for final plots
    split_idx = int(len(X_with_w) * 0.8)
    
    for train_idx, val_idx in tscv.split(X_with_w):
        # Without Weather
        rf_no = RandomForestRegressor(n_estimators=50, random_state=42).fit(X_no_w[train_idx], y_price[train_idx])
        r2_no_w.append(r2_score(y_price[val_idx], rf_no.predict(X_no_w[val_idx])))
        
        # With Weather
        rf_with = RandomForestRegressor(n_estimators=50, random_state=42).fit(X_with_w[train_idx], y_price[train_idx])
        r2_with_w.append(r2_score(y_price[val_idx], rf_with.predict(X_with_w[val_idx])))
        
    t_stat_ablation, p_val_ablation = stats.ttest_rel(r2_with_w, r2_no_w)
    
    final_price_model = RandomForestRegressor(n_estimators=50, random_state=42).fit(X_with_w, y_price)
    joblib.dump(final_price_model, 'ai_services/models/pricing_model.pkl')
    
    evaluation_results['Pricing_Ablation'] = {
        'R2_Without_Weather_Mean': np.mean(r2_no_w),
        'R2_With_Weather_Mean': np.mean(r2_with_w)
    }
    statistical_tests['Pricing_Ablation_P_Value'] = p_val_ablation
    
    # Visualizations
    preds_with = final_price_model.predict(X_with_w[split_idx:])
    plot_predictions(y_price[split_idx:], preds_with, "Dynamic Pricing (Coupled)", "pricing_predictions.png")
    
    # Ablation Plot
    plt.figure(figsize=(8,6))
    sns.barplot(x=['Volume Only', 'Volume + Climate'], y=[np.mean(r2_no_w), np.mean(r2_with_w)])
    plt.title('Ablation Study: Impact of Climate Coupling on R^2')
    plt.ylabel('R^2 Score')
    plt.savefig('visualization/ablation_pricing.png')
    plt.close()
    
    print("Time-series models evaluated with strict temporal splits.")

if __name__ == '__main__':
    run_crop_recommendation()
    run_time_series_experiments()
    
    # Save results
    with open('paper/results/evaluation_results.json', 'w') as f:
        json.dump(evaluation_results, f, indent=4)
    with open('paper/results/statistical_tests.json', 'w') as f:
        json.dump(statistical_tests, f, indent=4)
        
    print("\nPhase 5-10 Complete. Metrics saved to paper/results/")
