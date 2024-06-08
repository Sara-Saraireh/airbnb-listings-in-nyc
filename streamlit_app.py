import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

# Add Airbnb logo
st.image("pngkey.com-airbnb-logo-png-605967.png", width=200)

DATE_TIME = "last_review"
Data_URL = "AB_NYC_2019.csv"

st.title("Airbnb Listings in New York City")
st.markdown("This application is a Streamlit dashboard that can be used "
            "to analyze Airbnb listings in NYC.")

@st.cache_data(persist=True)
def load_data(nrows):
    data = pd.read_csv(Data_URL, nrows=nrows, parse_dates=['last_review'])
    data.dropna(subset=['latitude', 'longitude'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    return data

data = load_data(15000)

st.header("Where are the most expensive Airbnb listings in NYC?")
price_limit = st.slider("Price range of Airbnb listings", 0, 1000, 500)
st.map(data.query("price >= @price_limit")[["latitude", "longitude"]].dropna(how="any"))

st.header("How many listings are available in each neighborhood?")
neighborhood = st.selectbox("Select a neighborhood", data['neighbourhood_group'].unique())
neighborhood_data = data[data['neighbourhood_group'] == neighborhood]

midpoint = (np.average(neighborhood_data["latitude"]), np.average(neighborhood_data["longitude"]))
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data=neighborhood_data[['latitude', 'longitude']],
        get_position=["longitude", "latitude"],
        auto_highlight=True,
        radius=100,
        extruded=True,
        pickable=True,
        elevation_scale=4,
        elevation_range=[0, 1000],
        ),
    ],
))

if st.checkbox("Show raw data", False):
    st.subheader(f"Raw data for {neighborhood}")
    st.write(neighborhood_data)

st.subheader("Breakdown by room type")
room_type_data = neighborhood_data['room_type'].value_counts().reset_index()
room_type_data.columns = ['room_type', 'count']

fig = px.bar(room_type_data, x='room_type', y='count', hover_data=['room_type', 'count'], height=400)
st.write(fig)

st.header("Top 5 hosts by number of listings")
top_hosts = data['host_name'].value_counts().head(5).reset_index()
top_hosts.columns = ['host_name', 'number_of_listings']
st.write(top_hosts)

# Additional Features
st.header("Listings Availability by Month")
data['month'] = data['last_review'].dt.month
monthly_data = data['month'].value_counts().reset_index()
monthly_data.columns = ['month', 'count']

fig2 = px.bar(monthly_data, x='month', y='count', labels={'month': 'Month', 'count': 'Number of Listings'}, title="Number of Listings by Month")
st.write(fig2)

st.header("Average Price by Room Type")
room_type_price_data = data.groupby('room_type')['price'].mean().reset_index()
fig3 = px.pie(room_type_price_data, values='price', names='room_type', title='Average Price by Room Type')
st.write(fig3)

st.header("Correlation Between Price and Number of Reviews")
fig4 = px.scatter(data, x='price', y='number_of_reviews', title="Correlation Between Price and Number of Reviews", labels={'price': 'Price', 'number_of_reviews': 'Number of Reviews'})
st.write(fig4)

st.header("Average Price in Each Neighborhood")
neighborhood_price_data = data.groupby('neighbourhood_group')['price'].mean().reset_index()
fig5 = px.bar(neighborhood_price_data, x='neighbourhood_group', y='price', labels={'neighbourhood_group': 'Neighborhood', 'price': 'Average Price'}, title="Average Price in Each Neighborhood")
st.write(fig5)
