import streamlit as st
import requests
from PIL import Image
import io
import time

API_URL= "https://vit-api-589582796964.europe-west1.run.app/predict/"

# ========= HEADER =========
st.set_page_config(page_title="What Is This Mushroom?", page_icon="🍄", layout="wide")
st.title("🍄 What Is This Mushroom?")
st.caption("Upload a picture of a Mushroom and get to know its specie")

# ========= UI LAYOUT =========
left, right = st.columns([1, 1])

# ========= Left Column =========
with left :
    st.markdown("### Upload Your Picture")
    tab_cam, tab_file = st.tabs(["📷 Camera", "📁 File"])

    img_bytes = None
    filename = None
    mime = "image/jpeg"

    with tab_cam:
        photo = st.camera_input("Take a picture")
        if photo is not None:
            img_bytes = photo.getvalue()
            filename = "camera.jpg"
            mime = photo.type or "image/jpeg"
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

# ========= Right Column =========
with right :
    st.markdown("### Get to know the specie")
    if img_bytes:
        for i in range(2) :
            st.markdown(" ")
        with st.expander("Tips for best results", expanded=True):
            st.markdown(
            "- Use **good lighting** and a **sharp** photo\n"
            "- Center the **cap & stem**; avoid occlusions\n"
            "- Prefer a **single mushroom** per photo\n"
            "- If possible, include the **gills/underside**"
            )

        go = st.button("Get Specie",use_container_width=True)
    else:
        for i in range(6) :
            st.markdown(" ")
        st.info("Upload or capture an image to enable prediction.")
        go = False
    specie=" "
    if img_bytes and go:
        try:
            files = {"file": (filename, img_bytes, mime)}
            res = requests.post(API_URL, files=files, timeout=60)
            if res.ok:
                data = res.json()["prediction"]
                specie,edibility,confidence=data['class'],data['edibility'],data['confidence']

                progress = st.progress(0, text="Preparing request…")
                for percent_complete in range(0,110,10) :
                    time.sleep(0.1)
                progress.progress(percent_complete,text="Loading finished !")
            else:
                st.error(f"API error: {res.status_code} — {res.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")
    if specie != " " :
        c1, c2, c3 = st.columns([1.2, 1, 1])
        with c1:
            st.subheader(specie)
            if edibility == "not edible":
                st.error("This Mushroom is not edible")
            elif edibility == "edible":
                st.success("✅ edible")
        with c2:
            confidence=confidence[:-1]
            confidence=float(confidence)
            st.metric("Confidence", f"{confidence}%")
            if confidence>=80 :
                st.success("High confidence")
            elif confidence < 50 :
                st.error("low confidence")
            else :
                st.warning("mid confidence")

        with c3:
            st.metric("Source", "API")

        for i in range(3) :
                st.markdown(" ")
        if edibility == "not edible":
            st.warning("⚠️ Do not consume this mushroom !")
        elif edibility == "edible":
            st.caption("⚠️ Informational only. Do not eat mushrooms based on an app prediction.")
