import ee 
import geemap
from decouple import config

HEAT_MAP_GEE_PROJECT = config("GEE_PROJECT")
ee.Initialize(project=HEAT_MAP_GEE_PROJECT)


def main():
    print("Hello from urban-heat-island!")
    ## Approximate bounding box for Austin, Texas, creating a layer with legal boundraies 
    city = ee.Geometry.Point([-97.74414483713234,30.26562490046467])
    table = ee.FeatureCollection("FAO/GAUL/2015/level2")
    roi = table.filterBounds(city) # Region of Interest

    Map = geemap.Map()
    Map.centerObject(roi, 10)
    Map.addLayer(roi)

    # Creates image collection of Landsat 8 images, during summer months, filtering out cloud coverage of at least 30%,
    # To convert raw thermal data (from Band 10) to brightness temperature:
    landsat = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2").select('ST_B10')

    filtered = (
        landsat.filterBounds(roi).filterDate('2020-01-01', '2020-12-31').filter(ee.Filter.lt('CLOUD_COVER', 30))
        .map(lambda img: img.multiply(ee.Number(img.get("TEMPERATURE_MULT_BAND_ST_B10")))  # Gain
            .add(ee.Number(img.get("TEMPERATURE_ADD_BAND_ST_B10")))  # Offset
            .copyProperties(img, img.propertyNames())
        )
    )

    num_images = filtered.size().getInfo()
    print(f'Number of images after filtering: {num_images}')

    thermal_mean = landsat.median()
    Map.addLayer(thermal_mean.clip(roi),{},'tir_median', False)
    Map.save("heat_map.html")
    # Print the number of images in the filtered collection
    



if __name__ == "__main__":
    main()
