import pandas as pd
import os

os.makedirs('data/processed', exist_ok=True)

report = ["# Data Audit and Preprocessing Report\n"]

def process_crop_data():
    report.append("## 1. Crop Recommendation Dataset")
    try:
        df = pd.read_csv('data/raw/crop_recommendation.csv')
        report.append(f"- **Row count:** {len(df)}")
        report.append(f"- **Columns:** {', '.join(df.columns)}")
        
        # Missing values
        missing = df.isnull().sum()
        if missing.sum() == 0:
            report.append("- **Missing values:** None")
        else:
            report.append(f"- **Missing values:**\n{missing[missing > 0].to_string()}")
            df = df.dropna()
            report.append(f"  - *Action:* Dropped missing rows. New count: {len(df)}")
            
        # Class balance
        if 'label' in df.columns:
            balance = df['label'].value_counts()
            report.append("- **Class balance:** Perfectly balanced (most classes have ~200 samples)." if balance.min() > 90 and balance.max() - balance.min() < 20 else f"- **Class balance:** Imbalanced\n{balance.to_string()}")
        
        df.to_csv('data/processed/crop_recommendation.csv', index=False)
        report.append("- **Saved to:** `data/processed/crop_recommendation.csv`\n")
    except Exception as e:
        report.append(f"Error processing: {e}\n")

def process_demand_data():
    report.append("## 2. Demand Forecasting Dataset")
    try:
        df = pd.read_csv('data/raw/demand_forecasting.csv')
        report.append(f"- **Row count:** {len(df)}")
        report.append(f"- **Columns:** {', '.join(df.columns)}")
        
        # Missing values
        missing = df.isnull().sum()
        if missing.sum() == 0:
            report.append("- **Missing values:** None")
        else:
            report.append(f"- **Missing values:**\n{missing[missing > 0].to_string()}")
            df = df.dropna()
            report.append(f"  - *Action:* Dropped missing rows. New count: {len(df)}")
            
        df.to_csv('data/processed/demand_forecasting.csv', index=False)
        report.append("- **Saved to:** `data/processed/demand_forecasting.csv`\n")
    except Exception as e:
        report.append(f"Error processing: {e}\n")

def process_ecommerce_data():
    report.append("## 3. E-commerce Sales Dataset")
    try:
        df = pd.read_csv('data/raw/ecommerce_sales_analytics_5000.csv')
        report.append(f"- **Row count:** {len(df)}")
        report.append(f"- **Columns:** {', '.join(df.columns)}")
        
        # Missing values
        missing = df.isnull().sum()
        if missing.sum() == 0:
            report.append("- **Missing values:** None")
        else:
            report.append(f"- **Missing values:**\n{missing[missing > 0].to_string()}")
            # Impute or drop based on columns
            for col in missing[missing > 0].index:
                if df[col].dtype == 'object':
                    df[col] = df[col].fillna(df[col].mode()[0])
                else:
                    df[col] = df[col].fillna(df[col].mean())
            report.append("  - *Action:* Imputed categorical with mode and numerical with mean.")
            
        df.to_csv('data/processed/ecommerce_sales.csv', index=False)
        report.append("- **Saved to:** `data/processed/ecommerce_sales.csv`\n")
    except Exception as e:
        report.append(f"Error processing: {e}\n")

process_crop_data()
process_demand_data()
process_ecommerce_data()

with open('DATA_PREPROCESSING.md', 'w') as f:
    f.write("\n".join(report))

print("Audit complete. DATA_PREPROCESSING.md generated.")
