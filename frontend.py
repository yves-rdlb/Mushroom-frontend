import streamlit as st
import requests
from PIL import Image
import io
import time
import requests
from functions import background,title,url_exists,anses_safety_tips,load_points,norm_species,build_heatmap_deck,render_species_heatmap,name_and_month
import pandas as pd
from pathlib import Path

API_URL= "https://vit-api-589582796964.europe-west1.run.app/predict/"

# ========= HEADER =========

st.set_page_config(page_title="What Is This Mushroom?", page_icon="🍄", layout="wide")

#setting the color
background()
title()
st.markdown("---")
st.markdown("Upload a picture of a Mushroom and get to know its specie + site description etc...")
# ========= UI LAYOUT =========
left, right = st.columns([1, 1])

# ========= Left Column =========
with left :
    st.markdown("### Upload Your Picture")
    tab_file, tab_cam = st.tabs(["📁 File", "📷 Camera"])

    img_bytes = None
    filename = None
    mime = "image/jpeg"

    with tab_file:
        uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
        if uploaded is not None:
            img_bytes = uploaded.getvalue()
            filename = uploaded.name
            mime = uploaded.type or "image/jpeg"
            # see the file
            st.image(Image.open(io.BytesIO(img_bytes)), caption="Your file : ", use_container_width=True)

    with tab_cam:
        photo = st.camera_input("Take a picture")
        if photo is not None:
            img_bytes = photo.getvalue()
            filename = "camera.jpg"
            mime = photo.type or "image/jpeg"
            # see the picture
            st.image(Image.open(io.BytesIO(img_bytes)), caption="Your photo : ", use_container_width=True)

# ========= Right Column =========
with right :
    st.markdown("### Discover the specie")
    if img_bytes:
        for i in range(2) :
            st.markdown(" ")
        with st.expander("Tips for best results", expanded=True):
            st.markdown(
            "- Put a picture of a Mushroom (Not a picture of yourself 😉)\n"
            "- Use **good lighting** and a **good quality** photo\n"
            "- Put the mushroom in the middle. Make sure you can see the **top** and the **stem**.\n"
            "- Prefer a **single mushroom** per photo\n"
            )

        go = st.button("Get Specie",use_container_width=True)
    else:
        for i in range(6) :
            st.markdown(" ")
        st.info("Upload or capture an image to enable prediction.")
        go = False
    specie=" "
    if img_bytes and go:
        progress = st.progress(0, text="Preparing request…")
        try:
            progress.progress(0, text="Loading…")
            time.sleep(0.1)
            with st.spinner("Loading…") :
                progress.progress(23, text="Connecting with the model…")
                time.sleep(0.5)
                progress.progress(47, text="Model is running… (it might take longer for the first picture)")
                files = {"file": (filename, img_bytes, mime)}
                res = requests.post(API_URL, files=files, timeout=60)
                progress.progress(68, text="Getting the result…")
                time.sleep(0.5)

            if res.ok:
                data = res.json()["prediction"]
                specie,edibility,confidence=data['class'],data['edibility'],data['confidence']
                progress.progress(100, text="Done!")

            else:
                st.error(f"API error: {res.status_code} — {res.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")

    if specie != " " :
        c1, c2, c3 = st.columns([1.5, 1, 1])
        with c1:
            st.markdown('Scientific Name')
            st.markdown(f"#### {specie}")
            if edibility == "not edible":
                st.error("This Mushroom is not edible")
            elif edibility == "edible":
                st.success("This Mushroom is edible")
        with c2:
            confidence=confidence[:-1]
            confidence=float(confidence)
            st.markdown("Confidence",)
            st.markdown(f"#### {confidence}%")
            if confidence>=80 :
                st.success("High confidence")
            elif confidence < 50 :
                st.error("low confidence")
            else :
                st.warning("medium confidence")
        with c3 :
            common_name=name_and_month(specie)
            if common_name :
                st.markdown('Common Name')
                st.markdown(f"#### {common_name}")
            #st.metric('Fruiting Season',fruiting_season)



        for i in range(2) :
                st.markdown(" ")
        st.markdown("###### ⚠️ This is purely informational. Our model may be wrong. Never eat mushrooms based on an app prediction. ")

        for i in range(2) :
                st.markdown(" ")

        st.markdown("### More informations about this Mushroom")
        for i in range(2) :
                st.markdown(" ")
        col1, col2, col3 = st.columns(3)

        specie_with_underscore=specie.lower().replace(" ","_")
        specie_with_tiret=specie.lower().replace(" ","-")
        specie_with_plus=specie.lower().replace(" ","+")
        with col1 :
            expert_url=f"https://www.mushroomexpert.com/{specie_with_underscore}.html"
            nature_url=f"https://www.naturespot.org/species/{specie_with_tiret}"
            if url_exists(expert_url) :
                st.link_button(label='MushroomExpert.com',url=expert_url)
            if url_exists(nature_url) :
                st.link_button(label="naturespot.org",url=nature_url)

        with col2 :
            world_url=f"https://www.mushroom.world/show?n={specie_with_tiret}#google_vignette"
            if url_exists(world_url):
                st.link_button(label='MushroomWorld.com',url=world_url)

        with col3 :
            google_url=f"https://www.google.com/search?tbm=isch&q={specie_with_plus}"
            if url_exists(google_url) :
                st.link_button("🔎 More Pictures",google_url )

for i in range(2) :
    st.markdown(" ")
if specie and specie.strip():
    st.markdown("### Distribution map")
    with st.expander(label='Mushroom distribution on Earth',expanded=False) :
        render_species_heatmap(specie, csv_source="species_points.csv")

for i in range(2) :
    st.markdown(" ")
anses_safety_tips()
