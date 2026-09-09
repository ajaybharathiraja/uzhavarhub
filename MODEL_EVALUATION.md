# Model Evaluation Results

This document summarizes the final metrics obtained by training the machine learning models on real-world datasets for UzhavarHub. All numbers perfectly align with the computed results found in `ai_services/models/evaluation_results.json`, `paper/results/demand_forecasting_v2.json`, and `paper/results/pricing_classification_v2.json`.

## 1. Crop Recommendation Model
The Crop Recommendation module was trained using a `RandomForestClassifier` on the real 2,200 sample Kaggle dataset.

### Baseline Comparisons
To demonstrate the efficacy of our chosen model, we compared it against two baseline algorithms on a 5-fold Stratified Cross-Validation:
- **Baseline 1 (Logistic Regression):** Accuracy = 95.27%
- **Baseline 2 (K-Nearest Neighbors, k=5):** Accuracy = 96.68%

### Final Model Performance (Random Forest)
The Random Forest model significantly outperformed the baselines ($p = 0.0012, d = 3.66$ against LR), achieving near-perfect metrics across all 22 crop classes:
- **Accuracy:** 98.05%
- **Precision (Macro):** 98.09%
- **Recall (Macro):** 98.05%
- **F1 Score (Macro):** 98.03%

**Discussion:** The use of real data confirms that soil parameters (N, P, K, pH) and environmental conditions strongly predict crop suitability. The zero-reliance on synthetic data validates this approach for production use.

## 2. Demand Forecasting Model
The Demand Forecasting module originally used a simple Linear Regression yielding an R² of 0.088. To improve predictive rigor (V2), we upgraded the pipeline to utilize a `GradientBoostingRegressor`, augmenting the historical sales quantities with 7-day and 14-day rolling statistical features, temporal lags (t-1, t-7), and cyclic day-of-week encoding, while preventing leakage.

### Final Model Performance V2
- **Model Type:** Gradient Boosting Regressor
- **Test RMSE:** 35.98 (V1 was 44.84)
- **Test MAE:** 27.53 (V1 was 34.92)
- **Test R²:** 0.391 (V1 was 0.088)

**Discussion:** The upgraded feature engineering allowed the Gradient Boosting Regressor to explain nearly 40% of the variance (R² = 0.391), representing a statistically significant improvement over the naive mean-prediction baseline (RMSE = 47.41, p = 0.0026). This confirms that properly extracting lagged temporal dynamics is critical for demand forecasting.

## 3. Dynamic Pricing Model
Because continuous price regression yielded negative R² values in earlier iterations (-0.290), the dynamic pricing module was reframed as a bracket classification problem (Low, Fair, Premium tiers derived strictly from training-set tertiles) in V2. We trained a `GradientBoostingClassifier` on historical demand, category average price, and forecasted weather features.

### Final Model Performance V2
- **Model Type:** Gradient Boosting Classifier
- **Accuracy:** 33.35%
- **Macro F1:** 0.332
- **Naive Majority-Class Accuracy:** 34.96%

**Discussion:** The classification model failed to significantly outperform the majority-class naive baseline (p = 0.127). We report this negative result honestly: current telemetry (weather and volume) is insufficient to reliably bucket agricultural spot-market pricing without access to broader macroeconomic or sentiment indices.

## Integrity Checklist
- All `random.choice()` and `np.random` mock data generation logic has been strictly removed from the `ai_services` app for pricing targets.
- Every metric reported here corresponds to a `.pkl` model trained strictly on the `/data/processed/` datasets.
