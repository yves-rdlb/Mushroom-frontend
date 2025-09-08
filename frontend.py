url="https://mushroom-api-589582796964.europe-west1.run.app/predict/"

import streamlit as st
import requests

#################### Design Part ###################################
# ---------- PATHS ----------
# Resolve project root as the repo root (one level up from UI/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "model"
LOOKUPS_DIR = PROJECT_ROOT / "lookups"
DISTRIBUTIONS_DIR = PROJECT_ROOT / "distributions"
POINTS_CSV = DISTRIBUTIONS_DIR / "species_points.csv"
ICON_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/icon/marker.png"
DEFAULT_INPUT_SIZE = (224, 224)

# ---------- PAGE ----------
st.set_page_config(page_title="What Is This Mushroom?", page_icon="🍄", layout="wide")

# --- Light design polish (CSS) ---
st.markdown(
    """
    <style>
      /* overall look */
      .main {
        background: radial-gradient(1000px 500px at 20% 0%, #f6fff7 0%, #ffffff 40%) no-repeat;
      }
      h1, h2, h3 { letter-spacing: 0.2px; }
      /* cards */
      .card {
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 16px;
        padding: 18px 18px 14px 18px;
        background: #fff;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
      }
      /* pill labels */
      .pill {
        display:inline-block; padding:5px 10px; border-radius:999px;
        font-size:12px; font-weight:600; letter-spacing:.2px;
        background:#eef6ff; color:#1250aa; border:1px solid #d9eaff;
      }
      .pill.ok { background:#edfbf0; color:#126b36; border-color:#c9f1d6; }
      .pill.warn { background:#fff4ed; color:#9a3e00; border-color:#ffe1cc; }
      .pill.unknown { background:#f3f4f6; color:#374151; border-color:#e5e7eb; }
      /* CTA button */
      div.stButton > button {
        border-radius: 12px;
        font-weight: 700;
        padding: 10px 16px;
      }
      /* footer */
      .footer {
        color:#6b7280; font-size:12px; margin-top:8px;
      }
      /* nicer tabs spacing */
      .stTabs [data-baseweb="tab-list"] { gap: 4px; }
      .stTabs [data-baseweb="tab"] {
        padding-top: 8px; padding-bottom: 8px;
      }
      /* dataframes tighter */
      .stDataFrame { border-radius: 12px; overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown("### 🍄 What Is This Mushroom?")

################### Coding part using the docker image ###################################
uploaded_file = st.file_uploader("Upload a mushroom image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # envoie au backend FastAPI
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "image/jpeg")}
    res = requests.post(url, files=files)

    if res.status_code == 200:
        data = res.json()["prediction"]
        st.success(f"✅ Prediction: {data['class']} ({data['index']})")
        st.write(f"Confidence: {data['confidence']}")
    else:
        st.error(f"Error: {res.text}")
