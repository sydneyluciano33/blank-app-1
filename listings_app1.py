import streamlit as st # pyright: ignore[reportMissingImports]
import pandas as pd # pyright: ignore[reportMissingImports]
import altair as alt# pyright: ignore[reportMissingImports]
#from vega_datasets import data# pyright: ignore[reportMissingImports]
import json 
import pydeck as pdk# pyright: ignore[reportMissingImports]
import numpy as np# pyright: ignore[reportMissingImports]

st.set_page_config(layout="wide")

df = pd.read_csv("listings.csv")
#st.write(df)
df['price'] = (
    df['price']
    .replace('[\$,]', '', regex=True)
    .astype(float)
)
df['host_acceptance_rate'] = (
    df['host_acceptance_rate']
    .replace('[\%,]', '', regex=True)
    .astype(float)
)


selection = st.selectbox(
    "Select Neighborhood's Attributes",
    options=['Mean Price', 'Room Types', 'Year-Round Availability', 'Mean Host Acceptance Rate']
)

mean_chart = None
room_chart = None
circle_chart = None
acceptance_chart = None



if selection == 'Mean Price':
    mean_prices = df.groupby('neighbourhood_cleansed', as_index=False)['price'].mean()
    mean_chart = alt.Chart(mean_prices).mark_bar().encode(
        x = alt.X('neighbourhood_cleansed:N', title='Neighbourhood'),
        y = alt.Y('price:Q', title='Mean Price',  scale=alt.Scale(type='linear', domain=[0, 400]),
                axis = alt.Axis(values = [0, 50, 100, 150, 200, 250, 300, 350, 400])),
        color = alt.Color('neighbourhood_cleansed:N', legend=None),
    ). properties(
        title = "Mean Price of Listings by Neighbourhood",
        height = 400,
        width = 800

    )
    #st.altair_chart(mean_chart, use_container_width=True)
elif selection == 'Room Types':
    # Example: count of room types per neighbourhood
    room_counts = df.groupby(['neighbourhood_cleansed', 'room_type']).size().reset_index(name='count')
    room_chart = alt.Chart(room_counts).mark_circle().encode(
        x = alt.X('neighbourhood_cleansed:N', title='Neighbourhood'),
        y = alt.Y('room_type:N', title='Room Type'),
        size = alt.Size('count:Q', title='Count'),
        color = alt.Color('room_type:N', title='Room Type')
    ).properties(
        title = "Room Types In Each Neighbourhood",
        height = 600,
        width = 800
    )
    #st.altair_chart(room_chart, use_container_width=True)
elif selection == 'Year-Round Availability':
    circle_chart = alt.Chart(df).mark_circle().encode(
        x=alt.X('neighbourhood_cleansed', title='Neighbourhood'),
        y=alt.Y('availability_365', title='Year-Round Availability'),
        color=alt.Color('room_type', title='Room Type')
    ).properties(
        title='Year-Round Availability vs. Neighbourhood',
        height=600,
        width=800
    )
elif selection == 'Mean Host Acceptance Rate':
    mean_acceptance = df.groupby('neighbourhood_cleansed', as_index=False)['host_acceptance_rate'].mean()
    acceptance_chart = alt.Chart(mean_acceptance).mark_bar().encode(
        x=alt.X('neighbourhood_cleansed', title='Neighbourhood'),
        y=alt.Y('host_acceptance_rate', title='Host Acceptance Rate'),
    ).properties(
        title='Average Host Acceptance Rate vs. Neighbourhood',
    )

st.subheader("Boston AirBnB Listings in Neighbourhoods")
st.write("The first set of charts visualizes various attributes of AirBnB listings in Boston, including mean prices, room types, year-round availability, and host acceptance rates.")
st.write("Select an attribute from the sidebar to explore the data.")
if mean_chart:
    st.altair_chart(mean_chart, use_container_width=True)
if room_chart:
    st.altair_chart(room_chart, use_container_width=True)
if circle_chart:
    st.altair_chart(circle_chart, use_container_width=True)
if acceptance_chart:
    st.altair_chart(acceptance_chart, use_container_width=True)
   

filtered_df = df[df['price'] <= 3000]

linked_selection = alt.selection_point()#(fields=['room_type', 'neighbourhood_cleansed'])

scatter = alt.Chart(filtered_df).mark_circle(size=60, opacity=0.5).encode(
    x=alt.X('number_of_reviews', title='Number of Reviews'), #axis=alt.Axis(values=[0, 50, 100, 150, 200, 250, 300, 350, 400])),
    y=alt.Y('price:Q', title='Price'),
    color=alt.Color('room_type:N', title='Room Type'),
    tooltip=['price', 'number_of_reviews'],
    opacity=alt.condition(linked_selection, alt.value(1), alt.value(0))
).add_params(
    linked_selection
).properties(
    title='Rice vs. Number of Reviews',
    width=500,
    height=300
)
room_price_chart = alt.Chart(filtered_df).mark_circle().encode(
    y=alt.Y('neighbourhood_cleansed:N', title='Neighbourhood'),
    x=alt.X('price:Q', title='Price'),
    color=alt.Color('room_type:N', title='Room Type'),
    tooltip=['neighbourhood_cleansed:N', 'room_type:N', 'price:Q'],
    opacity = alt.condition(linked_selection, alt.value(1), alt.value(0))
).add_params(
    alt.selection_interval(bind='scales'),
    linked_selection
).properties(
    title='Price Distribution of Rooms In Each Neighbourhood',
    width=700,
    height=600
)

col = st.columns(2, gap = "large")

with col[0]:
    st.subheader("Number of Reviews vs. Price and Price Distribution of Rooms In Each Neighbourhood")
    st.write("Explore the relationship between number of reviews and price of AirBnB listings in Boston. Select a point of interest and then scroll down and see what neighbourhood this listing is in.")
    st.altair_chart(scatter & room_price_chart, use_container_width=True)
    #st.altair_chart(room_price_chart, use_container_width=True)
    
with col[1]:  
    st.subheader("Map of Boston AirBnB Listings")
    st.write("This map shows the distribution of AirBnB listings in Boston, with color indicating the type of each listing.")  
    st.write("This map allows you to see where your listing may be and to then look at the surrounding area")
    st.write("Select a room type to filter the listings on the map.")
# Map of Boston AirBnB Listings
    room_type_colors = {
    "Entire home/apt": [0, 128, 255, 160],   # blue
    "Private room": [255, 0, 0, 160],       # red
    "Shared room": [233, 30, 99, 160],       # pink
    "Hotel room": [173, 216, 230, 160],        # light blue
    }
    default_color = [150, 150, 150, 160]
    df["color"] = df["room_type"].map(room_type_colors)
    df["color"] = df["color"].apply(lambda x: x if isinstance(x, list) else default_color)

    room_types = df['room_type'].unique()
    room_type_options = ["All"] + list(room_types)
    selected_room = st.selectbox("Select Room Type", options=room_type_options)
    if selected_room == "All":
        filtered_df = df
    else:
        filtered_df = df[df['room_type'] == selected_room]

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position='[longitude, latitude]',
        get_color='color',
        get_radius=40,
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=filtered_df['latitude'].mean(),
        longitude=filtered_df['longitude'].mean(),
        zoom=11,
        pitch=0,
    )

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{neighbourhood_cleansed}\nRoom: {room_type}\nPrice: {price}"}
    )
    st.pydeck_chart(r)
