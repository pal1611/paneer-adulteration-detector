"""
Generates a synthetic training dataset until real samples are collected.
Ranges are rough placeholders based on typical paneer/dairy characteristics —
replace with your own reference-sample measurements as soon as you have them
(see Step 2 in the hardware guide: "reference samples").

Run:
    python generate_synthetic_dataset.py
Produces:
    combined_dataset.csv
"""

import numpy as np
import pandas as pd

np.random.seed(42)
N_PER_CLASS = 250

# --- Pure paneer ---
pure = pd.DataFrame({
    "pH": np.random.normal(5.6, 0.2, N_PER_CLASS),
    "ec": np.random.normal(1.1, 0.2, N_PER_CLASS),
    "turbidity": np.random.normal(18, 5, N_PER_CLASS),
    "temperature": np.random.normal(24, 1.5, N_PER_CLASS),
    "label": "PURE",
})

# --- Suspicious / adulterated (starch-added or water-diluted) ---
suspicious = pd.DataFrame({
    "pH": np.random.normal(4.5, 0.3, N_PER_CLASS),
    "ec": np.random.normal(3.4, 0.5, N_PER_CLASS),
    "turbidity": np.random.normal(70, 15, N_PER_CLASS),
    "temperature": np.random.normal(24, 1.5, N_PER_CLASS),
    "label": "SUSPICIOUS",
})

df = pd.concat([pure, suspicious], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle
df.to_csv("combined_dataset.csv", index=False)

print(f"Wrote combined_dataset.csv with {len(df)} rows")
print(df["label"].value_counts())
