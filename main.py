import argparse

from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
from src.create_map import create_heat_map
from src.constants import Default_Coordinates, Default_Year


def get_city_coordinates(city: str) -> list[int]:
    """Asks user for city and convert to coordinates."""
    city_name = city.title()
    try:
        geolocator = Nominatim(user_agent="urban_heat_island")
        location = geolocator.geocode(city_name)

    except GeopyError as e:
        raise ValueError(f"Geolocation service error: {e}")

    city_coordinates = [location.latitude, location.longitude]
    print(f"The center coordinates for your city are {city_coordinates}")
    return city_coordinates


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run main program with optional commands.")
    parser.add_argument("-c", "--city", help="Will provide the option to enter a city name in quotes, ex: 'New York'.")
    parser.add_argument("-y", "--year", help="Will provide the option to enter to enter a year, ex: 2020.")
    args = parser.parse_args()

    if args.city:
        location = get_city_coordinates(args.city)
    else:
        location = Default_Coordinates

    if args.year:
        year = int(args.year)
    else:
        year = Default_Year

    print("Hello from urban-heat-island!")
    create_heat_map(location, year)
