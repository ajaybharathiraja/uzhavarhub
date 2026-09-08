# Reproducibility Guide

This guide provides step-by-step instructions for academic peers and reviewers to exactly replicate the ML models, statistical tests, and application server environment described in the manuscript.

## Prerequisites
- Docker and Docker Compose (Optional, but recommended for exact environment replication)
- Python 3.11+ (If running locally)
- A valid Kaggle API token (`kaggle.json`) placed in your home directory (`~/.kaggle/kaggle.json` on Linux/Mac, `C:\Users\<User>\.kaggle\kaggle.json` on Windows).

## Method 1: Using Docker (Recommended)

1. **Build the container:**
   ```bash
   docker build -t uzhavarhub:latest .
   ```
2. **Run the container interactively:**
   ```bash
   docker run -it -p 8000:8000 -v ~/.kaggle:/root/.kaggle uzhavarhub:latest /bin/bash
   ```
3. **Execute the Machine Learning Pipeline:**
   Inside the container, run:
   ```bash
   python train_ai_models.py
   ```
   This will:
   - Download the raw data via the Kaggle API.
   - Run the 5-fold cross-validation on both the RandomForest (Crop) and LinearRegression (Demand) models.
   - Run the Paired t-tests.
   - Output `evaluation_results.json` and `statistical_tests.json`.

4. **Verify the Output:**
   Compare the generated JSON metrics against the ones published in the `/paper/results/` directory of this repository. Because `random_state=42` is strictly enforced in `train_ai_models.py`, the metrics should match exactly.

## Method 2: Running Locally

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the Training Script:**
   ```bash
   python train_ai_models.py
   ```
3. **Run the Test Suite:**
   To verify that the AI integration functions within the Django framework properly:
   ```bash
   python manage.py test
   ```

## Key Random Seeds
To ensure determinism across different environments, the following seeds are pinned in `train_ai_models.py`:
- `random_state=42` for `train_test_split`, `StratifiedKFold`, and `KFold`.
- `random_state=42` for the `RandomForestClassifier` and `LogisticRegression` models.
