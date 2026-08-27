# Paneer Quality & Adulteration Detection — Team Innov8 (SIH26_85)

Rapid screening tool: 4 sensors (pH, EC, turbidity, temperature) feed a Random
Forest classifier that flags a sample as **PURE** or **SUSPICIOUS**, for lab
confirmation. Camera/image features and the load-cell weight sensor have been
removed from the original design to keep the hardware and pipeline simple.

## What changed from the original guides

- **Removed**: camera, OpenCV image feature extraction, load cell + HX711
  weight sensing, and every feature/wiring/code reference to them.
- **Kept**: pH probe, EC probe, turbidity probe (all via ADS1115), DS18B20
  temperature sensor, Random Forest model, Supabase storage, Streamlit
  dashboard.
- Feature vector is now `[pH, ec, turbidity, temperature]` everywhere —
  Pi code, training script, and dashboard all use this exact order.

## Project structure

```
paneer-adulteration-ml/
├── app.py                     # The website (Streamlit dashboard)
├── requirements.txt           # For Streamlit Cloud deployment
├── requirements-pi.txt        # For the Raspberry Pi (hardware libs)
├── calibration.json           # pH/EC calibration constants
├── ml/
│   ├── generate_synthetic_dataset.py
│   ├── train_model.py
│   └── paneer_rf_v1.pkl       # trained model (committed so the dashboard works standalone)
└── pi/
    ├── sensors.py              # raw sensor reads
    ├── data_builder.py         # calibration + JSON + feature vector
    ├── main.py                 # main loop: read -> predict -> OLED -> upload
    └── supabase_client.py
```

## Step 1 — Local setup

```bash
git clone <your-repo-url>
cd paneer-adulteration-ml
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 2 — Build the dataset and train the model

Until you've collected real samples, use the synthetic dataset:

```bash
cd ml
python generate_synthetic_dataset.py   # writes combined_dataset.csv
python train_model.py                  # writes paneer_rf_v1.pkl
cd ..
```

Once you've collected 15–20 real samples (see the "reference samples" step
in your hardware roadmap), append them to `combined_dataset.csv` with the
same four columns (`pH, ec, turbidity, temperature, label`) and retrain.

## Step 3 — Run the dashboard locally

```bash
streamlit run app.py
```

The **Simulate** tab works immediately with no hardware or Supabase needed —
good for testing the model and as a demo-day fallback. The **Live** tab needs
Supabase configured (Step 5).

## Step 4 — Set up the Raspberry Pi (hardware side)

On the Pi, install the hardware-specific dependencies instead:

```bash
pip install -r requirements-pi.txt
```

Wire only: pH probe → ADS1115 A0, EC probe → ADS1115 A1, turbidity probe →
ADS1115 A2, DS18B20 → GPIO4 (1-Wire), OLED → I2C, START button → GPIO17.
No camera, no load cell/HX711.

Fill in your Supabase URL/key in `pi/supabase_client.py`, copy
`paneer_rf_v1.pkl` to `/home/pi/models/`, then run `pi/main.py` (set it up as
a systemd service so it auto-starts — see your original Software Development
Guide Step 11 for the exact service file, it's unchanged).

## Step 5 — Supabase table

Create a `paneer_tests` table with columns:
`id, timestamp, pH, ec, turbidity, temperature, predicted_label, confidence, verified_label, label_verified`

(No `weight` or `image_*` columns needed anymore.)

## Step 6 — Deploy the dashboard to Streamlit Community Cloud

```bash
git init
git add .
git commit -m "Initial commit: simplified 4-sensor paneer screening app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/paneer-adulteration-ml.git
git push -u origin main
```

Then on [share.streamlit.io](https://share.streamlit.io):
1. Sign in with GitHub
2. "Create app" → "I already have an app"
3. Repository: `YOUR_USERNAME/paneer-adulteration-ml`, Branch: `main`, Main file: `app.py`
4. In app **Settings → Secrets**, add:
   ```
   SUPABASE_URL = "https://xxxx.supabase.co"
   SUPABASE_KEY = "your-anon-key"
   ```
5. Deploy

## Honest note for judges

The model is trained on a synthetic dataset (ranges informed by typical
dairy/paneer characteristics), not yet on real lab-confirmed samples. Present
it as a screening tool that improves as verified samples are added — not a
finished adulteration detector.
