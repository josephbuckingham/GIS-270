import geopandas as gpd 
import pandas as pd 
import numpy as np
import os 


def join_ecozone(in_shp, out_shp): 
    os.makedirs(os.path.dirname(out_shp), exist_ok=True)
    
    input = gpd.read_file(in_shp)
    if 'index_right' in input.columns:
        input = input.drop('index_right', axis=1)
    zones = gpd.read_file(r'input/BEC_BIOGEOCLIMATIC_POLY\BEC_POLY_polygon.shp')
    output = input.sjoin(zones[['geometry', 'ZONE']], predicate='within')
    print(output)
    output.to_file(out_shp, driver='OpenFileGDB')


if __name__ == "__main__":
    join_ecozone(r'processing\fire_not_planted_uid\fire_not_planted_uid.shp', r'processing/fire_not_planted_ecozone/fire_not_planted_ecozone.gdb')
    join_ecozone(r'processing\harvest_not_planted_uid\harvest_not_planted_uid.shp', r'processing/harvest_not_planted_ecozone/harvest_not_planted_ecozone.gdb')
    join_ecozone(r'processing\disturbances_planted\disturbances_planted.gdb', r'processing/planted_ecozone.gdb')
