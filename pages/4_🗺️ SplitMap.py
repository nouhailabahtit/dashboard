import streamlit as st
import leafmap.foliumap as leafmap

st.header("Split-panel Map", divider='rainbow')
st.write("")
st.write("")
col1, col2 = st.columns(2)
with col1:
    st.markdown('<span style="font-size:20px;">Choose the left layer:</span>', unsafe_allow_html=True)
    attributl = st.selectbox('Attribute', ["Humidity", "Precipitation", "Temperature"], key='left_attribute')
    jourl = st.selectbox('Day', [1, 2, 3, 4, 5, 6, 7], key='left_day')
    attributJl = attributl + str(jourl)
with col2:
    st.markdown('<span style="font-size:20px;">Choose the right layer:</span>', unsafe_allow_html=True)
    attributr = st.selectbox('Attribute', ["Humidity", "Precipitation", "Temperature"], key='right_attribute')
    jourr = st.selectbox('Day', [1, 2, 3, 4, 5, 6, 7], key='right_day')
    attributJr = attributr + str(jourr)
    
if attributJl == attributJr:
        st.markdown(':loudspeaker: <span style="color:red;">Choose different attribute or day</span>', unsafe_allow_html=True)
else:
        st.write("")
        on = st.toggle('Use Cloud Optimized Geotiff :barely_sunny:')
        if on:
            urlR = f'data\Geotiff\{attributr}_COG\{attributJr}_cog.tif'
            urlL = f'data\Geotiff\{attributl}_COG\{attributJl}_cog.tif'
        else:
            urlR = f'data\Geotiff\{attributr}\{attributJr}.tif'
            urlL = f'data\Geotiff\{attributl}\{attributJl}.tif'
            
        # select basemap option    
        col1, col2 = st.columns([3, 1])
        options = list(leafmap.basemaps.keys())
        index = options.index("CartoDB.Voyager")
        with col2:
            basemap = st.selectbox("Select a basemap:", options, index)
        
        # Create a Leafmap Folium Map
        map = leafmap.Map(location=[30.758207, -8.802633], zoom_start=5, scrollWheelZoom=False)
        map.add_basemap(basemap)    
        map.split_map(urlL, urlR)
        map.to_streamlit(width=700, height=600)



