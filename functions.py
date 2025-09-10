import streamlit as st
import requests
from pathlib import Path
import pandas as pd
import pydeck as pdk

def background():
    # IMPORTANT : appelle st.set_page_config avant d'appeler background()
    st.markdown("""
    <style>
    /* ================== Fonts & palette ================== */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Inter:wght@400;600&display=swap');
    :root{
      --bg:#f3f2ec;        /* beige clair */
      --ink:#171513;       /* texte */
      --accent:#6a4c93;    /* violet */
      --accent-2:#ff7a59;  /* orange corail */
      --muted:#8b8a85;
    }

    /* ============ Débloque le fond (enlève couches blanches) ============ */
    [data-testid="stHeader"]{ background: transparent; }
    .block-container{ background: transparent; }
    .stApp { background: transparent; } /* on laisse le conteneur root transparent */

    /* ================== Fond à pois ================== */
    /* Appliqué sur la vue principale pour être visible partout */
    [data-testid="stAppViewContainer"]{
      background:
        radial-gradient(rgba(0,0,0,0.10) 1.2px, transparent 1.2px) 0 0/24px 24px,
        radial-gradient(rgba(0,0,0,0.07) 1.2px, transparent 1.2px) 12px 12px/24px 24px,
        var(--bg);
    }
    /* Sidebar en beige uni (optionnel) */
    [data-testid="stSidebar"]{ background: var(--bg); }

    /* ================== Typo & titres ================== */
    h1, h2, h3, .stMarkdown h1 {
      font-family: "Cormorant Garamond", Georgia, serif !important;
      letter-spacing:.5px; color:var(--ink);
    }
    .stMarkdown, .stTextInput, .stButton, .stSelectbox, .stRadio, .stCheckbox, .stFileUploader, .stCameraInput {
      font-family:"Inter", system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    }

    /* ================== Séparateur fin ================== */
    .hr { height:1px; background:#00000010; margin:12px 0 24px; }

    /* ================== Badge cartouche ================== */
    .badge{
      display:inline-block; padding:8px 14px; border:1px solid #00000030;
      border-radius:8px; font-size:14px; color:var(--ink); background:#ffffffa6; backdrop-filter: blur(2px);
    }

    /* ================== Cards ================== */
    .card{
      border:1px solid #00000015; border-radius:16px; padding:16px;
      background:#fff; box-shadow:0 4px 12px #0000000d;
    }

    /* ================== Boutons ================== */
    .stButton>button{
      border-radius:12px; padding:10px 16px; font-weight:600;
      border:1px solid #00000020;
    }
    .stButton>button[kind="primary"]{ background:var(--accent); color:white; }
    .stButton>button:hover{ transform:translateY(-1px); }

    /* ================== Pills ================== */
    .pill{ padding:6px 10px; border-radius:999px; font-weight:600; font-size:13px; }
    .pill.ok  { background:#e8fff1; color:#207a43; border:1px solid #b8e7c7; }
    .pill.no  { background:#fff0f0; color:#b00020; border:1px solid #f3c1c1; }
    .pill.mid { background:#fff9e8; color:#8a5a00; border:1px solid #f3ddae; }
    </style>
    """, unsafe_allow_html=True)
    return 1


def title():
    st.markdown("""
    <h1 style="text-align:center; font-size:58px; margin-bottom:4px;">
      🍄 What is this Mushroom?
    </h1>
    <p style="text-align:center; margin-top:-6px;">
      <span class="badge">Mushroom Species Predictor</span>
    </p>
    """, unsafe_allow_html=True)
    return 1


def url_exists(url: str, timeout: float = 4.0) -> bool:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Streamlit/1.0)"}
    try:
        # HEAD d'abord (léger)
        r = requests.head(url, allow_redirects=True, timeout=timeout, headers=headers)
        if r.status_code < 400:
            return True
        # certains sites bloquent HEAD -> on tente un petit GET
        if r.status_code in (400, 401, 403, 405):
            r = requests.get(url, stream=True, allow_redirects=True, timeout=timeout, headers=headers)
            return r.status_code < 400
        return False
    except requests.RequestException:
        return False


def anses_safety_tips():
    st.markdown("### Field and safety tips (ANSES)")
    with st.expander("While foraging"):
        st.write("- Harvest **only** mushrooms you can identify with certainty.")
        st.write("- At the **slightest doubt**, **do not eat** your harvest before having it checked by a **pharmacist** or a **mycology association**.")
        st.write("- Be cautious with **ID smartphone apps**: the **error risk is high**.")

    with st.expander("Before eating"):
        st.write("- **Take a photo** of your harvest **before cooking**; it helps in case of poisoning assessment.")
        st.write("- **Never eat wild mushrooms raw.**")
        st.write("- **Cook thoroughly:** **20–30 min in a pan** or **15 min in boiling water**.")

    with st.expander("If you feel unwell"):
        st.write("- For **life-threatening** symptoms, call **15 or 112** (France) immediately (use your local emergency number elsewhere).")
        st.write("- For any other symptoms, contact a **Poison Control Center** right away.")

    with st.expander("Young children"):
        st.write("**Never** give wild mushrooms to **young children**.")

    st.link_button("Source: ANSES — “Cueillette des champignons”, 2021 infographic.","https://share.google/9LLk6vtnHd5Sk6237")

    return 1


################## Functions for the map #######################


def norm_species(s: str) -> str:
    return str(s).strip().lower().replace(" ", "_")

@st.cache_data
def load_points(source: str) -> pd.DataFrame:
    #turns csv into pd dataframe
    p = Path(source)
    if not p.exists():
        return
    df = pd.read_csv(p)
    df = df.dropna(subset=["lat","lon"]).copy()
    df["species"] = df["species"].astype(str).str.strip().str.lower().str.replace(" ", "_")

    return df[["species","lat","lon"]]

def build_heatmap_deck(points_df: pd.DataFrame, species_key: str) -> pdk.Deck:
    """Construit une carte pydeck avec uniquement la HeatmapLayer."""
    sdf = points_df[points_df["species"] == species_key]
    if sdf.empty:
        # centre par défaut (France approx)
        center_lat, center_lon = 46.5, 2.0
    else:
        center_lat = float(sdf["lat"].mean())
        center_lon = float(sdf["lon"].mean())

    heat = pdk.Layer(
        "HeatmapLayer",
        data=sdf,
        get_position='[lon, lat]',
        aggregation="MEAN",
        radiusPixels=40,    # taille des "taches"
        intensity=2.5       # intensité de la heatmap
    )

    view = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=1, bearing=0, pitch=0)
    return pdk.Deck(
        map_provider="carto",     # pas de token Mapbox nécessaire
        map_style="light",
        initial_view_state=view,
        layers=[heat],
        tooltip={"text": species_key.replace("_", " ")}
    )

def render_species_heatmap(species_name: str,
                           csv_source: str = "species_points.csv"):
    """
    Affiche la heatmap pour `species_name` à partir du CSV (local ou URL).
    Utilisation : render_species_heatmap(specie)  # ou top_species
    """
    pts_df = load_points(csv_source)
    if pts_df.empty :
        return

    species_key = norm_species(species_name)
    sdf = pts_df[pts_df["species"] == species_key]

    if sdf.empty:
        return

    deck = build_heatmap_deck(pts_df, species_key)
    st.pydeck_chart(deck, use_container_width=True)
    st.caption("Illustrative distribution. Do not forage based solely on this app.")

@st.cache_data
def name_and_month(specie) :
    df=pd.read_csv('species_profile_seed.csv')
    specie=norm_species(specie)
    df=df[df['scientific_name']==specie].head(1)
    if df.empty :
        return None
    common_name=df['common_name'].iloc[0]
    if pd.isna(common_name): common_name = None
    return common_name
