# train_model.py
# Run this file once to train the model and save it
# After this you don't need to run it again unless you change the data
#
# How to run:
#   python train_model.py

import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from config import (
    DATA_PATH, MODEL_PATH, FEATURE_COLUMNS,
    TARGET_COLUMN, RESULT_MAPPING, VENUE_MAPPING
)

print("Loading dataset...")
df = pd.read_csv(DATA_PATH)
print(f"Dataset loaded — {len(df)} rows, {len(df.columns)} columns")

# -------------------------------------------------------
# Step 1: Drop columns we don't need
# -------------------------------------------------------
cols_to_drop = [
    "Unnamed: 0", "time", "comp", "round", "day",
    "attendance", "captain", "formation", "opp formation",
    "referee", "match report", "notes", "dist",
    "pk", "pkatt", "gf", "ga"
]
df = df.drop(columns=cols_to_drop)
print("Unnecessary columns removed")

# -------------------------------------------------------
# Step 2: Handle missing values
# -------------------------------------------------------
# Only 'dist' had nulls but we dropped it above
# Fill any remaining nulls with median just in case
for col in ["poss", "sh", "sot", "xg", "xga", "fk"]:
    if df[col].isnull().sum() > 0:
        df[col] = df[col].fillna(df[col].median())

print("Missing values handled")

# -------------------------------------------------------
# Step 3: Encode categorical columns
# -------------------------------------------------------
# Convert Home/Away to 1/0
df["venue_encoded"] = df["venue"].map(VENUE_MAPPING)

# Convert W/D/L to 2/1/0
df["result_encoded"] = df["result"].map(RESULT_MAPPING)

print("Categorical columns encoded")

# -------------------------------------------------------
# Step 4: Split features and target
# -------------------------------------------------------
X = df[FEATURE_COLUMNS]
y = df[TARGET_COLUMN]

print(f"\nFeatures used for training: {FEATURE_COLUMNS}")
print(f"Target distribution:\n{df['result'].value_counts()}")

# -------------------------------------------------------
# Step 5: Train/test split (80% train, 20% test)
# -------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\nTraining samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")

# -------------------------------------------------------
# Step 6: Train the RandomForest model
# -------------------------------------------------------
print("\nTraining RandomForest model...")

model = RandomForestClassifier(
    n_estimators=100,     # 100 decision trees
    max_depth=10,         # limit tree depth to avoid overfitting
    random_state=42,      # for reproducibility
    class_weight="balanced"  # handles any imbalance between W/D/L
)

model.fit(X_train, y_train)
print("Model training complete")

# -------------------------------------------------------
# Step 7: Evaluate the model
# -------------------------------------------------------
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\nModel Accuracy: {round(accuracy * 100, 2)}%")
print("\nDetailed Report:")
print(classification_report(y_test, y_pred, target_names=["Loss", "Draw", "Win"]))

# Feature importance — useful to mention in viva
feature_importance = pd.Series(
    model.feature_importances_,
    index=FEATURE_COLUMNS
).sort_values(ascending=False)

print("Feature Importance (most influential first):")
print(feature_importance)

# -------------------------------------------------------
# Step 8: Save the model
# -------------------------------------------------------
with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)

print(f"\nModel saved to {MODEL_PATH}")
print("You can now run the app with: streamlit run app.py")
