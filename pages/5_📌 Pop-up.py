import folium
from folium.plugins import MarkerCluster
from folium.plugins import Draw
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_folium import folium_static as st_folium
import geopandas as gpd
import pandas as pd
from reportlab.pdfgen import canvas


st.set_page_config(layout="wide")

st.header("Graph in a popup", divider="rainbow")
st.write('')
st.write('')
st.subheader('Zoom and click on the marker to show the graph !')
st.write('')

def display_popup(df):
    #add geojson to the map
    communes ='data/communes.geojson'
    m = folium.Map(location=[30,-7.5], zoom_start=5 ,tiles="cartodbpositron")
    Draw(export=True).add_to(m)
    folium.GeoJson(communes, name="communes du Maroc",style_function=lambda feature: {
        "fillColor": "#74c2d4",
        "color": "black",
        "weight": 0.3,}
                   ).add_to(m)
    
    # Add marker cluster
    marker_cluster = MarkerCluster(name='High charts popup')
    
    #Make sure all the columns values are numeric 
    df['Latitude']= df['geometry'].y
    df['Longitude']= df['geometry'].x
    attribut=["Humidity" ,"Precipitation", "Temperature"]
    for j in range(3):
        for k in range(1,8):
            attributJ = attribut[j]+str(k)   
      
    # Generate a simple plot using Matplotlib   
    X= ["J1", "J2", "J3", "J4", "J5", "J6", "J7"]      
    for i in range(df.shape[0]):
        Humidity= [df[f"Humidity{j+1}"][i] for j in range(7)]
        Precip= [df[f"Precipitation{j+1}"][i] for j in range(7)]
        Temp= [df[f"Temperature{j+1}"][i] for j in range(7)]
        plt.plot(X,Humidity,'o-c',label='Humidity %')
        plt.plot(X, Precip,'o:b', label='Precipitation %')
        plt.plot(X,Temp,'o-r', label= 'Temperature °C')
        title= f'Meteo indicators of {df["commune"][i]}'
        plt.title(title)
        plt.xlabel('Days')
        plt.ylabel('Values')
        plt.grid(axis = 'y')
        plt.legend(loc="upper left")
        plt.ylim(0,max(df[f"Humidity{j+1}"][i] for j in range(7))+25)
        # Save the Matplotlib plot to a BytesIO object
        image_stream = BytesIO()
        plt.savefig(image_stream, format='png')
        plt.close()
        # Convert the BytesIO object to a base64-encoded string
        image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
        
        #Generate the marker
        popup_content = folium.Popup(f'<img src="data:image/png;base64,{image_base64}" width="400">')
        marker_info = {
            'location': [df['Latitude'][i], df['Longitude'][i]],
            'popup': popup_content
        }
        marker_cluster.add_child(folium.Marker(**marker_info))
        
    # Map display
    m.add_child(marker_cluster)
    folium.LayerControl(autoZIndex=False).add_to(m)
    st_map = st_folium(m, width=700, height=500)
    return m


def create_pdf(commune, df):
    for i in range(len(df)):
        if df["commune"][i] == commune:
            X = ["D1", "D2", "D3", "D4", "D5", "D6", "D7"]
            Humidity = [df[f"Humidity{j+1}"][i] for j in range(7)]
            Precip = [df[f"Precipitation{j+1}"][i] for j in range(7)]
            Temp = [df[f"Temperature{j+1}"][i] for j in range(7)]
            plt.plot(X, Humidity, 'o-c', label='Humidity %')
            plt.plot(X, Precip, 'o:b', label='Precipitation %')
            plt.plot(X, Temp, 'o-r', label='Temperature °C')
            title = f'Meteo indicators of {commune}'
            plt.title(title)
            plt.xlabel('Days')
            plt.ylabel('Values')
            plt.grid(axis='y')
            plt.legend(loc="upper left")
            plt.ylim(0, max(df[f"Humidity{j+1}"][i] for j in range(7)) + 25)
            plt.savefig("graph.png", format='png')
            plt.close()  # Close the Matplotlib plot
            break  # Stop after finding the relevant commune

    pdf_filename = f"report_{commune}_graphic.pdf"
    pdf = canvas.Canvas(pdf_filename)

    # Add the text with adjusted y-coordinates
    pdf.setFont("Helvetica", 20)
    pdf.drawString(200, 750, "Attributes Graphic Report ")
    pdf.setFont("Helvetica", 13)
    pdf.drawString(100, 680, f"Commune: {commune}")

    # Save the figure to the PDF
    pdf.drawInlineImage("graph.png", 100, 350, width=400, height=300)

    # Create a table as a Pandas DataFrame
    table_data = {
        'Day': ["D1", "D2", "D3", "D4", "D5", "D6", "D7"],
        'Humidity(%)': [df[f"Humidity{j+1}"][i] for j in range(7)],
        'Precipitation(%)': [df[f"Precipitation{j+1}"][i] for j in range(7)],
        'Temperature(°C)': [df[f"Temperature{j+1}"][i] for j in range(7)],
    }
    table_df = pd.DataFrame(table_data)

    # Convert the table to an image
    fig, ax = plt.subplots(figsize=(6, 2))  # Adjust the size as needed
    ax.axis('off')
    ax.table(cellText=table_df.values, colLabels=table_df.columns, loc='center', cellLoc='center', bbox=[0, 0, 1, 1])
    plt.savefig("table.png", format='png', bbox_inches='tight')
    plt.close()
    pdf.drawInlineImage("table.png", 125, 180, width=350, height=150)

    pdf.setFont("Helvetica", 10)
    pdf.drawString(400, 80, "Made with streamlit")
    pdf.save()

#Display Filters and Map
df_meteo = gpd.read_parquet('data/data.parquet')
m = display_popup(df_meteo)

# Add a button to export the results to a PDF
col1,col2 = st.columns(2)
commune= col1.selectbox("Choose the commune to export its graph",[df_meteo["commune"][i] for i in range(len(df_meteo))])

if st.button("Export to PDF"):
    pdf_filename = create_pdf(commune,df_meteo)
    st.success(f"PDF report exported successfully!")
