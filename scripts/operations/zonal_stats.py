import glob
from multiprocessing import connection
import concurrent.futures
import geopandas as gpd 
import pandas as pd
import numpy as np
import datetime
import rasterio
from rasterio import features
import os

def rasterize_to_extent(in_shp, reference_tif, out_tiff):
    print(reference_tif)
    shp = gpd.read_file(in_shp)
    geom = [(geometry, value) for geometry, value in zip(shp.geometry, shp.ACTIVITY_TREATMENT_UNIT_ID)]

    with rasterio.open(reference_tif) as ref: 
        meta = ref.meta.copy()
        height, width = ref.shape
        transform = ref.transform

    rasterized_array = features.rasterize(geom, 
                                          out_shape = (height, width),
                                          fill=0,
                                          transform=transform,
                                          all_touched=False,
                                          default_value=0,
                                          dtype=None)
    
    with rasterio.open(out_tiff, 'w', **meta) as dst: 
        dst.write(rasterized_array, 1)
    return rasterized_array
        
def zonal_stats_array(data, zones, nodata_val):

    zones = np.where(data != nodata_val, zones, nodata_val)
    
    df = pd.DataFrame({'ID': zones, 'Value': data})
    df = df[df.ID != nodata_val] 
    
    df = df.groupby('ID').agg(
         {'Value': ['min', 'max', 'mean', 'median', 'std', 'count']}
         )
    
    df = df.droplevel(0, axis=1).rename(
         columns = {'min': 'MinValue',
                    'max': 'MaxValue',
                    'mean': 'MeanValue',
                    'median': 'MedianValue',
                    'std': 'StdevValue',
                    'count': 'CountValue'})
    
    df = df.reset_index()
    
    return df

def make_zonal_df(data_tiff, zones):

    with rasterio.open(data_tiff, 'r') as src: 
        stats_df = zonal_stats_array(src.read(1).ravel(), zones.ravel(), src.nodata)

    zones_list = pd.DataFrame({'ID': np.unique(zones.ravel())})

    joined = zones_list.set_index('ID').join(stats_df.set_index('ID'), on='ID')
    
    date = datetime.datetime.strptime(os.path.basename(data_tiff).split('.')[4], "%Y%j")
    joined['date'] = date

    return joined.reset_index()


def make_ndvi_timeseries(polygon, zones_name):
    tiff_dir = 'weekly_max_ndvi/data/clipped'
    tiffs = os.listdir(tiff_dir)

    # zones_tiff = f'processing/{zones_name}.tiff'
    # zones = rasterize_to_extent(polygon, os.path.join(tiff_dir, tiffs[0]), zones_tiff)
    zones_2022 = rasterize_to_extent(polygon, os.path.join(tiff_dir, ([tiff for tiff in tiffs if int(tiff.split('.')[4][0:4]) >= 2022])[0]), f'processing/zone_test.tiff')

    futures = []

    pool = concurrent.futures.ProcessPoolExecutor(16)

    
    for tiff in tiffs: 
        if not tiff.endswith('.tif'):
            continue
        print(tiff)
        tiff_path = os.path.join(tiff_dir, tiff)
        if int(tiff.split('.')[4][0:4]) >= 2022: 
            futures.append(pool.submit(make_zonal_df, tiff_path, zones_2022))
        # else: 
        #     futures.append(pool.submit(make_zonal_df, tiff_path, zones))

    pool.shutdown(wait=True)

    dfs = [future.result() for future in futures if future.done() and future.exception() is None]

    print(dfs)

    final: pd.DataFrame = pd.concat(dfs)
    print(final)
    final.to_csv(f'output/{zones_name}.csv')



if __name__ == "__main__":
    make_ndvi_timeseries('disturbances_planted/disturbances_planted.gdb', 'disturbances_planted')

