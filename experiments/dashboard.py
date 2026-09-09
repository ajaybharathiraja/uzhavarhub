import os
import json
import streamlit as st
import pandas as pd

st.set_page_config(page_title="UzhavarHub Q1 MLOps Dashboard", layout="wide")

st.title("UzhavarHub Q1 MLOps Dashboard")
st.markdown("### Risk-Aware Multi-Objective Optimization & Explainability")

# --- Load Explainability Data ---
base_dir = os.path.dirname(os.path.abspath(__file__))
explain_path = os.path.join(base_dir, '../paper/results/explainability/risk_explainability_report.json')

if os.path.exists(explain_path):
    with open(explain_path, 'r') as f:
        explain_data = json.load(f)
else:
    explain_data = None

# --- Load Optimizer Data ---
optimizer_path = os.path.join(base_dir, '../paper/results/optimizer/sensitivity_analysis.json')
if os.path.exists(optimizer_path):
    with open(optimizer_path, 'r') as f:
        optimizer_data = json.load(f)
else:
    optimizer_data = None

# --- Layout ---
col1, col2 = st.columns(2)

with col1:
    st.header("1. Risk-Aware Multi-Objective Optimizer")
    if optimizer_data:
        st.subheader("Sensitivity Scenarios")
        scenario = st.selectbox("Select Scenario:", list(optimizer_data.keys()))
        
        scenario_data = optimizer_data[scenario]
        df_scenario = pd.DataFrame(scenario_data)
        
        st.write(f"**Winner:** {df_scenario.iloc[0]['crop']} (Score: {df_scenario.iloc[0]['score']:.3f})")
        st.dataframe(df_scenario[['crop', 'score']].head(5))
        
        st.write("Detailed Metrics (Top Recommendation):")
        st.json(df_scenario.iloc[0]['metrics'])
    else:
        st.warning("Optimizer data not found.")

with col2:
    st.header("2. AI Explainability (SHAP & Counterfactuals)")
    if explain_data:
        st.subheader("Global Feature Importance (SHAP)")
        importances = explain_data.get("Feature_Importance", {})
        if importances:
            df_imp = pd.DataFrame(list(importances.items()), columns=["Feature", "Importance"])
            df_imp = df_imp.sort_values(by="Importance", ascending=True)
            st.bar_chart(df_imp.set_index("Feature"))
            
        st.subheader("Counterfactual Analysis")
        st.json(explain_data.get("Counterfactual", {}))
    else:
        st.warning("Explainability data not found.")

st.divider()

st.header("3. Demand Forecasting Uncertainty")
if explain_data and "Uncertainty_Estimation" in explain_data:
    demand_unc = explain_data["Uncertainty_Estimation"].get("Demand", {})
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Mean Prediction", f"{demand_unc.get('Sample_Mean_Prediction', 0):.1f}")
    col_b.metric("Lower 95% Interval", f"{demand_unc.get('Sample_Lower_95PI', 0):.1f}")
    col_c.metric("Upper 95% Interval", f"{demand_unc.get('Sample_Upper_95PI', 0):.1f}")
    
    st.info("Intervals derived via empirical variance of Random Forest estimators.")
else:
    st.warning("Uncertainty data not found.")
