import streamlit as st
from data_collection.create_map import setting_region_of_interest, get_city_coordinates
from constants import Default_City, Default_Year


def create_ubran_heat_map():
    """"""
    st.set_page_config(layout="centered")
    st.title("Land Surface temperature Heat Map")
    st.markdown("This dashboard displays a heat map created with Google Earth Engine.")

    st.sidebar.title("Options")
    year = st.sidebar.number_input("Enter Year", min_value=2001, max_value=2020, value=Default_Year, step=1)
    city = st.sidebar.text_input("Enter City", value=Default_City)

    try:
        city_coordinates = get_city_coordinates(city)
        Map = setting_region_of_interest(city_coordinates, year, "Heat Map")

        if hasattr(Map, "to_streamlit"):
            Map.to_streamlit()
        else:
            st.error("Map object does not support `to_streamlit()` method.")
    except ValueError:
        st.error


if __name__ == "__main__":
    create_ubran_heat_map()
