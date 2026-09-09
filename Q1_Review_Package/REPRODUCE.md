# Reproduction Guide for UzhavarHub Results

This document provides exact, step-by-step instructions to recreate every machine learning evaluation metric reported in the manuscript from scratch.

### Prerequisites
- Python 3.9+
- A working Django environment
- Packages listed in `requirements.txt` (specifically `scikit-learn`, `pandas`, `numpy`, `scipy`)

### Execution Time
- **Expected Time:** ~1-2 minutes on a standard laptop CPU.
- No GPU is required.

### Step-by-Step Instructions

1. **Activate your virtual environment** (if applicable):
   ```bash
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Run the master experiment script:**
   From the root directory of the project, execute:
   ```bash
   python run_all_experiments.py
   ```

3. **Verify the Output:**
   The script performs 5-fold cross-validation on all models using a fixed random seed (`np.random.seed(42)`). 
   
   Upon completion, it will overwrite the models in `ai_services/models/` and generate two new files:
   - `paper/results/final_results.json`: Contains the canonical R², RMSE, Accuracy, and F1 scores.
   - `paper/results/final_statistical_tests.json`: Contains the p-values and Cohen's d effect sizes.

### Note on Dynamic Pricing Results (R² < 0)
You may notice that the `Dynamic_Pricing` R² is negative (approx `-0.25`). This is mathematically correct and not a bug. Predicting highly volatile agricultural spot-market prices solely using lagging demand, inventory, and weather metrics is known to be exceptionally difficult without macroeconomic and market-sentiment features. The negative R² indicates that the naive baseline (predicting the historical mean price) outperforms the Random Forest model on unseen data. This limitation is discussed transparently in the manuscript.
