# Databricks notebook source
# =======================================
# A) TRAINING & SAVING MODELS (Databricks)
# =======================================

# 1) Read your data (example: from an existing table)
df_spark = spark.read.table("workspace.default.financial_data_v2")
df_spark.printSchema()

import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import joblib
import os

# ------------------------------------------
# 2) Convert to Pandas, basic data cleaning
# ------------------------------------------
df = df_spark.toPandas()

crucial_cols = ["payment_type", "fraud_bool"]
df = df.dropna(subset=crucial_cols)
df["fraud_bool"] = df["fraud_bool"].astype(int)

# ------------------------------------------
# 3) Train/Test Split
# ------------------------------------------
train_df, test_df = train_test_split(
    df,
    test_size=0.2,
    random_state=42,
    stratify=df["fraud_bool"]
)

# ------------------------------------------
# 4) Numeric Feature List
# ------------------------------------------
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

# ------------------------------------------
# 5) Train a LogisticRegression per p_type
# ------------------------------------------
best_models = {}

all_payment_types = train_df["payment_type"].unique()
for p_type in all_payment_types:
    subset = train_df[train_df["payment_type"] == p_type]
    if len(subset) < 10:
        print(f"Skipping '{p_type}' due to insufficient data.")
        continue
    
    X_train = subset[numeric_cols].dropna()
    y_train = subset.loc[X_train.index, "fraud_bool"]
    
    model = LogisticRegression(solver="liblinear", random_state=42)
    model.fit(X_train, y_train)
    
    auc = roc_auc_score(y_train, model.predict_proba(X_train)[:,1])
    print(f"Trained model for payment_type='{p_type}' AUC={auc:.4f}")
    
    best_models[p_type] = model

# ------------------------------------------
# 6) Evaluate on test set (just for a check)
# ------------------------------------------
test_df["fraud_prob"] = np.nan

for p_type, model in best_models.items():
    subset_idx = test_df[test_df["payment_type"] == p_type].index
    if len(subset_idx) > 0:
        X_test_sub = test_df.loc[subset_idx, numeric_cols].fillna(0)
        probs = model.predict_proba(X_test_sub)[:, 1]
        test_df.loc[subset_idx, "fraud_prob"] = probs

overall_auc = roc_auc_score(
    test_df["fraud_bool"].values,
    test_df["fraud_prob"].fillna(0).values
)
print(f"\nOVERALL TEST AUC: {overall_auc:.4f}")

# ----------------------------------------------------
# 7) Save the Models + Feature Lists to DBFS "FileStore"
# ----------------------------------------------------
dbfs_dir = "dbfs:/FileStore/saved_models"    # DBFS path
local_dir = "/dbfs/FileStore/saved_models"   # equivalent local driver path

# Create folder in DBFS
dbutils.fs.mkdirs(dbfs_dir)
os.makedirs(local_dir, exist_ok=True)

# Save each trained model
for p_type, model in best_models.items():
    model_path = os.path.join(local_dir, f"best_model_{p_type}.joblib")
    joblib.dump(model, model_path)
    print(f"Saved model '{p_type}' to {model_path}")

# Save numeric_cols for reference in Streamlit
feature_set_path = os.path.join(local_dir, "feature_sets.joblib")
joblib.dump(numeric_cols, feature_set_path)
print(f"Saved feature sets to {feature_set_path}")

# Also save the list of payment types that we actually trained
trained_payment_types_path = os.path.join(local_dir, "trained_payment_types.joblib")
joblib.dump(list(best_models.keys()), trained_payment_types_path)
print(f"Saved trained payment types to {trained_payment_types_path}")

print("\n=== DONE: Models saved in DBFS ===")


# COMMAND ----------

display(dbutils.fs.ls("dbfs:/FileStore/saved_models"))
