import os
import json
from django.test import TestCase
from django.conf import settings
from ai_services.analyzer import load_model, recommend_crop, get_market_insights

class AIServicesTests(TestCase):
    def setUp(self):
        self.metrics_path = os.path.join(settings.BASE_DIR, 'ai_services', 'models', 'evaluation_results.json')
        self.crop_model = load_model('crop_model.pkl')
        self.demand_model = load_model('demand_model.pkl')
        
    def test_evaluation_results_exist_and_meet_baselines(self):
        self.assertTrue(os.path.exists(self.metrics_path), "evaluation_results.json does not exist")
        
        with open(self.metrics_path, 'r') as f:
            metrics = json.load(f)
            
        self.assertIn('Crop_Recommendation', metrics)
        crop_metrics = metrics['Crop_Recommendation']
        self.assertGreater(crop_metrics['RF_Accuracy'], 0.85, "Crop accuracy must be > 0.85")
        self.assertGreater(crop_metrics['RF_Accuracy'], crop_metrics['Baseline_LR_Accuracy'], "RF must beat Baseline LR")
        
        self.assertIn('Demand_Forecasting', metrics)
        demand_metrics = metrics['Demand_Forecasting']
        self.assertIn('Test_RMSE', demand_metrics)

    def test_crop_recommendation_valid_prediction(self):
        self.assertIsNotNone(self.crop_model, "crop_model.pkl not loaded")
        # N, P, K, temperature, humidity, ph, rainfall
        crop = recommend_crop(104, 18, 30, 23.6, 60.3, 6.7, 140.91)
        self.assertIsInstance(crop, str)
        self.assertNotEqual(crop, 'Unknown', "Crop recommendation failed to predict")
