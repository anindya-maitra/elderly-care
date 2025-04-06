import pandas as pd
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# Create output folder
os.makedirs("models", exist_ok=True)

# --- Load Datasets ---
health_df = pd.read_csv("data/health_monitoring.csv")
safety_df = pd.read_csv("data/safety_monitoring.csv")

# --- Label Encoder Setup ---
le = LabelEncoder()

# --- Health Alert Model Training ---
def train_health_model(df):
    label_cols = [
        "Heart Rate Below/Above Threshold (Yes/No)",
        "Blood Pressure Below/Above Threshold (Yes/No)",
        "Glucose Levels Below/Above Threshold (Yes/No)",
        "SpO₂ Below Threshold (Yes/No)",
        "Alert Triggered (Yes/No)"
    ]
    for col in label_cols:
        df[col] = le.fit_transform(df[col])

    X = df[["Heart Rate", "Glucose Levels", "Oxygen Saturation (SpO₂%)"]]
    y = df["Alert Triggered (Yes/No)"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    joblib.dump(model, "models/health_alert_model.pkl")
    print("✅ Health model saved.")

# --- Safety Alert Model Training ---
def train_safety_model(df):
    df["Alert Triggered (Yes/No)"] = le.fit_transform(df["Alert Triggered (Yes/No)"])
    df["Fall Detected (Yes/No)"] = le.fit_transform(df["Fall Detected (Yes/No)"])
    df["Movement Activity"] = le.fit_transform(df["Movement Activity"].astype(str))
    df["Location"] = le.fit_transform(df["Location"].astype(str))

    X = df[[
        "Movement Activity",
        "Fall Detected (Yes/No)",
        "Post-Fall Inactivity Duration (Seconds)",
        "Location"
    ]]
    y = df["Alert Triggered (Yes/No)"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    joblib.dump(model, "models/safety_alert_model.pkl")
    print("✅ Safety model saved.")

# --- Run Training ---
if __name__ == "__main__":
    train_health_model(health_df)
    train_safety_model(safety_df)
