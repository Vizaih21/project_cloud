import pandas as pd
import streamlit as st
@st.cache_data
def load_data():
    trips = pd.read_csv("datasets/trips.csv")
    cars = pd.read_csv("datasets/cars.csv")
    cities = pd.read_csv("datasets/cities.csv")
    return trips, cars, cities

cars_df, trips_df, cities_df = load_data()

trips_df_merged = trips_df.merge(cars_df, left_on='car_id', right_on='id', how='left')
trips_df_merged = trips_df_merged.merge(cities_df, on='city_id', how='left')

cols_to_drop = ["id_x", "id_y", "car_id", "city_id", "customer_id"]
existing_cols_to_drop = [col for col in cols_to_drop if col in trips_df_merged.columns]
trips_df_merged = trips_df_merged.drop(columns=existing_cols_to_drop)
