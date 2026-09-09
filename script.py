import os

audit_dir = r'c:\Users\ajayb\UzhavarHub\research_audit'
os.makedirs(audit_dir, exist_ok=True)

files = {
    '01_project_architecture.md': '''# Project Architecture Audit
- **Current State**: Django monolith with embedded ML models via scikit-learn.
- **Issues**: Tightly coupled, synthetic data generation inside training scripts.
- **Action**: Needs proper ML pipeline separation and risk-aware optimizer integration.
''',
    '02_data_inventory.md': '''# Data Inventory Audit
- **Crop Recommendation**: data/processed/crop_recommendation.csv (Simulated noise added during training).
- **Demand Forecasting**: data/processed/demand_forecasting.csv
- **Dynamic Pricing**: Synthetically generated target features with injected correlation.
- **Yield Prediction**: 100% synthetic generated using random normal distributions.
- **Sentiment Analysis**: Synthetic/hand-crafted text corpus.
- **Action**: Identify and ingest real datasets, or explicitly declare models as simulations.
''',
    '03_model_inventory.md': '''# Model Inventory Audit
1. **Crop Recommendation**: RandomForestClassifier (Scikit-learn).
2. **Demand Forecasting**: RandomForestRegressor (Scikit-learn).
3. **Dynamic Pricing**: RandomForestRegressor (Scikit-learn) - Highly flawed due to data leakage.
4. **Weather Forecasting**: RandomForestRegressor (Scikit-learn).
5. **Yield Prediction**: RandomForestRegressor (Scikit-learn) - Trained on synthetic data.
6. **Sentiment Analysis**: TF-IDF + MultinomialNB.
''',
    '04_experiment_inventory.md': '''# Experiment Inventory Audit
- un_all_experiments.py runs all scripts sequentially.
- **Leakage**: KFold(shuffle=True) used for time-series demand forecasting and dynamic pricing, leading to severe future data leakage.
- **Generalization**: No geographic or temporal holdout validation.
- **Action**: Implement TimeSeriesSplit and proper cross-validation.
''',
    '05_reproducibility_audit.md': '''# Reproducibility Audit
- **Current State**: 	rain_ai_models.py produces the models and metrics reproducibly because seeds are fixed.
- **Issue**: Reproducing synthetic data doesn't equate to scientific reproducibility.
''',
    '06_methodology_audit.md': '''# Methodology Audit
- **Current State**: Purely point predictions (e.g., predicted demand). No uncertainty estimation. No multi-objective optimization.
- **Action**: Must implement prediction intervals and a risk-aware decision framework incorporating agronomic, economic, and climatic factors.
''',
    '07_q1_reviewer_audit.md': '''# Q1 Reviewer Audit
- **AI/ML Reviewer Score**: 2/10 (Severe data leakage, synthetic targets, weak validation).
- **Sustainability Reviewer Score**: 1/10 (No measurable sustainability metrics).
- **Methodology Reviewer Score**: 3/10 (Lack of rigorous experimental design and hypotheses).
''',
    '08_claim_evidence_matrix.csv': '''Claim,Source,Dataset,Model,Experiment,Metric,Actual Result,Real/Synthetic,Reproducible,Statistically Supported,Q1 Risk Level
Crop Rec 97.86%,Manuscript,processed/crop,RF,5-fold CV,Accuracy,98.04%,Synthetic Noise,Yes,Yes,High (Simulated)
Demand R2 0.088,Manuscript,processed/demand,RF,KFold,R2,0.088,Real,Yes,Yes,Critical (Temporal Leakage)
Pricing Ablation,Manuscript,ecommerce,RF,KFold,R2,-0.25,Synthetic Target,Yes,Yes,Critical (Fabricated)
Yield Prediction,Manuscript,synthetic,RF,KFold,RMSE,6.04,Synthetic,Yes,Yes,Critical (Fabricated)
''',
    '09_problem_priority_matrix.csv': '''Problem,Category,Priority,Description,Action
Temporal Leakage,Methodology,P0,Demand and Pricing use shuffled KFold,Replace with TimeSeriesSplit
Synthetic Pricing,Data,P0,Dynamic pricing target is mathematically generated,Use real historical prices or declare simulation
Synthetic Yield,Data,P0,Yield data is np.random generated,Use FAO/real data or remove claim
No Uncertainty,Methodology,P1,Models give point predictions without risk,Add prediction intervals
No Multi-Objective,Architecture,P0,System lacks risk-aware optimization,Implement multi-objective optimizer
''',
    '10_current_q1_readiness.md': '''# Current Q1 Readiness
- **Scientific validity**: 20%
- **Data quality**: 10%
- **Experimental validation**: 15%
- **Methodology/statistics**: 20%
- **Overall Q1 Readiness**: ~15%
- **Blockers**: Severe temporal leakage in demand/pricing, synthetic data presented as real, lack of uncertainty quantification.
'''
}

for filename, content in files.items():
    with open(os.path.join(audit_dir, filename), 'w', encoding='utf-8') as f:
        f.write(content)

print('Audit files generated successfully.')
