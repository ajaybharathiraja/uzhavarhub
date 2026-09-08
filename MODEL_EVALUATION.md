# Model Evaluation Results

This document summarizes the final metrics obtained by training the machine learning models on real-world datasets for UzhavarHub. All numbers perfectly align with the computed results found in `ai_services/models/evaluation_results.json` and `paper/results/statistical_tests.json`.

## 1. Crop Recommendation Model
The Crop Recommendation module was trained using a `RandomForestClassifier` on the real 2,200 sample Kaggle dataset.

### Baseline Comparisons
To demonstrate the efficacy of our chosen model, we compared it against two baseline algorithms on a 5-fold Stratified Cross-Validation:
- **Baseline 1 (Logistic Regression):** Accuracy = 97.09%
- **Baseline 2 (K-Nearest Neighbors, k=5):** Accuracy = 98.09%

### Final Model Performance (Random Forest)
The Random Forest model significantly outperformed the baselines ($p = 0.0012, d = 3.66$ against LR), achieving near-perfect metrics across all 22 crop classes:
- **Accuracy:** 99.54%
- **Precision (Macro):** 99.57%
- **Recall (Macro):** 99.54%
- **F1 Score (Macro):** 99.54%

**Discussion:** The use of real data confirms that soil parameters (N, P, K, pH) and environmental conditions strongly predict crop suitability. The zero-reliance on synthetic data validates this approach for production use.

## 2. Demand Forecasting Model
The Demand Forecasting module was trained using a `LinearRegression` model. We merged historical demand data with e-commerce sales quantities by date and product category, extracting temporal features (day of year, month, weekend flags) and lag features.

### Final Model Performance
- **Model Type:** Linear Regression
- **Test RMSE (Root Mean Squared Error):** 44.86
- **Test MAE (Mean Absolute Error):** 35.38
- **Test R² (R-squared):** 0.087

**Discussion:** Predicting raw demand solely from calendar features on this dataset yields an R² of ~0.087. This suggests the demand is highly volatile or depends heavily on unobserved external factors. However, this is a genuine statistical projection ($p < 0.0001, d = 13.67$ against a naive mean baseline). Future iterations could explore advanced time-series models like Prophet or ARIMA to capture more complex temporal trends.

## 3. Dynamic Pricing Model
The Dynamic Pricing module was trained using a `RandomForestRegressor`.

### Final Model Performance
- **Model Type:** Random Forest Regressor
- **Test RMSE:** 192.17
- **Test R²:** -0.290

**Discussion:** The dynamic pricing model performed worse than a naive mean-prediction baseline. An ablation study demonstrated that incorporating explicit demand forecasts into pricing yields a statistically insignificant difference ($p = 0.241$), highlighting the severe challenges of predicting dynamic markets strictly from volume and date without external economic indicators.

## Integrity Checklist
- All `random.choice()` and `np.random` mock data generation logic has been strictly removed from the `ai_services` app.
- Every metric reported here corresponds to a `.pkl` model trained strictly on the `/data/processed/` datasets.
