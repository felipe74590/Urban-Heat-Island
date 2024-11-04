import ee
import geemap.foliumap as geemap
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
from decouple import config
from constants import Cloud_Coverage, Spatial_Res, Geo_Tolerance, temperature_palette, temp_ranges

HEAT_MAP_GEE_PROJECT = config("GEE_PROJECT")
ee.Initialize(project=HEAT_MAP_GEE_PROJECT)


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


def collect_LST(roi, start_time, end_time):
    """
    Collect Land Surface Temperature (LST) data. Creates image collection of Landsat 8 images,
    filtering out cloud coverage, while converting raw thermal data (from Band 10) to brightness temperature.
    """

    landsat = (
        ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        .select("ST_B10")
        .filterDate(start_time, end_time)
        .filterBounds(roi)
        .filter(ee.Filter.lt("CLOUD_COVER", Cloud_Coverage))
        .map(
            lambda img: img.multiply(ee.Number(img.get("TEMPERATURE_MULT_BAND_ST_B10")))  # Gain
            .add(ee.Number(img.get("TEMPERATURE_ADD_BAND_ST_B10")))  # Offset
            .copyProperties(img, img.propertyNames())
        )
    )
    num_images = landsat.size().getInfo()
    if num_images == 0:
        raise RuntimeError(
            "Error, Not enough images were available for the heat map to be created. Try another city, or a different year."
        )

    print(f"Number of images after filtering: {num_images}")
    thermal_infra_image = landsat.median()
    land_surface_temp_data = (
        thermal_infra_image.reduceRegion(reducer=ee.Reducer.mean(), geometry=roi, scale=Spatial_Res, bestEffort=True)
        .values()
        .get(0)
    )

    return thermal_infra_image, land_surface_temp_data


def collect_Land_Use(roi, start_time, end_time):
    """
    Collect Land Use data to help predict land surface temperature based on land use, vegetation, and other features.
    """
    land_use_dataset = (
        ee.ImageCollection("MODIS/006/MCD12Q1")
        .select("LC_Type1")
        .filterDate(start_time, end_time)
        .filterBounds(roi)
        .first()
    )
    if not land_use_dataset:
        raise Exception(f"Land use data for the year {start_time} is not available.")

    land_use_values = land_use_dataset.reduceRegion(
        reducer=ee.Reducer.mode(), geometry=roi.geometry(), scale=30, bestEffort=True
    )
    # Check if the land use data for the year exists

    return land_use_values


def create_heat_map(roi, city, start_time, end_time):
    """
    Create urban heat map based on city selected and time frame provided.
    """
    thermal_image, lst_values = collect_LST(roi, start_time, end_time)

    # Calculate the mean temprature value over a region (roi), setting the spatial resolution in meters (scale=100)
    tir_mean = ee.Number(lst_values)

    urban_heat_is = thermal_image.expression("(tir - mean)/mean", {"tir": thermal_image, "mean": tir_mean}).rename(
        "urban_heat_is"
    )

    # Classifing: each pixel based on the temperature to be set to the corresponding color.
    uhi_class = (
        ee.Image.constant(0)
        .where(urban_heat_is.gte(0).And(urban_heat_is.lt(0.005)), 1)
        .where(urban_heat_is.gte(0.005).And(urban_heat_is.lt(0.010)), 2)
        .where(urban_heat_is.gte(0.010).And(urban_heat_is.lt(0.015)), 3)
        .where(urban_heat_is.gte(0.015).And(urban_heat_is.lt(0.020)), 4)
        .where(urban_heat_is.gte(0.020), 5)
    )

    # If I just need to pull data for calculation or train the model, I can prevent creating a new map each run
    # Layers: gloabl admin border layer, heat index layer
    Map = geemap.Map()
    Map.centerObject(city, 13)
    Map.addLayer(roi, {}, "borders", True)
    Map.addLayer(
        uhi_class.clip(roi),
        {"min": 0.371, "max": 3.898, "opacity": 0.40, "palette": temperature_palette},
        "uhi_class",
        True,
    )

    # legend_dict = {
    #     f"{temp_ranges[i]} - {temp_ranges[i+1]}°F": temperature_palette[i] for i in range(len(temp_ranges) - 1)
    # }

    # Map.add_legend(
    #     title="Temperature (°F)", legend_keys=list(legend_dict.keys()), legend_colors=list(legend_dict.values())
    # )
    # Map.save(f"heat_map_{start_time}.html")
    return Map


def setting_region_of_interest(coordinates, year: str, task: str):
    """
    Cases: Train Model, Heat Map
    """
    ## Approximate bounding box for Austin, Texas, creating a layer with legal boundraies
    city = ee.Geometry.Point(coordinates)
    table = ee.FeatureCollection("FAO/GAUL/2015/level2")
    roi = table.filterBounds(city).map(lambda vec: vec.simplify(Geo_Tolerance))  # Region of Interest
    start_date, end_date = f"{year}-01-01", f"{year}-12-31"

    match task:
        case "Train Model":
            print("Train Model, this is limited to certain years due to data provided.")
            # Organize when preparing ML model
            # collect_LST(roi, start_date, end_date)
            # collect_Land_Use(roi, start_date, end_date)

        case "Heat Map":
            heat_map = create_heat_map(roi, city, start_date, end_date)
            return heat_map
