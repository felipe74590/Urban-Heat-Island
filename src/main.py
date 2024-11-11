import argparse
from data_collection.create_map import setting_region_of_interest, get_city_coordinates

from constants import DEFAULT_CITY, DEFAULT_YEAR


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run main program with optional commands.")
    parser.add_argument(
        "-c",
        "--city",
        help="Will provide the option to enter a city name in quotes, ex: 'New York'.",
        default=DEFAULT_CITY,
    )
    parser.add_argument(
        "-y",
        "--year",
        type=int,
        help="Will provide the option to enter to enter a year, ex: 2020.",
        default=DEFAULT_YEAR,
    )

    parser.add_argument(
        "-t", "--task", type=str, help="Select between 'Train Model' and 'Heat Map'. ", default="Heat Map"
    )
    args = parser.parse_args()

    location = get_city_coordinates(args.city)

    print("Hello from urban-heat-island!")
    setting_region_of_interest(location, args.year, args.task)
