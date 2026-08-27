"""
Trains the Random Forest classifier on combined_dataset.csv.
Run this on your laptop, not the Raspberry Pi — training doesn't need to
happen on the Pi, only prediction does.

Run:
    python train_model.py
Produces:
    paneer_rf_v1.pkl
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

FEATURE_COLUMNS = ["pH", "ec", "turbidity", "temperature"]  # must match json_to_features order

df = pd.read_csv("combined_dataset.csv")
X = df[FEATURE_COLUMNS]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))

joblib.dump(model, "paneer_rf_v1.pkl")
print("Saved paneer_rf_v1.pkl")
