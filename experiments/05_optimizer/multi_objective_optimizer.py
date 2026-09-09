import os
import json
import numpy as np
import pandas as pd
from itertools import product

class RiskAwareOptimizer:
    def __init__(self):
        # Weights derived from literature (e.g., FAO agricultural decision-making framework)
        # Weights should sum to 1.0 for normalized calculation.
        self.default_weights = {
            'agronomic_suitability': 0.35,  # w1
            'expected_profit': 0.25,        # w2
            'expected_demand': 0.15,        # w3
            'climate_risk': -0.10,          # w4 (Negative impact)
            'water_requirement': -0.10,     # w5 (Negative impact)
            'environmental_impact': -0.05   # w6 (Negative impact)
        }
        
    def evaluate_crop(self, crop_metrics, weights=None):
        if weights is None:
            weights = self.default_weights
            
        score = (
            weights['agronomic_suitability'] * crop_metrics['agronomic_suitability'] +
            weights['expected_profit'] * crop_metrics['expected_profit'] +
            weights['expected_demand'] * crop_metrics['expected_demand'] +
            weights['climate_risk'] * crop_metrics['climate_risk'] +
            weights['water_requirement'] * crop_metrics['water_requirement'] +
            weights['environmental_impact'] * crop_metrics['environmental_impact']
        )
        return score

    def optimize(self, crops_data, weights=None):
        """
        Takes a dict of crops and their normalized metrics (0 to 1 scale) and returns the ranked list.
        """
        results = []
        for crop_name, metrics in crops_data.items():
            score = self.evaluate_crop(metrics, weights)
            results.append({
                'crop': crop_name,
                'score': score,
                'metrics': metrics
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
        
def run_sensitivity_analysis():
    print("--- Running Sensitivity Analysis on Multi-Objective Optimizer ---")
    optimizer = RiskAwareOptimizer()
    
    # Mock data representing normalized scores for 3 crops
    crops = {
        'Rice': {
            'agronomic_suitability': 0.9,
            'expected_profit': 0.7,
            'expected_demand': 0.8,
            'climate_risk': 0.6,
            'water_requirement': 0.9, # High water need
            'environmental_impact': 0.5
        },
        'Millet': {
            'agronomic_suitability': 0.8,
            'expected_profit': 0.5,
            'expected_demand': 0.4,
            'climate_risk': 0.2, # Low climate risk
            'water_requirement': 0.2, # Low water need
            'environmental_impact': 0.2
        },
        'Tomato': {
            'agronomic_suitability': 0.7,
            'expected_profit': 0.9, # High profit
            'expected_demand': 0.9,
            'climate_risk': 0.8, # High risk
            'water_requirement': 0.6,
            'environmental_impact': 0.6
        }
    }
    
    # Baseline Scenario
    baseline_ranking = optimizer.optimize(crops)
    print(f"\nBaseline Winner: {baseline_ranking[0]['crop']} (Score: {baseline_ranking[0]['score']:.3f})")
    
    # Scenario: Severe Drought (Water requirement weight heavily penalized)
    drought_weights = optimizer.default_weights.copy()
    drought_weights['water_requirement'] = -0.40
    drought_weights['agronomic_suitability'] = 0.20 # Rebalanced
    drought_ranking = optimizer.optimize(crops, weights=drought_weights)
    print(f"Drought Scenario Winner: {drought_ranking[0]['crop']} (Score: {drought_ranking[0]['score']:.3f})")
    
    # Scenario: Market Boom (Profit and demand prioritized)
    boom_weights = optimizer.default_weights.copy()
    boom_weights['expected_profit'] = 0.40
    boom_weights['expected_demand'] = 0.30
    boom_weights['agronomic_suitability'] = 0.15 # Rebalanced
    boom_ranking = optimizer.optimize(crops, weights=boom_weights)
    print(f"Market Boom Scenario Winner: {boom_ranking[0]['crop']} (Score: {boom_ranking[0]['score']:.3f})")
    
    # Save results
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'paper', 'results', 'optimizer')
    os.makedirs(output_dir, exist_ok=True)
    
    sensitivity_results = {
        'Baseline': baseline_ranking,
        'Drought': drought_ranking,
        'Market_Boom': boom_ranking
    }
    
    with open(os.path.join(output_dir, 'sensitivity_analysis.json'), 'w') as f:
        json.dump(sensitivity_results, f, indent=4)
        
    print(f"\nSensitivity analysis saved to {output_dir}/sensitivity_analysis.json")

if __name__ == '__main__':
    run_sensitivity_analysis()
