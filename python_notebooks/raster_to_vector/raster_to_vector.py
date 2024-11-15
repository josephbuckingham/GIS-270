import rasterio
from rasterio.features import shapes
import geopandas as gpd 
from shapely.geometry import shape

mask = None

def make_shp(input, output):
    with rasterio.Env():
        with rasterio.open(input) as src:
            image = src.read(1) # first band
            results = (
            {'properties': {'raster_val': v}, 'geometry': s}
            for i, (s, v) 
            in enumerate(
                shapes(image, mask=mask, transform=src.transform)))
        
        geoms = list(results)
        gpd_polygonized_raster  = gpd.GeoDataFrame.from_features(geoms)
        print(gpd_polygonized_raster)
        gpd_polygonized_raster.to_file(output)
    

if __name__ == "__main__":
    # make_shp('/home/josephb/Dev/GIS-270/python_notebooks/raster_to_vector/input/forest_fire.tif',
    #          '/home/josephb/Dev/GIS-270/python_notebooks/raster_to_vector/output/forest_fire.shp')
    make_shp('/home/josephb/Dev/GIS-270/python_notebooks/raster_to_vector/input/forest_Harvest.tif',
             '/home/josephb/Dev/GIS-270/python_notebooks/raster_to_vector/output/forest_harvest.shp')