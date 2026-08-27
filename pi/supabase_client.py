from supabase import create_client

# Fill these in from Project Settings > API on supabase.com
SUPABASE_URL = "https://xxxx.supabase.co"
SUPABASE_KEY = "your-anon-key"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_to_supabase(data, label, confidence):
    row = {
        **data,
        "predicted_label": label,
        "confidence": float(confidence),
        "verified_label": None,
        "label_verified": False,
    }
    try:
        supabase.table("paneer_tests").insert(row).execute()
    except Exception as e:
        print(f"[WARN] Upload failed, will retry later: {e}")
