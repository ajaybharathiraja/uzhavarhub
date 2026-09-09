import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def generate():
    print("Generating statistical tests and visualizations...")
    os.makedirs('output', exist_ok=True)
    summary = []
    
    # 1. Pricing
    if os.path.exists('output/pricing_results.pkl'):
        df_p = pd.read_pickle('output/pricing_results.pkl')
        base_mae = df_p['Baseline (Random Forest)'].apply(lambda x: x['mae'] if isinstance(x, dict) else np.nan)
        # We stored dicts in columns, let's parse it correctly since the dataframe was created from a nested dict
        # In benchmark scripts we did: pd.DataFrame(results).to_pickle
        
        # Actually, pd.DataFrame(dict) with lists makes rows=items in list.
        # So df_p['Baseline (Random Forest)'] is a series of dicts OR it's rows of lists.
        # Wait, the structure was: results = {'Model': {'rmse': [], ...}}
        # pd.DataFrame(results) will have columns 'Model' and rows 'rmse', 'mae', etc. where each cell is a list.
        
        # Let's extract properly
        models = df_p.columns
        metrics = df_p.index # ['rmse', 'mae', 'r2', 'preds', 'actuals']
        
        base_maes = np.array(df_p.loc['mae', 'Baseline (Random Forest)'])
        
        for m in models:
            mae_list = np.array(df_p.loc['mae', m])
            rmse_list = np.array(df_p.loc['rmse', m])
            r2_list = np.array(df_p.loc['r2', m])
            
            # Stat test vs baseline (mae)
            if m == 'Baseline (Random Forest)':
                p_val = "N/A"
            else:
                try:
                    _, p_val = stats.ttest_rel(mae_list, base_maes)
                except:
                    p_val = np.nan
                    
            summary.append({
                'Task': 'Price Prediction',
                'Model': m,
                'MAE': np.mean(mae_list),
                'RMSE': np.mean(rmse_list),
                'R2/MAPE': np.mean(r2_list),
                'p_value_vs_baseline': p_val
            })
            
        # Chart
        plt.figure(figsize=(8,5))
        maes = [np.mean(df_p.loc['mae', m]) for m in models]
        plt.bar(models, maes, color=['blue', 'orange', 'green'])
        plt.ylabel('Mean Absolute Error')
        plt.title('Price Prediction: Model Comparison')
        plt.savefig('output/chart_pricing_mae.png')
        plt.close()

    # 2. Demand
    if os.path.exists('output/demand_results.pkl'):
        df_d = pd.read_pickle('output/demand_results.pkl')
        models = df_d.columns
        base_maes = np.array(df_d.loc['mae', 'Baseline (Random Forest)'])
        
        for m in models:
            mae_list = np.array(df_d.loc['mae', m])
            rmse_list = np.array(df_d.loc['rmse', m])
            mape_list = np.array(df_d.loc['mape', m])
            
            if m == 'Baseline (Random Forest)':
                p_val = "N/A"
            else:
                try:
                    _, p_val = stats.ttest_rel(mae_list, base_maes)
                except:
                    p_val = np.nan
                    
            summary.append({
                'Task': 'Demand Forecasting',
                'Model': m,
                'MAE': np.mean(mae_list),
                'RMSE': np.mean(rmse_list),
                'R2/MAPE': np.mean(mape_list),
                'p_value_vs_baseline': p_val
            })
            
        # Chart
        plt.figure(figsize=(8,5))
        mapes = [np.mean(df_d.loc['mape', m]) for m in models]
        plt.bar(models, mapes, color=['blue', 'orange', 'green'])
        plt.ylabel('Mean Absolute Pct Error (MAPE)')
        plt.title('Demand Forecasting: Model Comparison')
        plt.savefig('output/chart_demand_mape.png')
        plt.close()

    # 3. Ablation
    if os.path.exists('output/ablation_pricing.pkl'):
        df_ap = pd.read_pickle('output/ablation_pricing.pkl')
        models = df_ap.columns
        base_maes = np.array(df_ap.loc['mae', 'Without Demand (Baseline)'])
        
        for m in models:
            mae_list = np.array(df_ap.loc['mae', m])
            rmse_list = np.array(df_ap.loc['rmse', m])
            
            if m == 'Without Demand (Baseline)':
                p_val = "N/A"
            else:
                try:
                    _, p_val = stats.ttest_rel(mae_list, base_maes)
                except:
                    p_val = np.nan
                    
            summary.append({
                'Task': 'Ablation (Pricing)',
                'Model': m,
                'MAE': np.mean(mae_list),
                'RMSE': np.mean(rmse_list),
                'R2/MAPE': 'N/A',
                'p_value_vs_baseline': p_val
            })

    if os.path.exists('output/ablation_crop.pkl'):
        df_ac = pd.read_pickle('output/ablation_crop.pkl')
        models = df_ac.columns
        base_profit = np.array(df_ac.loc['profit', 'Naive Suitability'])
        
        for m in models:
            profit_list = np.array(df_ac.loc['profit', m])
            
            if m == 'Naive Suitability':
                p_val = "N/A"
            else:
                try:
                    _, p_val = stats.ttest_rel(profit_list, base_profit)
                except:
                    p_val = np.nan
                    
            summary.append({
                'Task': 'Ablation (Crop Rec)',
                'Model': m,
                'MAE': 'N/A',
                'RMSE': 'N/A',
                'R2/MAPE': f"Profit: {np.mean(profit_list):.2f}",
                'p_value_vs_baseline': p_val
            })
            
    df_out = pd.DataFrame(summary)
    df_out.to_csv('output/results_summary.csv', index=False)
    print("results_summary.csv and charts saved to output/ folder.")

if __name__ == '__main__':
    generate()
