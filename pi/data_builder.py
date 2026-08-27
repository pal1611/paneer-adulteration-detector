"""
Turns raw sensor readings into:
  1. A calibrated JSON reading (human-readable, goes to Supabase)
  2. A fixed-order numeric feature vector (goes to the ML model)

IMPORTANT: the order in json_to_features() must exactly match the column
order used in train_model.py. If you change one, change both.
"""

import json
from datetime import datetime

from sensors import (
    safe_read,
    read_ph_raw,
    read_ec_raw,
    read_turbidity_raw,
    read_temperature,
)

with open("calibration.json") as f:
    cal = json.load(f)


def raw_to_ph(raw_voltage):
    if raw_voltage is None:
        return None
    return cal["ph_slope"] * raw_voltage + cal["ph_offset"]


def raw_to_ec(raw_voltage):
    if raw_voltage is None:
        return None
    return cal["ec_slope"] * raw_voltage + cal["ec_offset"]


def build_reading_json():
    ph_raw = safe_read(read_ph_raw, "pH")
    ec_raw = safe_read(read_ec_raw, "EC")

    data = {
        "timestamp": datetime.now().isoformat(),
        "pH": raw_to_ph(ph_raw),
        "ec": raw_to_ec(ec_raw),
        "turbidity": safe_read(read_turbidity_raw, "Turbidity"),
        "temperature": safe_read(read_temperature, "Temp"),
    }
    return data


def json_to_features(data):
    """Fixed order: pH, ec, turbidity, temperature. Must match training data."""
    return [
        data["pH"],
        data["ec"],
        data["turbidity"],
        data["temperature"],
    ]
