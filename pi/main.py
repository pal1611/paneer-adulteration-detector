"""
Main control loop on the Raspberry Pi.
States: IDLE -> SAMPLE -> RESULT (MODE button no longer needed for camera/
calibration switching now that there's no image or load-cell state; keeping
just START keeps the demo simpler).

Run this via systemd (see README) so it auto-starts on boot.
"""

import time
import joblib
import RPi.GPIO as GPIO
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306

from data_builder import build_reading_json, json_to_features
from supabase_client import upload_to_supabase

START_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(START_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

serial = i2c(port=1, address=0x3C)
oled = ssd1306(serial)

model = joblib.load("/home/pi/models/paneer_rf_v1.pkl")


def show_on_oled(text):
    print(text)  # replace/extend with actual luma.oled draw calls
    # oled drawing omitted here for brevity — see luma.oled docs for text rendering


def predict(feature_vector):
    label = model.predict([feature_vector])[0]
    confidence = model.predict_proba([feature_vector]).max()
    return label, confidence


def main():
    show_on_oled("Ready - press START")
    while True:
        if GPIO.input(START_PIN) == GPIO.LOW:
            show_on_oled("Reading sensors...")
            data = build_reading_json()
            features = json_to_features(data)
            label, confidence = predict(features)
            show_on_oled(f"{label} ({confidence*100:.0f}%)")
            upload_to_supabase(data, label, confidence)
            time.sleep(3)
            show_on_oled("Ready - press START")
        time.sleep(0.1)


if __name__ == "__main__":
    main()
