import ee
import geemap
from decouple import config
from src.constants import Cloud_Coverage, Spatial_Res, Geo_Tolerance, temperature_palette, temp_ranges

HEAT_MAP_GEE_PROJECT = config("GEE_PROJECT")
ee.Initialize(project=HEAT_MAP_GEE_PROJECT)


def create_heat_map(coordinates: str, year: str, create_map=True):
    ## Approximate bounding box for Austin, Texas, creating a layer with legal boundraies
    city = ee.Geometry.Point(coordinates)
    table = ee.FeatureCollection("FAO/GAUL/2015/level2")
    roi = table.filterBounds(city).map(lambda vec: vec.simplify(Geo_Tolerance))  # Region of Interest

    start_time, end_time = f"{year}-01-01", f"{year}-12-31"

    # Creates image collection of Landsat 8 images, during summer months, filtering out cloud coverage of at least 30%,
    # To convert raw thermal data (from Band 10) to brightness temperature:

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
        raise Exception(
            "Error, Not enough images were available for the heat map to be created. Try another city, or a different year."
        )

    print(f"Number of images after filtering: {num_images}")
    thermal_infra_image = landsat.median()

    # Calculate the mean temprature value over a region (roi), setting the spatial resolution in meters (scale=100)
    tir_mean = ee.Number(
        thermal_infra_image.reduceRegion(reducer=ee.Reducer.mean(), geometry=roi, scale=Spatial_Res, bestEffort=True)
        .values()
        .get(0)
    )

    urban_heat_is = thermal_infra_image.expression(
        "(tir - mean)/mean", {"tir": thermal_infra_image, "mean": tir_mean}
    ).rename("urban_heat_is")

    # Classifing: each pixel based on the temperature to be set to the corresponding color.
    uhi_class = (
        ee.Image.constant(0)
        .where(urban_heat_is.gte(0).And(urban_heat_is.lt(0.005)), 1)
        .where(urban_heat_is.gte(0.005).And(urban_heat_is.lt(0.010)), 2)
        .where(urban_heat_is.gte(0.010).And(urban_heat_is.lt(0.015)), 3)
        .where(urban_heat_is.gte(0.015).And(urban_heat_is.lt(0.020)), 4)
        .where(urban_heat_is.gte(0.020), 5)
    )

    if create_map:
        # If I just need to pull data for calculation or train the model, I can prevent creating a new map each run
        # Layers: gloabl admin border layer, heat index layer
        Map = geemap.Map()
        Map.centerObject(city, 13)
        Map.addLayer(roi, {}, "borders", True)
        Map.addLayer(
            uhi_class.clip(roi),
            {"min": 0.371, "max": 3.898, "opacity": 0.47, "palette": temperature_palette},
            "uhi_class",
            True,
        )

        legend_dict = {
            f"{temp_ranges[i]} - {temp_ranges[i+1]}°F": temperature_palette[i] for i in range(len(temp_ranges) - 1)
        }

        Map.add_legend(
            title="Temperature (°F)", legend_keys=list(legend_dict.keys()), legend_colors=list(legend_dict.values())
        )

        Map.save(f"heat_map_{year}.html")
