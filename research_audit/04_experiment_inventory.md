# Experiment Inventory Audit
- 
un_all_experiments.py runs all scripts sequentially.
- **Leakage**: KFold(shuffle=True) used for time-series demand forecasting and dynamic pricing, leading to severe future data leakage.
- **Generalization**: No geographic or temporal holdout validation.
- **Action**: Implement TimeSeriesSplit and proper cross-validation.
