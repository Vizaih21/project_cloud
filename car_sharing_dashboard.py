import pandas as pd
import streamlit as st
@st.cache_data
def load_data():
    trips = pd.read_csv("datasets/trips.csv")
    cars = pd.read_csv("datasets/cars.csv")
    cities = pd.read_csv("datasets/cities.csv")
    return trips, cars, cities

trips_df, cars_df, cities_df = load_data()

trips_df_merged = trips_df.merge(cars_df, left_on='car_id', right_on='id', how='left')
trips_df_merged = trips_df_merged.merge(cities_df, on='city_id', how='left')

cols_to_drop = ["id_x", "id_y", "car_id", "city_id", "customer_id"]
existing_cols_to_drop = [col for col in cols_to_drop if col in trips_df_merged.columns]
trips_df_merged = trips_df_merged.drop(columns=existing_cols_to_drop)

trips_df_merged["pickup_time"] = pd.to_datetime(trips_df_merged["pickup_time"])
trips_df_merged["dropoff_time"] = pd.to_datetime(trips_df_merged["dropoff_time"])
trips_df_merged["pickup_date"] = trips_df_merged["pickup_time"].dt.date

selected_brand = st.sidebar.selectbox(
    "Select a Car Brand", 
    options=["All"] + list(trips_df_merged["brand"].unique()), 
)

if selected_brand != "All":
    trips_df_merged = trips_df_merged[trips_df_merged["brand"] == selected_brand]

total_trips_df = trips_df_merged.shape[0]  

total_distance = trips_df_merged["distance"].sum()  

top_car_df = (
    trips_df_merged.groupby("model")["revenue"]
    .sum()
    .idxmax()
) 

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Trips", value=total_trips_df)

with col2:
    st.metric(label="Top Car Model by Revenue", value=top_car_df)

with col3:
    st.metric(label="Total Distance (km)", value=f"{total_distance:,.2f}")

st.write("### Preview of the Merged Trips DataFrame")
st.write(trips_df_merged.head())

