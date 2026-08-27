"""
Sensor reading functions for the Raspberry Pi.

Sensors used (final list — camera and load cell removed):
  - pH probe        -> ADS1115 channel A0
  - EC (conductivity) probe -> ADS1115 channel A1
  - Turbidity probe  -> ADS1115 channel A2
  - DS18B20 temperature -> 1-Wire GPIO

Each function is small, single-purpose, and meant to be tested standalone
before being wired into main.py.
"""

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from w1thermsensor import W1ThermSensor

# --- one-time setup ---
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

ph_channel = AnalogIn(ads, ADS.P0)
ec_channel = AnalogIn(ads, ADS.P1)
turbidity_channel = AnalogIn(ads, ADS.P2)

temp_sensor = W1ThermSensor()


def safe_read(sensor_func, name, default=None):
    """Wrap any sensor read so one bad sensor never crashes the whole loop."""
    try:
        return sensor_func()
    except Exception as e:
        print(f"[WARN] {name} read failed: {e}")
        return default


def read_ph_raw():
    return ph_channel.voltage


def read_ec_raw():
    return ec_channel.voltage


def read_turbidity_raw():
    # Turbidity sensors are typically used directly in NTU-equivalent voltage;
    # calibrate against a known standard the same way as pH/EC if needed.
    return turbidity_channel.voltage


def read_temperature():
    return temp_sensor.get_temperature()
