import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from selenium import webdriver
from folium.plugins import Draw
import os
import time
from reportlab.pdfgen import canvas
import tempfile
from streamlit_extras.switch_page_button import switch_page


st.header('Discover our Data !', divider='rainbow')
st.write("")


def display_time_filters():
    col1, col2 = st.columns(2)
    attribut = col1.selectbox('Attribut', ["Humidity", "Precipitation", "Temperature"])
    Day = col2.selectbox('Day', [1, 2, 3, 4, 5, 6, 7])
    st.write("")
    st.subheader(f"{attribut} day {Day}")
    st.write("")
    return attribut, Day


def display_map(df, attribut, jour):
    attributJ = attribut + str(jour)
    df[attributJ] = pd.to_numeric(df[attributJ], errors='coerce')
    communes = 'data/communes.geojson'
    m = folium.Map(location=[30, -7.5], zoom_start=5, tiles="cartodbpositron")
    Draw(export=False).add_to(m)
    if attribut == 'Humidity':
        fill_color = "Purples"
        unit = '%'
        legend="Humidity (%)"
    elif attribut == 'Precipitation':
        fill_color = "Blues"
        unit = '%'
        legend="Precipitation (%)"
    elif attribut == 'Temperature':
        fill_color = "YlOrRd"
        unit = '°C'
        legend="Temperature (°C)"

    choropleth = folium.Choropleth(
        geo_data=communes,
        data=df,
        name="Choropleth",
        columns=['commune', attributJ],
        key_on='feature.properties.commune',
        fill_color=fill_color,
        line_opacity=0.6,
        legend_name=legend,
        highlight=True
    ).add_to(m)

    # Tooltip
    df_indexed = df.set_index('commune')
    for feature in choropleth.geojson.data['features']:
        commune = feature['properties']['commune']
        feature['properties'][attributJ] = f'{attribut}: {df_indexed.loc[commune, attributJ]}{unit}'

    choropleth.geojson.add_child(folium.features.GeoJsonTooltip(['commune', attributJ], labels=False))

    folium.LayerControl(autoZIndex=False).add_to(m)
    st_map = st_folium(m, width=700, height=500)
    return m


def create_pdf_report(attribut, Day, m):
    pdf_filename = f"report_{attribut}_D{Day}.pdf"

    # save the map as html
    mapFname = 'output.html'
    m.save(mapFname)
    mapUrl = 'file://{0}/{1}'.format(os.getcwd(), mapFname)
    
    # use selenium to save the html as png image
    driver = webdriver.Edge()
    driver.get(mapUrl)
    
    # wait for 5 seconds for the maps and other assets to be loaded in the browser
    time.sleep(5)
    
    screenshot_filename = f"screenshot_{attribut}_D{Day}.png"
    driver.save_screenshot(screenshot_filename)
    driver.quit()

    # Create a PDF and add text
    pdf = canvas.Canvas(pdf_filename)
    
    # Add the text with adjusted y-coordinates
    pdf.setFont("Helvetica", 20)
    pdf.drawString(200, 750, "Choropleth map Report ")
    pdf.setFont("Helvetica", 13)
    pdf.drawString(100, 650, f"Attribute: {attribut}")
    pdf.drawString(100, 630, f"Day: {Day}")

    # Save the screenshot to a temporary file and add it to the PDF
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(open(screenshot_filename, 'rb').read())
        img = tmp_file.name
        pdf.drawInlineImage(img, 50, 200, width=500, height=350)
    
    pdf.setFont("Helvetica", 10)
    pdf.drawString(400, 100, "Made with streamlit")
    pdf.save()
    return pdf_filename



df_meteo = gpd.read_parquet('data/data.parquet')

# Display Filters and Map
attribut, Day = display_time_filters()
m = display_map(df_meteo, attribut, Day)

# Add a button to export the results to a PDF
if st.button("Export to PDF"):
    pdf_filename = create_pdf_report(attribut, Day, m)
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