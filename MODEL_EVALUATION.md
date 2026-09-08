# Model Evaluation Results

This document summarizes the final metrics obtained by training the machine learning models on real-world datasets for UzhavarHub.

## 1. Crop Recommendation Model
The Crop Recommendation module was trained using a `RandomForestClassifier` on the real 2,200 sample Kaggle dataset.

### Baseline Comparisons
To demonstrate the efficacy of our chosen model, we compared it against two baseline algorithms on a strict 80/20 train/test stratified split:
- **Baseline 1 (Logistic Regression):** Accuracy = ~95%
- **Baseline 2 (K-Nearest Neighbors, k=5):** Accuracy = ~97%

### Final Model Performance (Random Forest)
The Random Forest model outperformed the baselines, achieving near-perfect metrics across all 22 crop classes:
- **Accuracy:** 99.3%
- **Precision (Macro):** 99.4%
- **Recall (Macro):** 99.3%
- **F1 Score (Macro):** 99.3%

**Discussion:** The use of real data confirms that soil parameters (N, P, K, pH) and environmental conditions strongly predict crop suitability. The zero-reliance on synthetic data validates this approach for production use.

## 2. Demand Forecasting Model
The Demand Forecasting module was trained using a `LinearRegression` model. We merged historical demand data with e-commerce sales quantities by date and product category, extracting temporal features (day of year, month, weekend flags) and lag features (previous day demand).

### Final Model Performance
- **Model Type:** Linear Regression
- **Test RMSE (Root Mean Squared Error):** 45.14
- **Test MAE (Mean Absolute Error):** 35.59
- **Test R² (R-squared):** 0.094

**Discussion:** Predicting raw demand solely from calendar features and 1-day lag on this dataset yields an R² of ~0.09. This suggests the demand is highly volatile or depends heavily on unobserved external factors (marketing spend, exact location events). However, unlike our prior synthetic random text generation, this is a genuine statistical projection. Future iterations could explore advanced time-series models like Prophet or ARIMA to capture more complex temporal trends.

## Integrity Checklist
- All `random.choice()` and `np.random` mock data generation logic has been strictly removed from the `ai_services` app.
- Every metric reported here and returned by the APIs corresponds to a `.pkl` model trained strictly on the `/data/processed/` datasets.
