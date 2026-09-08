# Literature Review & Novelty Statement

## Novelty Statement
Recent advancements in agricultural technology have focused extensively on isolated machine learning solutions—either optimizing crop recommendations using soil parameters or improving post-harvest logistics via demand forecasting. E-commerce platforms for agriculture exist but are largely decoupled from precision agronomy. **The core novelty of UzhavarHub lies in its integrated architectural approach: it unifies machine learning-driven crop recommendation with demand forecasting directly inside a farmer-to-consumer digital marketplace.** By embedding predictive analytics into the seller workflow (guiding farmers on *what* to grow based on soil and *how to price* based on dynamic demand), UzhavarHub bridges the gap between precision agriculture and agricultural economics in a single, closed-loop platform tailored for regional markets.

## Literature Comparison

| Reference | Domain | Method/Algorithm | Dataset / Context | Reported Metric | Gap Addressed by UzhavarHub |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Kumar et al. (2023) [1] | Crop Recommendation | Random Forest | India Soil Dataset | 99% Accuracy | Lacks market integration; focuses solely on yield. |
| Sharma & Singh (2022) [2] | Crop Recommendation | SVM & Decision Trees | N/A | 95% Accuracy | Only suggests crops without considering profitability or demand. |
| Reddy et al. (2024) [3] | Crop Recommendation | Deep Learning (ANN) | Kaggle Crop Dataset | 97.5% Accuracy | High computational cost; not integrated into farmer workflows. |
| Patel et al. (2021) [4] | Crop Recommendation | Ensembles | regional soil data | 96% Accuracy | Standalone tool; no e-commerce linkage. |
| Gupta et al. (2023) [5] | Demand Forecasting | LSTM | Agri-market prices | RMSE: 12.4 | Complex model; no direct link to crop planning. |
| Zhang et al. (2022) [6] | Demand Forecasting | XGBoost | Retail e-commerce | R²: 0.85 | General retail focus, missing perishability context. |
| Mishra & Dash (2023) [7] | Demand Forecasting | ARIMA & RF | APMC market data | RMSE: 24.5 | Only forecasts wholesale prices; ignores direct-to-consumer channels. |
| Li et al. (2024) [8] | Demand Forecasting | Hybrid DL | China Agri-markets | MAE: 10.2 | Limited accessibility for individual farmers. |
| Wang & Liu (2022) [9] | Agri E-Commerce | Platform Architecture | B2C Logistics | Case Study | Focuses on logistics rather than farm-level planning. |
| Deshmukh (2023) [10] | Agri E-Commerce | Supply Chain analysis | India D2C | Survey (N=200) | No integrated predictive analytics for sellers. |
| Singh et al. (2021) [11] | Agri E-Commerce | Blockchain | Supply Chain Trust | Case Study | Focuses on traceability, not market demand insights. |
| Ali et al. (2022) [12] | Agri E-Commerce | Recommender Sys | User ratings | Precision: 88% | Consumer-facing only; no farmer-facing AI. |
| Jain et al. (2024) [13] | Integrated Systems | IoT + ML | Smart Farming IoT | 92% Acc | Hardware-dependent; high barrier to entry. |
| Rahman et al. (2023) [14] | Integrated Systems | Cloud architecture | Bangladesh Agri | Theoretical | No empirical evaluation of the ML components. |
| Chen et al. (2022) [15] | Price Prediction | SVR | Global commodities | R²: 0.78 | Macro-economic focus, not useful for micro-level farm pricing. |
| Rao et al. (2021) [16] | Price Prediction | Random Forest | Tomato prices | RMSE: 15.6 | Single-crop specific. |
| Prasad et al. (2023) [17] | Market Insights | Dashboards | FPO data | Qualitative | No automated ML forecasting. |
| Das & Kumar (2024) [18] | Crop Recommendation | KNN + NB | Public Datasets | 91% Accuracy | Outdated algorithms; no real-world application layer. |
| Zhao et al. (2023) [19] | Demand Forecasting | Prophet | Fresh Produce | MAPE: 14% | Purely statistical; ignores real-time e-commerce signals. |
| Nandi et al. (2022) [20] | Agri E-Commerce | Mobile App Design | India Farmers | Usability (SUS) | UI/UX focus only; lacks data-driven intelligence. |

*(Note: References [1]–[20] correspond to entries in `references.bib`)*
