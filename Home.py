import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.colored_header import colored_header
from streamlit_card import card
import pandas as pd

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
This project falls within the framework of the Web Mapping course of Surveying Engineering students in Agronomic and Veterinary studies Hassan II.
December, 2023
"""

st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "data\sidebar.png"
st.sidebar.image(logo)


def display_banner():
    st.image("data\Banner.jpg")

def goto_page(display_text, destination_page):
    if st.button(display_text):
        switch_page(destination_page)

def footer():
    goto_page("Take me Home 🏠", "Home")

display_banner()

# Customize page title
colored_header(
    label="Welcome to our Dashboard 🌍",
    description="",
    color_name="blue-70",
)
#⭐
st.info("**A Geospatial Dashboard by Moroccan surveying engineering students.**")
st.text("\n")


st.subheader("Browse our website")

# Switch_page button
col1, col2 = st.columns(2)
with col1 :
    if st.button("Choropleth Map 🎨"):
        switch_page("Choropleth")
    if st.button("Slider Map 🎚️"):
        switch_page("Slider Map")
    if st.button("Timelaps 📺"):
        switch_page("Timelapse")
    if st.button("Split-panel Map 🗺️"):
        switch_page("SplitMap")
with col2 :
    if st.button("Pop-up Map 📌"):
        switch_page("Pop-up")
    if st.button("Call by coordinates 📍"):
        switch_page("Call by coordinates")
    if st.button("Filter Map 🔍"):
        switch_page("Filter Map")
    if st.button("Home page 🏠"):
        switch_page("Home")


colored_header(
    label="Get to know us",
    description="Resume below",
    color_name="blue-70",
)

# Custom CSS to make the text size smaller
custom_css = """
    <style>
        .small-text {
            font-size: 12px;
        }
    </style>
"""


# Cards
col1, col2 = st.columns(2)
with col1 :
    card(
        title="",
        text="Check Nouhaila's resume",
        image="https://raw.githubusercontent.com/nouhailabahtit/Streamlit_essai/main/ana.jpeg",
        url="https://nouhailabahtit.github.io/"
    )

with col2 :
    card(
        title="",
        text="Check Fatima Zahra's resume",
        image="https://raw.githubusercontent.com/nouhailabahtit/Streamlit_essai/main/wjeh_fati.jpeg",
        url="https://fatima-zahra-bamessaoud.github.io/cv/"
    )



footer()