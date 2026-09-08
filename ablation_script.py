import os
import json
import numpy as np
import pandas as pd
import warnings
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error, r2_score
from scipy import stats

warnings.filterwarnings('ignore')

def cohens_d(group1, group2):
    diff = group1 - group2
    return np.mean(diff) / np.std(diff, ddof=1) if np.std(diff, ddof=1) != 0 else 0

def run_ablation():
    print("--- Running Ablation Study on Dynamic Pricing Model ---")
    ecommerce_path = 'data/processed/ecommerce_sales.csv'
    demand_path = 'data/processed/demand_forecasting.csv'
    
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
    
    # Condition A: With Demand Feature
    feature_cols_A = ['day_of_year', 'month', 'is_weekend', 'quantity', 'Demand']
    X_A = df_joined[feature_cols_A].values
    
    # Condition B: Without Demand Feature
    feature_cols_B = ['day_of_year', 'month', 'is_weekend', 'quantity']
    X_B = df_joined[feature_cols_B].values
    
    y = df_joined['unit_price'].values
    
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    rmses_A = []
    r2s_A = []
    
    rmses_B = []
    r2s_B = []
    
    for train_idx, test_idx in kf.split(X_A):
        # Condition A
        X_train_A, X_test_A = X_A[train_idx], X_A[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        model_A = RandomForestRegressor(n_estimators=50, random_state=42)
        model_A.fit(X_train_A, y_train)
        preds_A = model_A.predict(X_test_A)
        
        rmses_A.append(np.sqrt(mean_squared_error(y_test, preds_A)))
        r2s_A.append(r2_score(y_test, preds_A))
        
        # Condition B
        X_train_B, X_test_B = X_B[train_idx], X_B[test_idx]
        
        model_B = RandomForestRegressor(n_estimators=50, random_state=42)
        model_B.fit(X_train_B, y_train)
        preds_B = model_B.predict(X_test_B)
        
        rmses_B.append(np.sqrt(mean_squared_error(y_test, preds_B)))
        r2s_B.append(r2_score(y_test, preds_B))

    # Condition A stats
    rmse_mean_A = float(np.mean(rmses_A))
    r2_mean_A = float(np.mean(r2s_A))
    
    # Condition B stats
    rmse_mean_B = float(np.mean(rmses_B))
    r2_mean_B = float(np.mean(r2s_B))
    
    # Statistical test on RMSE
    # Paired t-test between RMSE of A and B
    # Null hypothesis: Mean difference is 0.
    t_stat_rmse, p_val_rmse = stats.ttest_rel(rmses_B, rmses_A)
    # cohens_d: positive means B has higher RMSE (worse performance without demand)
    d_val_rmse = cohens_d(np.array(rmses_B), np.array(rmses_A))

    # Statistical test on R2
    t_stat_r2, p_val_r2 = stats.ttest_rel(r2s_A, r2s_B)
    d_val_r2 = cohens_d(np.array(r2s_A), np.array(r2s_B))

    results = {
        "Condition_A_With_Demand": {
            "Features": feature_cols_A,
            "Test_RMSE_Mean": rmse_mean_A,
            "Test_R2_Mean": r2_mean_A
        },
        "Condition_B_Without_Demand": {
            "Features": feature_cols_B,
            "Test_RMSE_Mean": rmse_mean_B,
            "Test_R2_Mean": r2_mean_B
        },
        "Statistical_Significance": {
            "RMSE_B_vs_A": {
                "p_value": float(p_val_rmse),
                "cohens_d": float(d_val_rmse),
                "interpretation": "Positive Cohen's d means removing Demand increased RMSE (worse error)."
            },
            "R2_A_vs_B": {
                "p_value": float(p_val_r2),
                "cohens_d": float(d_val_r2),
                "interpretation": "Positive Cohen's d means adding Demand increased R2 (better fit)."
            }
        }
    }
    
    os.makedirs('paper/results', exist_ok=True)
    with open('paper/results/ablation_pricing_demand.json', 'w') as f:
        json.dump(results, f, indent=4)
        
    print("Ablation study complete! Results saved to paper/results/ablation_pricing_demand.json")
    print(f"Condition A R2: {r2_mean_A:.4f}, Condition B R2: {r2_mean_B:.4f}")
    print(f"p-value for R2 difference: {p_val_r2:.4e}")

if __name__ == '__main__':
    run_ablation()
