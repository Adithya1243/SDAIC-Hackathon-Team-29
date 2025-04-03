import streamlit as st
import joblib
import pandas as pd

# -----------------------------------------------------
# Load Models Individually
# -----------------------------------------------------

try:
    model_AA = joblib.load("/dbfs/FileStore/saved_models/best_model_AA.joblib")
    st.write("Model AA loaded successfully!")
except Exception as e:
    model_AA = None
    st.error(f"Error loading model AA: {e}")

try:
    model_AB = joblib.load("/dbfs/FileStore/saved_models/best_model_AB.joblib")
    st.write("Model AB loaded successfully!")
except Exception as e:
    model_AB = None
    st.error(f"Error loading model AB: {e}")

try:
    model_AC = joblib.load("/dbfs/FileStore/saved_models/best_model_AC.joblib")
    st.write("Model AC loaded successfully!")
except Exception as e:
    model_AC = None
    st.error(f"Error loading model AC: {e}")

try:
    model_AD = joblib.load("/dbfs/FileStore/saved_models/best_model_AD.joblib")
    st.write("Model AD loaded successfully!")
except Exception as e:
    model_AD = None
    st.error(f"Error loading model AD: {e}")

try:
    model_AE = joblib.load("/dbfs/FileStore/saved_models/best_model_AE.joblib")
    st.write("Model AE loaded successfully!")
except Exception as e:
    model_AE = None
    st.error(f"Error loading model AE: {e}")

models = {
    "AA": model_AA,
    "AB": model_AB,
    "AC": model_AC,
    "AD": model_AD,
    "AE": model_AE,
}

# -----------------------------------------------------
# Feature Definitions
# -----------------------------------------------------

numeric_cols = [
    "income",
    "name_email_similarity",
    "prev_address_months_count",
    "current_address_months_count",
    "customer_age",
    "days_since_request",
    "intended_balcon_amount",
    "zip_count_4w",
    "velocity_6h",
    "velocity_24h",
    "velocity_4w",
    "bank_branch_count_8w",
    "date_of_birth_distinct_emails_4w",
    "credit_risk_score",
    "email_is_free",
    "phone_home_valid",
    "phone_mobile_valid",
    "bank_months_count",
    "has_other_cards",
    "proposed_credit_limit",
    "foreign_request",
    "session_length_in_minutes",
    "keep_alive_session",
    "device_distinct_emails_8w",
    "device_fraud_count",
    "month"
]

# -----------------------------------------------------
# Streamlit App Layout
# -----------------------------------------------------
st.title("Fraud Detection Prediction")

st.sidebar.header("Input Parameters")

selected_payment_type = st.sidebar.selectbox("Payment Type", list(models.keys()))

st.sidebar.subheader("Numeric Features")
input_features = {feature: st.sidebar.number_input(feature, value=0.0) for feature in numeric_cols}

# -----------------------------------------------------
# Predict Button and Output
# -----------------------------------------------------
if st.sidebar.button("Predict Fraud Probability"):
    model = models.get(selected_payment_type)
    
    if model is not None:
        input_df = pd.DataFrame([input_features], columns=numeric_cols)
        
        try:
            proba = model.predict_proba(input_df)[0, 1]
            st.write(f"### Predicted Fraud Probability: {proba:.4f}")
        except Exception as e:
            st.error(f"Prediction error: {e}")
    else:
        st.warning("Model not loaded for the selected payment type.")
