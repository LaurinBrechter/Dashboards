import pandas as pd
import pydeck as pdk
import streamlit as st
import numpy as np

# makes it so that we are not running this part every time the application is rerun (e.g. every time we change a filter value)
@st.cache(persist=True, allow_output_mutation=True) 
def load_data(path):
    data_raw = pd.read_excel(path)
    
    deselected_cols = ["Minimum_kms_to_be_covered_in_a_day", "Driver_Name", "Driver_MobileNo", "Driver_MobileNo", 
                       "Curr_lat", "Curr_lon", "Current_Location", "DestinationLocation", "DestinationLocation_Code",
                       "OriginLocation_Code"]

    relevant_cols = [i for i in data_raw.columns if i not in deselected_cols]

    data = data_raw[relevant_cols]
    
    data[["org_lat", "org_lon"]] = data["Org_lat_lon"].str.split(",", 1, expand=True)
    data[["des_lat", "des_lon"]] = data["Des_lat_lon"].str.split(",", 1, expand=True)
    
    data["Des_lat_lon"] = data["Des_lat_lon"].str.split(",", 1).apply(lambda x: list(map(float, x))+ [0])
    data["Org_lat_lon"] = data["Org_lat_lon"].str.split(",", 1).apply(lambda x: list(map(float, x)) + [0])
    
    data[["org_lat", "org_lon", "des_lat", "des_lon"]] = data[["org_lat", "org_lon", "des_lat", "des_lon"]].astype(np.float64)
    
    return data
    
data = load_data("F:\\Data\\Delivery truck trip data.xlsx")

line_layer = pdk.Layer(
    "LineLayer",
    data[["org_lat", "org_lon", "des_lat", "des_lon"]],
    get_source_position=["org_lon", "org_lat"],
    get_target_position=["des_lon", "des_lat"],
    get_color=[255,255,153]
)

scatter_layer = pdk.Layer(
             "ScatterplotLayer",
             data = data[["org_lat", "org_lon", "des_lat", "des_lon"]],
             get_position=["org_lon", "org_lat"],
             radius=100,
             pickable=True,
             elevation_scale=4,
             elevation_range=[0,1000],
             auto_highlight=True,
             radius_scale=6,
             radius_min_pixels=1,
             get_fill_color=[255, 140, 0],
             get_radius = 200
         )

fig = pdk.Deck(
    map_style="dark", # mapbox://styles/mapbox/light-v9
    initial_view_state={
        "latitude": 13.1550, 
        "longitude": 80.1960,
        "zoom": 11,
        "pitch":50 # pitched at 50 degrees
    },
    layers=[scatter_layer, line_layer]
)

st.write(fig)
    
