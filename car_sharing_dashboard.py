import pandas as pd
import streamlit as st
import numpy as np 
import matplotlib.pyplot as plt

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


# Visualization 1: Trips Over Time
st.subheader("Trips Over Time")
trips_by_date = trips_df_merged.groupby(trips_df_merged["pickup_time"].dt.date).size().reset_index(name="trip_count")
trips_by_date.columns = ["date", "trip_count"]
st.line_chart(trips_by_date.set_index("date"))

# Visualization 2: Revenue Per Car Model
st.subheader("Revenue Per Car Model")
revenue_by_model = trips_df_merged.groupby("model")["revenue"].sum().reset_index()
revenue_by_model = revenue_by_model.sort_values("revenue", ascending=False)
st.bar_chart(revenue_by_model.set_index("model"))

# Visualization 3: Cumulative Revenue Growth Over Time
st.subheader("Cumulative Revenue Growth Over Time")
revenue_by_date = trips_df_merged.groupby(trips_df_merged["pickup_time"].dt.date)["revenue"].sum().reset_index()
revenue_by_date.columns = ["date", "revenue"]
revenue_by_date["cumulative_revenue"] = revenue_by_date["revenue"].cumsum()
st.area_chart(revenue_by_date.set_index("date")["cumulative_revenue"])

# Visualization 4: Number of Trips Per Car Model
st.subheader("Number of Trips Per Car Model")
trips_by_model = trips_df_merged.groupby("model").size().reset_index(name="trip_count")
trips_by_model = trips_by_model.sort_values("trip_count", ascending=False)
st.bar_chart(trips_by_model.set_index("model"))

# Visualization 5: Alternative to trip duration - Trip Distance by City
st.subheader("Average Trip Distance by City (km)")
distance_by_city = trips_df_merged.groupby("city_name")["distance"].mean().reset_index()
distance_by_city = distance_by_city.sort_values("distance", ascending=False)
st.bar_chart(distance_by_city.set_index("city_name"))

# Visualization 6: Revenue by City
st.subheader("Total Revenue by City")
revenue_by_city = trips_df_merged.groupby("city_name")["revenue"].sum().reset_index()
revenue_by_city = revenue_by_city.sort_values("revenue", ascending=False)
st.bar_chart(revenue_by_city.set_index("city_name"))

# Visualization 7 (Bonus): Revenue vs. Distance Relationship
st.subheader("Revenue vs. Distance Relationship")
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(trips_df_merged["distance"], trips_df_merged["revenue"], alpha=0.5)
ax.set_xlabel("Distance (km)")
ax.set_ylabel("Revenue")
ax.set_title("Revenue vs. Distance")

# Add trend line
z = np.polyfit(trips_df_merged["distance"], trips_df_merged["revenue"], 1)
p = np.poly1d(z)
ax.plot(trips_df_merged["distance"], p(trips_df_merged["distance"]), "r--", alpha=0.8)

st.pyplot(fig)

# Additional bonus visualization: Revenue by Hour of Day
st.subheader("Revenue by Hour of Day")
trips_df_merged["hour_of_day"] = trips_df_merged["pickup_time"].dt.hour
hourly_revenue = trips_df_merged.groupby("hour_of_day")["revenue"].sum().reset_index()
st.line_chart(hourly_revenue.set_index("hour_of_day"))