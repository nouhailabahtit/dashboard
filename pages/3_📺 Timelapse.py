import streamlit as st
import rasterio
import os
import time
import numpy as np
from streamlit_extras.switch_page_button import switch_page


#footer
def goto_page(display_text, destination_page):
    if st.button(display_text):
        switch_page(destination_page)
def footer():
    goto_page("Take me Home 🏠", "Home")


def list_geotiff_files(directory):
    return [file for file in os.listdir(directory) if file.endswith(".tif")]

def read_geotiff(file_path):
    with rasterio.open(file_path) as src:
        data = src.read()  # Read all bands
        metadata = src.meta

    # Extract RGB channels if there are four bands
    if data.shape[0] == 4:
        data = data[:3, :, :]

    return data, metadata

def main():
    st.header("Geotiff Timelapse Viewer", divider="rainbow")
    st.write("")
    #Attribut choice
    attribut= st.selectbox("Attribut", ["Humidity" ,"Precipitation", "Temperature"])
    st.write("")
    # Hardcoded directory containing geotiff files
    geotiff_directory = f'data/tiff/{attribut}'
    geotiff_files = list_geotiff_files(geotiff_directory)

    # Display time-lapse
    st.subheader("Time-lapse Viewer")
    st.write("")
    # Create a horizontal layout for the images
    images = []
    for file in geotiff_files:
        data, _ = read_geotiff(os.path.join(geotiff_directory, file))
        images.append(data)

    # Display time-lapse with a button for smooth transition
    current_frame = st.empty()

    # Display time-lapse with a smooth transition
    frame_idx = 0
    while True:
        current_frame.image(np.transpose(images[frame_idx], (1, 2, 0)), caption= f'Day {frame_idx+1}' , use_column_width=False, width=700)
        time.sleep(0.8)  # Adjust the delay as needed
        frame_idx += 1
        if  frame_idx == 7:
             frame_idx = 0

if __name__ == "__main__":
    main()
footer()

