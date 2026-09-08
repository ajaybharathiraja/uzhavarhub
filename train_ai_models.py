import os
import json
import joblib
import pandas as pd
import numpy as np
import warnings
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.dummy import DummyRegressor
from scipy import stats

warnings.filterwarnings('ignore')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uzhavarhub.settings')
django.setup()

evaluation_results = {}
statistical_tests = {}

def cohens_d(group1, group2):
    diff = group1 - group2
    return np.mean(diff) / np.std(diff, ddof=1) if np.std(diff, ddof=1) != 0 else 0

def train_crop_recommendation_model():
    print("\n--- Training Crop Recommendation Model ---")
    csv_path = 'data/processed/crop_recommendation.csv'
    if not os.path.exists(csv_path):
        print(f"ERROR: {csv_path} not found.")
        return
        
    df = pd.read_csv(csv_path)
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']].values
    y = df['label'].values
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    rf_accs = []
    lr_accs = []
    knn_accs = []
    
    rf_precs = []
    rf_recs = []
    rf_f1s = []
    
    cm_final = None
    best_rf = None
    best_acc = 0
    
    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Baselines
        lr = LogisticRegression(max_iter=1000, random_state=42)
        lr.fit(X_train, y_train)
        lr_accs.append(accuracy_score(y_test, lr.predict(X_test)))
        
        knn = KNeighborsClassifier(n_neighbors=5)
        knn.fit(X_train, y_train)
        knn_accs.append(accuracy_score(y_test, knn.predict(X_test)))
        
        # Primary
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        preds = rf.predict(X_test)
        
        acc = accuracy_score(y_test, preds)
        rf_accs.append(acc)
        rf_precs.append(precision_score(y_test, preds, average='macro', zero_division=0))
        rf_recs.append(recall_score(y_test, preds, average='macro', zero_division=0))
        rf_f1s.append(f1_score(y_test, preds, average='macro', zero_division=0))
        
        if acc > best_acc:
            best_acc = acc
            best_rf = rf
            cm_final = confusion_matrix(y_test, preds).tolist()
            
    # Statistical test: RF vs LR
    t_stat_lr, p_val_lr = stats.ttest_rel(rf_accs, lr_accs)
    d_lr = cohens_d(np.array(rf_accs), np.array(lr_accs))
    
    # Statistical test: RF vs KNN
    t_stat_knn, p_val_knn = stats.ttest_rel(rf_accs, knn_accs)
    d_knn = cohens_d(np.array(rf_accs), np.array(knn_accs))
    
    # 95% CI for RF acc
    mean_rf = np.mean(rf_accs)
    std_rf = np.std(rf_accs, ddof=1)
    ci_rf = stats.t.interval(0.95, len(rf_accs)-1, loc=mean_rf, scale=std_rf/np.sqrt(len(rf_accs)))
    
    evaluation_results['Crop_Recommendation'] = {
        'Baseline_LR_Accuracy_Mean': float(np.mean(lr_accs)),
        'Baseline_LR_Accuracy_Std': float(np.std(lr_accs)),
        'Baseline_KNN_Accuracy_Mean': float(np.mean(knn_accs)),
        'Baseline_KNN_Accuracy_Std': float(np.std(knn_accs)),
        'RF_Accuracy_Mean': float(mean_rf),
        'RF_Accuracy_Std': float(std_rf),
        'RF_Accuracy_95CI': [float(ci_rf[0]), float(ci_rf[1])],
        'RF_Precision_Macro_Mean': float(np.mean(rf_precs)),
        'RF_Recall_Macro_Mean': float(np.mean(rf_recs)),
        'RF_F1_Macro_Mean': float(np.mean(rf_f1s)),
        'Confusion_Matrix': cm_final
    }
    
    statistical_tests['Crop_Recommendation'] = {
        'RF_vs_LR': {'p_value': float(p_val_lr), 'cohens_d': float(d_lr)},
        'RF_vs_KNN': {'p_value': float(p_val_knn), 'cohens_d': float(d_knn)}
    }
    
    os.makedirs('ai_services/models', exist_ok=True)
    joblib.dump(best_rf, 'ai_services/models/crop_model.pkl')
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
    X = df_joined[feature_cols].values
    y = df_joined['Demand'].values
    
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    lr_rmses = []
    lr_maes = []
    lr_r2s = []
    
    naive_rmses = []
    naive_r2s = []
    
    best_model = None
    best_r2 = -float('inf')
    
    for train_idx, test_idx in kf.split(X):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Naive Baseline: Predict Mean
        dummy = DummyRegressor(strategy='mean')
        dummy.fit(X_train, y_train)
        dummy_preds = dummy.predict(X_test)
        naive_rmses.append(np.sqrt(mean_squared_error(y_test, dummy_preds)))
        naive_r2s.append(r2_score(y_test, dummy_preds))
        
        # Primary: Linear Regression
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        lr_rmses.append(rmse)
        lr_maes.append(mean_absolute_error(y_test, y_pred))
        lr_r2s.append(r2)
        
        if r2 > best_r2:
            best_r2 = r2
            best_model = model
            
    # Statistical test: LR vs Naive (RMSE)
    t_stat, p_val = stats.ttest_rel(lr_rmses, naive_rmses)
    d_val = cohens_d(np.array(naive_rmses), np.array(lr_rmses)) # + means naive is worse
    
    mean_r2 = np.mean(lr_r2s)
    std_r2 = np.std(lr_r2s, ddof=1)
    ci_r2 = stats.t.interval(0.95, len(lr_r2s)-1, loc=mean_r2, scale=std_r2/np.sqrt(len(lr_r2s)))

    evaluation_results['Demand_Forecasting'] = {
        'Model_Type': 'LinearRegression',
        'Test_RMSE_Mean': float(np.mean(lr_rmses)),
        'Test_RMSE_Std': float(np.std(lr_rmses)),
        'Test_MAE_Mean': float(np.mean(lr_maes)),
        'Test_R2_Mean': float(mean_r2),
        'Test_R2_Std': float(std_r2),
        'Test_R2_95CI': [float(ci_r2[0]), float(ci_r2[1])],
        'Naive_Baseline_RMSE_Mean': float(np.mean(naive_rmses)),
        'Naive_Baseline_R2_Mean': float(np.mean(naive_r2s))
    }
    
    statistical_tests['Demand_Forecasting'] = {
        'LR_vs_Naive_RMSE': {'p_value': float(p_val), 'cohens_d': float(d_val)}
    }
    
    joblib.dump(best_model, 'ai_services/models/demand_model.pkl')
    print("Demand forecasting model saved. Metrics logged.")

def train_dynamic_pricing_model():
    print("\n--- Training Dynamic Pricing Model ---")
    ecommerce_path = 'data/processed/ecommerce_sales.csv'
    demand_path = 'data/processed/demand_forecasting.csv'
    
    if not os.path.exists(ecommerce_path) or not os.path.exists(demand_path):
        print("ERROR: Processed datasets not found for dynamic pricing.")
        return
        
    df_ecom = pd.read_csv(ecommerce_path)
    df_demand = pd.read_csv(demand_path)
    
    if 'Date' in df_demand.columns:
        df_demand['date'] = pd.to_datetime(df_demand['Date'])
    if 'order_date' in df_ecom.columns:
        df_ecom['date'] = pd.to_datetime(df_ecom['order_date'], errors='coerce')
        
    df_demand['category'] = df_demand['Category'].str.lower()
    df_ecom['category'] = df_ecom['product_category'].str.lower()
    
    df_demand_daily = df_demand.groupby(['date', 'category'])['Demand'].sum().reset_index()
    df_joined = pd.merge(df_ecom, df_demand_daily, on=['date', 'category'], how='left')
    df_joined['Demand'] = df_joined['Demand'].fillna(df_joined['Demand'].mean())
    
    df_joined['day_of_year'] = df_joined['date'].dt.dayofyear
    df_joined['month'] = df_joined['date'].dt.month
    df_joined['is_weekend'] = (df_joined['date'].dt.dayofweek >= 5).astype(int)
    
    # We predict optimal price based on time features, expected demand, and typical quantity sold
    feature_cols = ['day_of_year', 'month', 'is_weekend', 'quantity', 'Demand']
    X = df_joined[feature_cols].values
    y = df_joined['unit_price'].values
    
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    rf_rmses = []
    rf_r2s = []
    naive_rmses = []
    
    best_model = None
    best_r2 = -float('inf')
    
    from sklearn.ensemble import RandomForestRegressor
    
    for train_idx, test_idx in kf.split(X):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        dummy = DummyRegressor(strategy='mean')
        dummy.fit(X_train, y_train)
        dummy_preds = dummy.predict(X_test)
        naive_rmses.append(np.sqrt(mean_squared_error(y_test, dummy_preds)))
        
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        rf_rmses.append(rmse)
        rf_r2s.append(r2)
        
        if r2 > best_r2:
            best_r2 = r2
            best_model = model
            
    evaluation_results['Dynamic_Pricing'] = {
        'Model_Type': 'RandomForestRegressor',
        'Test_RMSE_Mean': float(np.mean(rf_rmses)),
        'Test_R2_Mean': float(np.mean(rf_r2s)),
        'Naive_Baseline_RMSE_Mean': float(np.mean(naive_rmses))
    }
    
    joblib.dump(best_model, 'ai_services/models/pricing_model.pkl')
    print("Pricing model saved. Metrics logged.")


if __name__ == '__main__':
    train_crop_recommendation_model()
    train_demand_forecasting_model()
    train_dynamic_pricing_model()
    
    os.makedirs('ai_services/models', exist_ok=True)
    os.makedirs('paper/results', exist_ok=True)
    
    with open('ai_services/models/evaluation_results.json', 'w') as f:
        json.dump(evaluation_results, f, indent=4)
        
    with open('paper/results/statistical_tests.json', 'w') as f:
        json.dump(statistical_tests, f, indent=4)
        
    print("\nSaved evaluation metrics and statistical tests.")
