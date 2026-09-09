import joblib
import pandas as pd
import numpy as np

def explain_model():
    print("Loading Crop Recommendation model...")
    model = joblib.load('ai_services/models/crop_model.pkl')
    
    # We will just get feature importances directly from Random Forest
    features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    importances = model.feature_importances_
    
    # Sort them
    feature_importance = pd.DataFrame({'Feature': features, 'Importance': importances})
    feature_importance = feature_importance.sort_values(by='Importance', ascending=False)
    
    print("\nFeature Importances (Proxy for SHAP global explainability):")
    for idx, row in feature_importance.iterrows():
        print(f"{row['Feature']}: {row['Importance']:.4f}")

if __name__ == '__main__':
    explain_model()
