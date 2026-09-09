# Reproducibility Guide: UzhavarHub

This guide allows reviewers to reproduce every single metric, statistical test, and simulation result currently reported in the manuscript. The full execution requires less than 2 minutes on a standard CPU.

## Environment Setup
To ensure exact replication of the numbers in the paper, please install the pinned dependencies.

```bash
# Create a virtual environment (recommended)
python -m venv venv
# Windows: venv\Scripts\activate
# Unix/MacOS: source venv/bin/activate

# Install exact versions used during development
pip install -r requirements.txt
```

## Step 1: Core Machine Learning Metrics & Statistical Tests
This script trains all primary models (Crop Recommendation, Demand Forecasting, Dynamic Pricing, Yield, Sentiment), evaluates them using K-Fold Cross Validation with a fixed random seed (42), and performs the reported ablation study. Note that this script automatically injects the ±5% Gaussian noise for the Crop Recommendation evaluation to simulate IoT sensor variance.

```bash
python run_all_experiments.py
```
**Output:** This will generate `paper/results/final_results.json` and `paper/results/final_statistical_tests.json`. You can cross-reference the exact accuracy (98.05%), R² values (-0.25), and Cohen's *d* sizes from these JSON files with the manuscript.

## Step 2: Economic Simulation
To reproduce the Monte Carlo simulation projecting an 82.02% profit increase and the ±50% sensitivity analysis metrics reported in Section 4.4:

```bash
python experiments/simulate_economic_impact.py
```
**Output:** This will print the projected baseline increases, the pessimistic/optimistic sensitivity bounds, and the sustainability KPIs directly to the terminal.

## Step 3: SUS / TAM Usability Study Data
To reproduce the N=34 synthetic user study results, including the Mean SUS Score (74.41) and the TAM correlation ($r=0.48$):

```bash
python experiments/generate_sus_tam_data.py
```
**Output:** Generates `paper/results/sus_results.txt` and `paper/results/tam_analysis.csv` and prints the exact reported metrics.

## Step 4: IoT Telemetry Simulation
To run the extended IoT telemetry simulation script (generates time-series noise patterns referenced in future work limitations):

```bash
python experiments/simulate_iot_telemetry.py
```
