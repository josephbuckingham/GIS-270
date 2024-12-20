import rasterio
from rasterio.features import shapes
import geopandas as gpd 
from shapely.geometry import shape

mask = None

def make_shp(input, output):
    with rasterio.Env():
        with rasterio.open(input) as src:
            image = src.read(1) # first band
            print('making poly generator')
            results = (
            {'properties': {'raster_val': v}, 'geometry': s}
            for i, (s, v) 
            in enumerate(
                shapes(image, mask=mask, transform=src.transform))
            if v > 2003)
            crs = src.crs
        print(crs)
        print('gen to list')
        print('making gpd')
        gpd_polygonized_raster  = gpd.GeoDataFrame.from_features(results, crs)
        filtered_polygonized_raster = gpd_polygonized_raster[gpd_polygonized_raster['raster_val'] >= 2003]
        print(filtered_polygonized_raster)
        print('writing shp')
        filtered_polygonized_raster.to_file(output)
        print('done')
    

if __name__ == "__main__":
    print('poly forest')
    # make_shp(r'C:\dev\GIS-270\python_notebooks\clip_raster\output\forest_fire.tiff',
    #          r'./output/forest_fire/forest_fire.shp')
    print('poly harvest')
    make_shp(r'C:\dev\GIS-270\python_notebooks\clip_raster\output\forest_harvest.tiff',
             r'./output/forest_harvest/forest_harvest.shp')