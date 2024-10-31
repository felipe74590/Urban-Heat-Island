import ee
import geemap
from decouple import config
from src.constants import Cloud_Coverage, Spatial_Res, Geo_Tolerance

HEAT_MAP_GEE_PROJECT = config("GEE_PROJECT")
ee.Initialize(project=HEAT_MAP_GEE_PROJECT)


def create_heat_map(coordinates: str, year: str):
    ## Approximate bounding box for Austin, Texas, creating a layer with legal boundraies
    city = ee.Geometry.Point(coordinates)
    table = ee.FeatureCollection("FAO/GAUL/2015/level2")
    roi = table.filterBounds(city).map(lambda vec: vec.simplify(Geo_Tolerance))  # Region of Interest

    Map = geemap.Map()
    Map.centerObject(roi, 10)

    # Creates image collection of Landsat 8 images, during summer months, filtering out cloud coverage of at least 30%,
    # To convert raw thermal data (from Band 10) to brightness temperature:
    landsat = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2").select("ST_B10")

    filters = (
        landsat.filterBounds(roi)
        .filter(ee.Filter.calendarRange(year, year, "year"))
        .filter(ee.Filter.lt("CLOUD_COVER", Cloud_Coverage))
        .map(
            lambda img: img.multiply(ee.Number(img.get("TEMPERATURE_MULT_BAND_ST_B10")))  # Gain
            .add(ee.Number(img.get("TEMPERATURE_ADD_BAND_ST_B10")))  # Offset
            .copyProperties(img, img.propertyNames())
        )
    )

    num_images = filters.size().getInfo()
    if num_images == 0:
        raise Exception(
            "Error, Not enough images were available for the heat map to be created. Try another city, or a different year."
        )

    print(f"Number of images after filtering: {num_images}")
    thermal_infra_image = landsat.median()
    Map.addLayer(thermal_infra_image.clip(roi), {}, "tir_median", False)

    # Calculate the mean temprature value over a region (roi), setting the spatial resolution in meters (scale=100)
    tir_mean = ee.Number(
        thermal_infra_image.reduceRegion(reducer=ee.Reducer.mean(), geometry=roi, scale=Spatial_Res, bestEffort=True)
        .values()
        .get(0)
    )

    urban_head_island = thermal_infra_image.expression(
        "(tir - mean)/mean", {"tir": thermal_infra_image, "mean": tir_mean}
    ).rename("urban_heat_is")
    Map.addLayer(urban_head_island.clip(roi), {}, "urban_heat_is", False)

    # Classifing: each pixel based on the temperature to be set to the corresponding color.
    uhi_class = (
        ee.Image.constant(0)
        .where(urban_head_island.gte(0).And(urban_head_island.lt(0.005)), 1)
        .where(urban_head_island.gte(0.005).And(urban_head_island.lt(0.010)), 2)
        .where(urban_head_island.gte(0.010).And(urban_head_island.lt(0.015)), 3)
        .where(urban_head_island.gte(0.015).And(urban_head_island.lt(0.020)), 4)
        .where(urban_head_island.gte(0.020), 5)
    )
    Map.addLayer(
        uhi_class.clip(roi),
        {"min": 1, "max": 5, "opacity": 0.50, "palette": ["blue", "green", "yellow", "orange", "red"]},
        "uhi_class",
        True,
    )

    Map.save("heat_map.html")
    # Print the number of images in the filtered collection
