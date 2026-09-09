import os
import json
import numpy as np
import pandas as pd
import joblib
import shap
import warnings

warnings.filterwarnings('ignore')

def run_explainability_and_uncertainty():
    print("--- Running Risk-Aware AI & Explainability ---")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. SHAP & Counterfactuals for Crop Recommendation
    crop_model_path = os.path.join(script_dir, '../../ai_services/models/crop_model.pkl')
    crop_data_path = os.path.join(script_dir, '../../data/processed/crop_recommendation.csv')
    
    if os.path.exists(crop_model_path) and os.path.exists(crop_data_path):
        crop_model = joblib.load(crop_model_path)
        df_crop = pd.read_csv(crop_data_path)
        X = df_crop[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']].values
        y = df_crop['label'].values
        features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        
        # Sample for SHAP
        X_sample = X[:100]
        explainer = shap.TreeExplainer(crop_model)
        shap_values = explainer.shap_values(X_sample)
        
        # Global Feature Importance from RF
        importances = crop_model.feature_importances_
        feature_importance = {features[i]: float(importances[i]) for i in range(len(features))}
        
        # Counterfactual Analysis (Example: Reduce rainfall by 30% for a specific Rice instance)
        # Find a rice instance
        rice_idx = np.where(y == 'rice')[0][0]
        base_instance = X[rice_idx].copy()
        base_pred_idx = crop_model.predict([base_instance])[0]
        
        # Counterfactual: Drop rainfall by 30% (index 6 is rainfall)
        cf_instance = base_instance.copy()
        cf_instance[6] *= 0.70
        cf_pred_idx = crop_model.predict([cf_instance])[0]
        
        counterfactual_result = {
            'Base_Prediction': str(base_pred_idx),
            'Counterfactual_Prediction': str(cf_pred_idx),
            'Intervention': 'Reduced rainfall by 30%'
        }
    else:
        feature_importance = {}
        counterfactual_result = {}

    # 2. Uncertainty Estimation (Prediction Intervals) for Demand & Pricing
    # We use the variance across the trees in the Random Forest to estimate uncertainty
    demand_model_path = os.path.join(script_dir, '../../ai_services/models/demand_model.pkl')
    demand_data_path = os.path.join(script_dir, '../../data/processed/demand_forecasting.csv')
    
    uncertainty_results = {}
    
    if os.path.exists(demand_model_path) and os.path.exists(demand_data_path):
        demand_model = joblib.load(demand_model_path)
        df_demand = pd.read_csv(demand_data_path)
        df_demand['day_of_year'] = pd.to_datetime(df_demand['Date']).dt.dayofyear
        df_demand['prev_demand'] = df_demand.groupby(['Product ID'])['Demand'].shift(1).fillna(0)
        X_dem = df_demand[['day_of_year', 'prev_demand', 'Price', 'Discount']].values[:50]
        
        # Predict using all trees to get standard deviation
        preds = np.array([tree.predict(X_dem) for tree in demand_model.estimators_])
        mean_preds = np.mean(preds, axis=0)
        std_preds = np.std(preds, axis=0)
        
        # 95% Prediction Interval bounds (assuming normal distribution of tree predictions)
        lower_bounds = mean_preds - 1.96 * std_preds
        upper_bounds = mean_preds + 1.96 * std_preds
        
        uncertainty_results['Demand'] = {
            'Sample_Mean_Prediction': float(mean_preds[0]),
            'Sample_Lower_95PI': float(lower_bounds[0]),
            'Sample_Upper_95PI': float(upper_bounds[0]),
            'Risk_Interval_Width': float(upper_bounds[0] - lower_bounds[0])
        }

    out_dir = os.path.join(script_dir, '../../paper/results/explainability')
    os.makedirs(out_dir, exist_ok=True)
    
    results = {
        'Feature_Importance': feature_importance,
        'Counterfactual': counterfactual_result,
        'Uncertainty_Estimation': uncertainty_results
    }
    
    with open(os.path.join(out_dir, 'risk_explainability_report.json'), 'w') as f:
        json.dump(results, f, indent=4)
        
    print("Risk & Explainability report saved.")

if __name__ == '__main__':
    run_explainability_and_uncertainty()
