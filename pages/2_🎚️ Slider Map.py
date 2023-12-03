import streamlit as st
import os
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
from streamlit_toggle import st_toggle_switch
from streamlit_extras.switch_page_button import switch_page


def display_attribute_filters():
    col1,col2=st.columns(2)
    attribut = col1.selectbox('Choose an attribute:', ["Humidity", "Precipitation", "Temperature"])
    return attribut

def display_selected_image(folder_path, cmap,attribut):
    geo_tiff_files = [f for f in os.listdir(folder_path) if f.endswith('.tif')]
    
    if not geo_tiff_files:
        st.warning("No GeoTIFF files found in the specified folder.")
        return
    
    selected_index = st.slider("Slide between the different days", 1, len(geo_tiff_files) , 1)
    selected_file = os.path.join(folder_path, geo_tiff_files[selected_index-1])

    with rasterio.open(selected_file) as src:
        image_data = src.read(1, masked=True)

        fig, ax = plt.subplots(figsize=(3, 3))
        show(image_data, cmap=cmap, ax=ax)
        ax.set_axis_off()
        plt.title(f'{attribut} in day {selected_index}', fontsize=5)
        st.pyplot(fig)

def main():
    st.header("Slider Map", divider="rainbow")
    st.write("")
    attribut = display_attribute_filters()

    folder_paths = {
        'Humidity': 'data\Geotiff\Humidity',
        'Precipitation': 'data\Geotiff\Precipitation',
        'Temperature': 'data\Geotiff\Temperature'
    }

    folder_path = folder_paths[attribut] if not st_toggle_switch('Switch to COG') else f'{folder_paths[attribut]}_COG'
    cmap_dict = {'Humidity': 'Purples', 'Precipitation': 'Blues', 'Temperature': 'Reds'}
    cmap = cmap_dict[attribut]

    display_selected_image(folder_path, cmap,attribut)

def goto_page(display_text, destination_page):
    if st.button(display_text):
        switch_page(destination_page)

def footer():
    st.write("\n")
    goto_page("Take me Home 🏠", "Home")

if __name__ == "__main__":
    main()
    footer()
