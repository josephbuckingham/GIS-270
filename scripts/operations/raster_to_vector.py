import rasterio
from rasterio.features import shapes
import geopandas as gpd 
import os

def make_shp(input, output):
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with rasterio.Env():
        with rasterio.open(input) as src:
            image = src.read(1)
            print('making poly generator')
            results = (
            {'properties': {'raster_val': v}, 'geometry': s}
            for i, (s, v) 
            in enumerate(
                shapes(image, mask=None, transform=src.transform))
            if v >= 2003)
            crs = src.crs
        print('making gdf')
        gpd_polygonized_raster  = gpd.GeoDataFrame.from_features(results, crs)
        filtered_polygonized_raster = gpd_polygonized_raster[gpd_polygonized_raster['raster_val'] >= 2003]
        print(filtered_polygonized_raster)
        print('writing shp')
        filtered_polygonized_raster.to_file(output)
        print('done')
    

if __name__ == "__main__":
    print('poly forest')
    make_shp('processing/fire_clipped.tiff', 'processing/fire_polygon/fire_polygon.shp')
    print('poly harvest')
    make_shp('processing/harvest_clipped.tiff', 'processing/harvest_polygon/harvest_polygon.shp')
