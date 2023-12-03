import xml.etree.ElementTree as ET
import folium
import streamlit as st
from streamlit_folium import folium_static as st_folium
import geopandas as gpd
from shapely.geometry import Point
from streamlit_extras.switch_page_button import switch_page
import pandas as pd
from folium.plugins import Draw
from selenium import webdriver
import os
import time
from reportlab.pdfgen import canvas
import tempfile


st.set_page_config(layout="wide")


st.header("Find your point", divider="rainbow")
st.write("")
st.subheader("By KML file :")




def display_popup(lat, longe):
    m = folium.Map(location=[30, -7.5], zoom_start=5, tiles="cartodbpositron")
    Draw(export=False).add_to(m)
    # Add geojson with tooltip to the map
    communes = 'data\communes.geojson'
    tooltip = folium.GeoJsonTooltip(fields=['commune'], labels=False)
    folium.GeoJson(communes, name="communes du Maroc", style_function=lambda feature: {
        "fillColor": "red",
        "fillOpacity": 0.5,
        "color": "black",
        "weight": 0.3, },
                   tooltip=tooltip,
                   highlight_function=lambda x: {"fillColor": "#3a616a", "color": "#3a616a", "weight": 2}
                   ).add_to(m)

    # Find the commune based on the location
    query_geom = Point(longe, lat)
    df_point = gpd.GeoDataFrame(geometry=gpd.GeoSeries(query_geom), crs="EPSG:4326")
    communes_gpd = gpd.read_file(communes).to_crs("EPSG:4326")
    result = gpd.sjoin(df_point, communes_gpd, how="left", op="within")

    # Add the marker with popup
    if not result["commune"].isna().all():
        # Location is inside a commune
        commune_name = result["commune"].iloc[0]
        content= f'This location is in {commune_name}'
        icone="ok-sign"
        color="green"
    else:
        # Location is outside Morocco
        content= 'The location is outside Morocco'
        icone="remove-sign"
        color="red"

    folium.Marker(
        location=[lat, longe],
        icon=folium.Icon(color=color, icon=icone),
        popup=folium.Popup(content, show=True, max_width=400)
        ).add_to(m)

    # Display map
    folium.LayerControl(autoZIndex=False).add_to(m)
    st_map = st_folium(m, width=700, height=600)
    return m,content


file = st.file_uploader('Drag KML file here')

st.write("")
st.subheader('Or enter your coordinates manually :')

# Only if KML file uploaded
if file is not None:
    df_meteo = gpd.read_parquet('data/data.parquet')
    def extract_coordinates(kml_content):
        root = ET.fromstring(kml_content)

        coordinates = []

        # Find all coordinates in the KML file
        for placemark in root.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
            for point in placemark.findall('.//{http://www.opengis.net/kml/2.2}Point/{http://www.opengis.net/kml/2.2}coordinates'):
                # Extract coordinates from the coordinates element
                coords = point.text.strip().split(',')
                coordinates.append((float(coords[1]), float(coords[0])))  # (latitude, longitude)

        return coordinates

    # Example usage
    kml_content = file.read()
    extracted_coordinates = extract_coordinates(kml_content)

    # Print the extracted coordinates
    for lat, lon in extracted_coordinates:
        st.write(f"Latitude: {lat}, Longitude: {lon}")

    # Assuming you want to display the popup for the first coordinate in the KML file
    if extracted_coordinates:
        m,_=display_popup(*extracted_coordinates[0])

else:
    col1,col2=st.columns(2)
    lat = col1.number_input("Insert the latitude", value=34.02, min_value=20.97, max_value=35.88,
                          placeholder="Type a number...(ex: 34.02)")
    lon = col2.number_input("Insert the longitude", value=-6.84, min_value=-9.94, max_value=-1.23,
                            placeholder="Type a number...(ex: -6.84)")
    st.write("")
    st.write("")
    m,_= display_popup(lat,lon)


def create_pdf_report(lat, lon, m,content):
    pdf_filename = f"report_Location{lat}_{lon}.pdf"

    # save the map as html
    mapFname = 'output.html'
    m.save(mapFname)
    mapUrl = 'file://{0}/{1}'.format(os.getcwd(), mapFname)
    
    # use selenium to save the html as png image
    driver = webdriver.Edge()
    driver.get(mapUrl)
    
    # wait for 5 seconds for the maps and other assets to be loaded in the browser
    time.sleep(5)
    
    screenshot_filename = f"screenshot_{lat}_{lon}.png"
    driver.save_screenshot(screenshot_filename)
    driver.quit()

    # Create a PDF and add text
    pdf = canvas.Canvas(pdf_filename)
    
    # Add the text with adjusted y-coordinates
    pdf.setFont("Helvetica", 20)
    pdf.drawString(200, 750, "Search Location Report ")
    pdf.setFont("Helvetica", 13)
    pdf.drawString(100, 650, f"Latitude: {lat}")
    pdf.drawString(100, 630, f"Longitude: {lon}")
    pdf.drawString(100, 610, content)

    # Save the screenshot to a temporary file and add it to the PDF
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(open(screenshot_filename, 'rb').read())
        img = tmp_file.name
        pdf.drawInlineImage(img, 50, 200, width=500, height=350)
    
    pdf.setFont("Helvetica", 10)
    pdf.drawString(400, 100, "Made with streamlit")
    pdf.save()
    return pdf_filename    
    
# Add a button to export the results to a PDF
if st.button("Export to PDF"):
    pdf_filename = create_pdf_report(lat,lon,m,_)
    st.success(f"PDF report exported successfully!")
    
#footer
def goto_page(display_text, destination_page):
    if st.button(display_text):
        switch_page(destination_page)

def footer():
    df = pd.read_json("https://api.quotable.io/random")
    st.write("\n")
    goto_page("Take me Home 🏠", "Home")

footer()