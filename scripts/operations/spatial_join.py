import geopandas as gpd 
import pandas as pd
import os 

# left join using intersect, keeps left geometry and dissolves geometry that matches same area
def join(left_shp, right_shp, out_gdb):
    os.makedirs(os.path.dirname(out_gdb), exist_ok=True)

    left = gpd.read_file(left_shp)
    right = gpd.read_file(right_shp)
    
    out = left.sjoin(right)
    
    out['geometry'] = out.normalize()
    out = out.drop_duplicates('geometry')
    out.to_file(out_gdb, driver='OpenFileGDB')

# drops from right shp the matching indices in the joined shp resulting in a reduction of the shapes that were joined
def drop_joined(joined_shp, right_shp, out_shp):
    os.makedirs(os.path.dirname(out_shp), exist_ok=True)

    joined = gpd.read_file(joined_shp)
    right = gpd.read_file(right_shp)

    duplicate_indices = joined['index_right']
    out = right.drop(duplicate_indices)
    out.to_file(out_shp)

def reformat_and_filter(harvest_planted_gdb, fire_planted_gdb, out_gdb):
    os.makedirs(os.path.dirname(out_gdb), exist_ok=True)

    harvest_planted: gpd.GeoDataFrame = gpd.read_file(harvest_planted_gdb)
    fire_planted: gpd.GeoDataFrame = gpd.read_file(fire_planted_gdb)

    # Change date time to year 
    harvest_planted['ATU_COMPLETION_DATE'] = harvest_planted['ATU_COMPLETION_DATE'].dt.year
    fire_planted['ATU_COMPLETION_DATE'] = fire_planted['ATU_COMPLETION_DATE'].dt.year

    # matching from both harvest and fire that have same treatment units (ie. matching geometry)
    matching = fire_planted.merge(harvest_planted[['ACTIVITY_TREATMENT_UNIT_ID', 'raster_val']], on='ACTIVITY_TREATMENT_UNIT_ID', how='inner')
    # remove from original data frames rows that took were in the resulting merge 
    harvest_planted = harvest_planted.set_index('ACTIVITY_TREATMENT_UNIT_ID').drop(matching['ACTIVITY_TREATMENT_UNIT_ID'])
    fire_planted = fire_planted.set_index('ACTIVITY_TREATMENT_UNIT_ID').drop(matching['ACTIVITY_TREATMENT_UNIT_ID'])
    
    # Give all valid rows to fire dropping unnecessary harvest year and renaming fire year back to original label
    matching_given_to_fire = matching.drop('raster_val_y', axis=1).rename({'raster_val_x': 'raster_val'}, axis=1).set_index('ACTIVITY_TREATMENT_UNIT_ID')

    # re add matching given to fire to fire dataframe 
    fire_planted = pd.concat([fire_planted, matching_given_to_fire])

    # give disturbance type descriptors to data frames and then append them together 
    fire_planted['disturbance_type'] = 'fire'
    harvest_planted['disturbance_type'] = 'harvest'

    disturbances_planted = pd.concat([fire_planted, harvest_planted])

    # write to a geodatabase to preserve long column names
    disturbances_planted.to_file(out_gdb, driver='OpenFileGDB')


if __name__ == "__main__":
    # join('input/RSLT_PLANTING.gdb', 'processing/fire_simplified/fire_simplified.shp', 'processing/fire_planted/fire_planted.gdb')
    # drop_joined('processing/fire_planted/fire_planted.gdb', 'processing/fire_simplified/fire_simplified.shp', 'processing/fire_not_planted/fire_not_planted.shp')

    # join('input/RSLT_PLANTING.gdb', 'processing/harvest_simplified/harvest_simplified.shp', 'processing/harvest_planted/harvest_planted.gdb')
    # drop_joined('processing/harvest_planted/harvest_planted.gdb', 'processing/harvest_simplified/harvest_simplified.shp', 'processing/harvest_not_planted/harvest_not_planted.shp')
    reformat_and_filter('processing/harvest_planted/harvest_planted.gdb', 'processing/fire_planted/fire_planted.gdb', 'processing/disturbances_planted/disturbances_planted.gdb')


    


