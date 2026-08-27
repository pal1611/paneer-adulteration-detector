import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Paneer Quality & Adulteration Detector", layout="wide")
st.title("🧀 Paneer Quality & Adulteration Detection")
st.caption("Team Innov8 — SIH26_85 — Multimodal edge sensing + Random Forest screening")

# Supabase connection is optional: the dashboard should still work (in Simulate
# mode) even if no credentials are set, e.g. while testing locally.
try:
    from supabase import create_client
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    SUPABASE_AVAILABLE = True
except Exception:
    SUPABASE_AVAILABLE = False

FEATURE_LABELS = {
    "pH": "pH",
    "ec": "Electrical Conductivity (mS/cm)",
    "turbidity": "Turbidity (NTU)",
    "temperature": "Temperature (°C)",
}

tab_live, tab_simulate = st.tabs(["📡 Live Results", "🧪 Simulate"])

# ---------------------------------------------------------------------------
# LIVE TAB — pulls real readings from Supabase
# ---------------------------------------------------------------------------
with tab_live:
    if not SUPABASE_AVAILABLE:
        st.warning(
            "Supabase isn't configured yet. Add SUPABASE_URL and SUPABASE_KEY "
            "to Streamlit secrets to enable live results. Use the Simulate tab "
            "in the meantime."
        )
    else:
        if st.button("🔄 Refresh"):
            st.rerun()

        result = (
            supabase.table("paneer_tests")
            .select("*")
            .order("timestamp", desc=True)
            .limit(1)
            .execute()
        )

        if not result.data:
            st.info("No readings yet. Run a test on the hardware to see results here.")
        else:
            row = result.data[0]
            label = row.get("predicted_label", "UNKNOWN")
            confidence = row.get("confidence", 0)

            col1, col2 = st.columns([1, 2])
            with col1:
                if label == "PURE":
                    st.success(f"### ✅ {label}")
                else:
                    st.error(f"### ⚠️ {label}")
                st.metric("Confidence", f"{confidence:.0f}%")
                st.caption(f"Recorded: {row.get('timestamp', '—')}")

            with col2:
                readings = {FEATURE_LABELS[k]: row[k] for k in FEATURE_LABELS if k in row}
                st.table(pd.DataFrame([readings]))

        # Recent trend chart
        history = (
            supabase.table("paneer_tests")
            .select("*")
            .order("timestamp", desc=True)
            .limit(20)
            .execute()
        )
        if history.data:
            hist_df = pd.DataFrame(history.data).sort_values("timestamp")
            st.subheader("Recent readings")
            fig = px.line(
                hist_df, x="timestamp", y=["pH", "ec", "turbidity"],
                labels={"value": "Reading", "timestamp": "Time", "variable": "Sensor"},
            )
            st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# SIMULATE TAB — manual demo / fallback mode, no hardware or Supabase needed
# ---------------------------------------------------------------------------
with tab_simulate:
    st.write("Manually enter or simulate a reading to see how the model classifies it.")

    sample_type = st.selectbox("Quick-fill", ["Custom", "Typical Pure Paneer", "Typical Adulterated"])

    defaults = {
        "Typical Pure Paneer": {"pH": 5.6, "ec": 1.1, "turbidity": 18.0, "temperature": 24.0},
        "Typical Adulterated": {"pH": 4.4, "ec": 3.5, "turbidity": 70.0, "temperature": 24.0},
        "Custom": {"pH": 5.6, "ec": 1.1, "turbidity": 18.0, "temperature": 24.0},
    }[sample_type]

    c1, c2, c3, c4 = st.columns(4)
    ph = c1.number_input("pH", 0.0, 14.0, defaults["pH"])
    ec = c2.number_input("EC (mS/cm)", 0.0, 20.0, defaults["ec"])
    turbidity = c3.number_input("Turbidity (NTU)", 0.0, 200.0, defaults["turbidity"])
    temperature = c4.number_input("Temperature (°C)", 0.0, 50.0, defaults["temperature"])

    if st.button("Run Random Forest Inference"):
        try:
            import joblib
            model = joblib.load("ml/paneer_rf_v1.pkl")
            pred = model.predict([[ph, ec, turbidity, temperature]])[0]
            conf = model.predict_proba([[ph, ec, turbidity, temperature]]).max() * 100
            if pred == "PURE":
                st.success(f"Result: PASS — {pred} ({conf:.0f}% confidence)")
            else:
                st.error(f"Result: ALERT — {pred} ({conf:.0f}% confidence)")
        except FileNotFoundError:
            st.warning("No trained model found at ml/paneer_rf_v1.pkl — run ml/train_model.py first.")
