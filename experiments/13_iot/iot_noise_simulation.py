import os
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold
import warnings

warnings.filterwarnings('ignore')

def run_iot_noise_simulation():
    print("--- Running IoT Sensor Noise Robustness Simulation ---")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '../../data/processed/crop_recommendation.csv')
    
    if not os.path.exists(csv_path):
        print(f"Data not found at {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']].values
    y = df['label'].values
    
    noise_levels = [0.0, 0.05, 0.10, 0.15, 0.20]
    results = {}
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for noise in noise_levels:
        np.random.seed(42)
        X_noisy = X * (1 + np.random.normal(0, noise, X.shape))
        
        accs = []
        for train_idx, test_idx in skf.split(X_noisy, y):
            X_train, X_test = X_noisy[train_idx], X_noisy[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            rf = RandomForestClassifier(n_estimators=50, random_state=42)
            rf.fit(X_train, y_train)
            accs.append(accuracy_score(y_test, rf.predict(X_test)))
            
        mean_acc = np.mean(accs)
        results[f"Noise_{int(noise*100)}pct"] = float(mean_acc)
        print(f"Accuracy with {int(noise*100)}% simulated sensor noise: {mean_acc:.4f}")
        
    out_dir = os.path.join(script_dir, '../../paper/results/iot_simulation')
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'noise_robustness.json'), 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == '__main__':
    run_iot_noise_simulation()
