# Project Architecture Audit
- **Current State**: Django monolith with embedded ML models via scikit-learn.
- **Issues**: Tightly coupled, synthetic data generation inside training scripts.
- **Action**: Needs proper ML pipeline separation and risk-aware optimizer integration.
