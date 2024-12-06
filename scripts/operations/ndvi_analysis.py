import numpy as np 
import pandas as pd 
import geopandas as gpd

def split_planted_disturbances(replanted_csv, replanted_shp):
    replanted = pd.read_csv(replanted_csv).dropna()
    replanted_geo = gpd.read_file(replanted_shp)

    if 'index_right' in replanted_geo.columns:
        replanted_geo = replanted_geo.drop('index_right', axis=1)

    replanted_merge = replanted.merge(replanted_geo[['ACTIVITY_TREATMENT_UNIT_ID', 'disturbance_type']], left_on='ID', right_on='ACTIVITY_TREATMENT_UNIT_ID')
    fire = replanted_merge[replanted_merge['disturbance_type'] == 'fire']
    harvest = replanted_merge[replanted_merge['disturbance_type'] == 'harvest']
    print(fire)
    print(harvest)
    fire.to_csv('processing/fire_planted.csv')
    harvest.to_csv('processing/harvest_planted.csv')

def days_after(df, ref_shp, shp_id):
    shp = gpd.read_file(ref_shp)
    shp['effective_date'] = pd.to_datetime(shp['raster_val'].astype(int) + 1, format='%Y')
    ndvi_effected = df.set_index('ID').merge(shp.set_index(shp_id), left_index=True, right_index=True).drop('geometry', axis=1)
    ndvi_effected['time_delta'] = pd.to_datetime(ndvi_effected['date']) - ndvi_effected['effective_date']
    return ndvi_effected.reset_index().groupby(['ZONE', 'time_delta']).mean(numeric_only=True).reset_index()

def calculate_correlation(df, column_label):
    x = np.array([td.days for td in df.index])
    y = np.array(list(df[column_label]))

    x_f = x[(~np.isnan(list(df[column_label]))) & (x > 0)]
    y_f = y[(~np.isnan(list(df[column_label]))) & (x > 0)]

    m, b = np.polyfit(x_f, y_f, 1)

    return pd.DataFrame({'ZONE': column_label, 'm': m, 'b': b}, index=[0])


def calculate_correlations(days_after, pivot_out):    
    pivot = days_after.pivot(index='time_delta', columns='ZONE', values='MedianValue')

    pivot.to_csv(pivot_out)

    return pd.concat([calculate_correlation(pivot, column) for column in pivot.columns])

def analyze_rate_of_recovery(ndvi_csv, gdb, id, pivot_out, out_csv):
    df = pd.read_csv(ndvi_csv).dropna()
    days_after_df = days_after(df, gdb, id)
    calculate_correlations(days_after_df, pivot_out).to_csv(out_csv)



if __name__ == "__main__": 
    # split_planted_disturbances(r'C:\dev\GIS-270\processing\disturbances_planted.csv', r'C:\dev\GIS-270\processing\planted_ecozone.gdb')


    # analyze_rate_of_recovery('processing/harvest_not_planted.csv', r'processing\harvest_not_planted_ecozone\harvest_not_planted_ecozone.gdb', 'ID', 'output/harvest_timeseries.csv', 'output/harvest_not_planted_recovery.csv')
    # analyze_rate_of_recovery('processing/fire_not_planted.csv', r'processing\fire_not_planted_ecozone\fire_not_planted_ecozone.gdb', 'ID', 'output/fire_timeseries.csv', 'output/fire_not_planted_recovery.csv')
    analyze_rate_of_recovery('processing/harvest_planted.csv', r'processing\planted_ecozone.gdb', 'ACTIVITY_TREATMENT_UNIT_ID', 'output/h_planted_timeseries.csv', 'output/harvest_planted_recovery.csv')
    analyze_rate_of_recovery('processing/fire_planted.csv', r'processing\planted_ecozone.gdb', 'ACTIVITY_TREATMENT_UNIT_ID', 'output/f_planted_timeseries.csv', 'output/fire_planted_recovery.csv')


