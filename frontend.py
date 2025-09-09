import streamlit as st
import requests
from PIL import Image
import io

API_URL = "https://mushroom-api-589582796964.europe-west1.run.app/predict/"

st.title("🍄 What is this Mushroom?")

tab_cam, tab_file = st.tabs(["📷 Camera", "📁 File"])

img_bytes = None
filename = None
mime = "image/jpeg"

with tab_cam:
    snap = st.camera_input("Take a picture")
    if snap is not None:
        img_bytes = snap.getvalue()
        filename = "camera.jpg"
        mime = snap.type or "image/jpeg"
        # see the picture
        st.image(Image.open(io.BytesIO(img_bytes)), caption="Your photo : ", use_container_width=True)

with tab_file:
    uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    if uploaded is not None:
        img_bytes = uploaded.getvalue()
        filename = uploaded.name
        mime = uploaded.type or "image/jpeg"
        # see the file
        st.image(Image.open(io.BytesIO(img_bytes)), caption="Your file : ", use_container_width=True)

if img_bytes and st.button("Get Specie"):
    try:
        files = {"file": (filename, img_bytes, mime)}
        res = requests.post(API_URL, files=files, timeout=60)
        if res.ok:
            data = res.json()["prediction"]
            st.success(f"✅ {data['class']} ({data['index']}) — confidence {data['confidence']}%")
        else:
            st.error(f"Erreur API: {res.status_code} — {res.text}")
    except Exception as e:
        st.error(f"Échec de la requête: {e}")
