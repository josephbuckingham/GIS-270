import geopandas as gpd
import os 


def reproject(in_shp, out_shp): 
    os.makedirs(os.path.dirname(out_shp), exist_ok=True)
    shp = gpd.read_file(in_shp)
    shp.geometry = shp.geometry.to_crs('EPSG:3005')
    shp.to_file(out_shp)



if __name__ == "__main__":
    reproject('processing/fire_polygon/fire_polygon.shp', 'processing/fire_reprojected/fire_reprojected.shp')
    reproject('processing/harvest_polygon/harvest_polygon.shp', 'processing/harvest_reprojected/harvest_reprojected.shp')