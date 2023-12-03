import folium
import pandas as pd
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium
from selenium import webdriver
import os
import time
from reportlab.pdfgen import canvas
import tempfile
from reportlab.lib.pagesizes import letter
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(layout="wide")

st.header("Filter Data", divider="rainbow")
st.write('')
st.write('')
st.subheader('Adjust the scales and add/eliminate dates')


# Read GeoDataFrame from GeoJSON file
df = gpd.read_file("data/communes.geojson")
gdf = gpd.read_parquet('data/data.parquet')

# --- STREAMLIT SELECTION
Date = gdf['Date'].unique().tolist()
Deaths = gdf['Deaths'].unique().tolist()
Births = gdf['Births'].unique().tolist()

Deaths_selection = st.slider('Deaths :',
                            min_value=min(Deaths),
                            max_value=max(Deaths),
                            value=(min(Deaths), max(Deaths))
                            )

Births_selection = st.slider('Births :',
                             min_value=min(Births),
                             max_value=max(Births),
                             value=(min(Births), max(Births))
                             )

Date_selection = st.multiselect('Date:',
                                Date,
                                default=Date)

# --- FILTER DATAFRAME BASED ON SELECTION
mask = (gdf['Deaths'].between(*Deaths_selection)) & (gdf['Births'].between(*Births_selection)) & (gdf['Date'].isin(Date_selection))
filtered_df = df[mask]
filtered_df['Date'] = filtered_df['Date'].astype(str)

# Map the GeoDataFrame with colored classes
st.subheader("Filtered Map")

m = folium.Map(location=[30, -7.5], zoom_start=5, tiles="cartodbpositron")

# Create a GeoJson layer for the filtered data
folium.GeoJson(
    filtered_df,
    style_function=lambda x: {'fillColor': 'orange', 'color': 'orange', 'weight': 1},
    highlight_function=lambda x: {'fillColor': 'yellow', 'color': 'yellow', 'weight': 2},
    tooltip=folium.features.GeoJsonTooltip(['commune','Births','Deaths'])
).add_to(m)

# Add other map elements or controls as needed
folium.LayerControl(autoZIndex=False).add_to(m)

# Display the map in Streamlit
col1,col2= st.columns([5,2])
with col1:
    st_folium(m, width=700, height=500)
with col2:
    number_of_result = filtered_df.shape[0]
    st.markdown(f'*Communes résultantes : {number_of_result}*')
    st.write(filtered_df["commune"])


def create_pdf_report(Deaths_selection, Births_selection, Date_selection, number_of_result):
    pdf_filename = "filter_report.pdf"

    # save the map as html
    mapFname = 'output.html'
    m.save(mapFname)
    mapUrl = 'file://{0}/{1}'.format(os.getcwd(), mapFname)
    
    # use selenium to save the html as png image
    driver = webdriver.Edge()
    driver.get(mapUrl)
    
    # wait for 5 seconds for the maps and other assets to be loaded in the browser
    time.sleep(5)
    screenshot_filename = f"screenshot_filter.png"
    driver.save_screenshot(screenshot_filename)
    driver.quit()
    
    # Use reportlab to generate a PDF

    pdf = canvas.Canvas(pdf_filename, pagesize=letter)

    pdf.setFont("Helvetica", 20)
    pdf.drawString(200, 750, "Filtered data Report")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 650, f"Births in between {min(Births_selection)} and {max(Births_selection)} people")
    pdf.drawString(100, 630, f"Deaths in between {min(Deaths_selection)} and {max(Deaths_selection)} people")
    y_coordinate = 610
    line_height = 20
    long_line = "The selected dates are: " + ", ".join([str(element) for element in Date_selection])
    chunks = [long_line[i:i + 80] for i in range(0, len(long_line), 80)]
    for chunk in chunks:
        pdf.drawString(100, y_coordinate, chunk)
        y_coordinate -= line_height
        
        # Save the screenshot to a temporary file and add it to the PDF
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(open(screenshot_filename, 'rb').read())
        img = tmp_file.name
        pdf.drawInlineImage(img, 50, 200, width=500, height=350)

    pdf.drawString(100, 150, f"The result is {number_of_result} communes")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(400, 100, "Made with Streamlit")
    pdf.showPage()
    pdf.save()
    return pdf_filename   

    
# Add a button to export the results to a PDF
if st.button("Export to PDF"):
    pdf_filename = create_pdf_report(Deaths_selection, Births_selection, Date_selection, number_of_result)
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