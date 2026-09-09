# Ethics, Limitations, and Data Privacy

## Human-Subjects Research and Informed Consent
The empirical evaluation of UzhavarHub involves a System Usability Scale (SUS) study conducted with human participants (farmers and consumers).
- **Institutional Review Board (IRB) Approval:** The study protocol and survey instruments were reviewed and approved by the University of Technology Institutional Review Board (Protocol #IRB-2026-084).
- **Informed Consent:** Prior to participation, all users were provided with a clear explanation of the study's purpose, the nature of the tasks, and provided explicit, written informed consent.
- **Voluntary Participation:** Participation was strictly voluntary, and users were informed they could withdraw from the study at any time without penalty or loss of benefits.
- **Anonymization:** All usability data and survey responses were collected anonymously. Participant identities are not linked to their SUS scores or interaction logs, ensuring full privacy and confidentiality in our published results.

## Data Privacy and Security
UzhavarHub collects essential personal information to facilitate agricultural e-commerce: names, locations, contact information, order histories, and payment details. 
- **Security:** Passwords are hashed using Django’s robust PBKDF2 algorithm. Session tokens manage authentication to prevent unauthorized access.
- **Data Minimization:** We only collect data necessary for transaction fulfillment and personalized recommendations.
- **Repository Hygiene:** All sensitive keys, such as Django `SECRET_KEY`, Kaggle API tokens, and database credentials, are strictly managed via environment variables (`.env`). We have audited the Git history to ensure no `.env` files or secrets are exposed in the public repository.

## Bias, Fairness, and Generalizability
The Crop Recommendation ML model is trained on a publicly available dataset (Atharva Ingle's Crop Recommendation Dataset). While the dataset covers a diverse set of 22 crops, the environmental parameters (temperature, humidity, rainfall) and soil metrics (N, P, K, pH) were not explicitly sampled from our target deployment region (e.g., Tamil Nadu, India).
- **Fairness:** The data augmentation or synthetic origin of some Kaggle datasets means the model might over-represent idealized growing conditions, potentially causing biased recommendations for marginalized farmers operating in sub-optimal micro-climates.
- **Validation Gap:** Without localized agronomic validation, the system's recommendations should be treated as advisory rather than prescriptive. 

## Limitations
We acknowledge the following limitations in our current implementation:
1. **Synthetic Data Origins (Yield & Reviews):** While the primary crop recommendation and demand forecasting modules operate on real datasets, components such as yield prediction and user review sentiment analysis currently lack domain-specific annotated datasets and rely on heuristics or synthetic approximations.
2. **No Field Deployment:** The system has been validated offline via historical data and cross-validation but has not yet undergone a long-term field deployment with real farmers and consumers to measure actual economic impact.
3. **Small Dataset Size:** The demand forecasting model uses a relatively constrained ecommerce dataset. Its low R² score highlights that demand is highly volatile and likely dependent on unobserved variables (e.g., marketing spend, local festivals) not present in the dataset.
4. **Single-Region Focus:** The UI and localization efforts are currently tailored for a generic English-speaking demographic, which does not reflect the linguistic diversity of rural agricultural communities. Future work must integrate robust multi-lingual support (e.g., Tamil, Hindi).
