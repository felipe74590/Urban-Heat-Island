import argparse

from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
from src.create_map import create_heat_map
from src.constants import Default_City, Default_Year


def get_city_coordinates(city: str) -> list[int]:
    """Asks user for city and convert to coordinates."""
    city_name = city.title()
    try:
        geolocator = Nominatim(user_agent="urban_heat_island")
        location = geolocator.geocode(city_name)

    except GeopyError as e:
        raise ValueError(f"Geolocation service error: {e}")

    city_coordinates = [location.longitude, location.latitude]
    print(f"The center coordinates for your city are {city_coordinates}")
    return city_coordinates


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run main program with optional commands.")
    parser.add_argument(
        "-c",
        "--city",
        help="Will provide the option to enter a city name in quotes, ex: 'New York'.",
        default=Default_City,
    )
    parser.add_argument(
        "-y",
        "--year",
        type=int,
        help="Will provide the option to enter to enter a year, ex: 2020.",
        default=Default_Year,
    )
    args = parser.parse_args()

    location = get_city_coordinates(args.city)
    year = args.year

    print("Hello from urban-heat-island!")
    create_heat_map(location, year)
