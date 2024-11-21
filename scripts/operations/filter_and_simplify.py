import geopandas as gpd 
import os 

def filter_by_area(in_shp, out_shp, min_value):
    os.makedirs(os.path.dirname(out_shp), exist_ok=True)
    shp = gpd.read_file(in_shp) 
    shp = shp[shp.geometry.area > min_value]
    shp.to_file(out_shp)

def simplify(in_shp, out_shp, tolerance):
    os.makedirs(os.path.dirname(out_shp), exist_ok=True)
    shp = gpd.read_file(in_shp)
    shp.geometry = shp.geometry.simplify(25)
    shp.to_file(out_shp)


if __name__ == "__main__":
    filter_by_area('processing/fire_reprojected/fire_reprojected.shp', 'processing/fire_filtered/fire_filtered.shp', 10000)
    filter_by_area('processing/harvest_reprojected/harvest_reprojected.shp', 'processing/harvest_filtered/harvest_filtered.shp', 10000)

    simplify('processing/fire_filtered/fire_filtered.shp', 'processing/fire_simplified/fire_simplified.shp', 25)
    simplify('processing/harvest_filtered/harvest_filtered.shp', 'processing/harvest_simplified/harvest_simplified.shp', 25)