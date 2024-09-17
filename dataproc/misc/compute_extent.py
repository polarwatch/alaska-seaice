#!/usr/bin/env python
# coding: utf-8

import xarray as xr
import matplotlib.pyplot as plt
import os, sys
import geopandas as gpd
import rasterio
import pandas as pd
import rioxarray
from shapely.geometry import mapping

# Import the utils module from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '../..'))
sys.path.insert(0, parent_dir)

from utils.pw_data import pwData

#from utils.clm import CLM

def main():
    # server and data set info
    
    crs = 'epsg:3413'
    cdr_id = 'nsidcG02202v4nh1day'
    var_name = 'cdr_seaice_conc'

    #regions = dict([('AlaskanArctic', 'arctic_sf.shp'), ('NorthernBering', 'nbering_sf.shp'), ('EasternBering', 'ebering_sf.shp')])
    regions = dict([('AlaskanArctic', 'arctic_sf.shp')])
    crs = 'epsg:3413'
    for name, shp in regions.items():
        print(f'name is {name}, and shape file is {shp}')

    #     print("reading shapefile : ")
    #     alaska_shp = gpd.read_file(f'resources/akmarineeco/{shp}')

    # # Transform projection to Polar Stereographic Projection
    #     alaska_shp_proj = alaska_shp.to_crs(crs)

    #     sic_m = pwSIC25k(crs, cdr_id, var_name, alaska_shp_proj)
    #     ext = sic_m.compute_extent_km(['1985-01-01', '2015-12-31'])
    #     ext_df = (ext
    #             .to_dataframe()
    #             .reset_index()
    #             .drop(['spatial_ref'], axis='columns'))
    #     ext_df.to_csv(f'ext_{name}.csv', index=False)

        df = pd.read_csv(f'ext_{name}.csv')
    # Create new columns for month and day
        df['time'] = pd.to_datetime(df['time'])
   
        df['month'] = df['time'].dt.month
        df['day'] = df['time'].dt.day

        # Drop the original time column
        df = df.drop(columns=['time'])

        # Group by month and day, then compute the mean for each group
        # mean_values = df.groupby(['month', 'day']).mean().reset_index()
        stats = df.groupby(['month', 'day']).agg(['mean', 'std']).reset_index()
        stats.columns = ['_'.join(col).strip() if col[1] else col[0] for col in stats.columns.values]     
        stats.round(2)   
        stats['date'] = stats.apply(lambda row: f"{row['month'].astype(int):02d}-{row['day'].astype(int):02d}", axis=1)
        stats.reset_index().to_csv(f'bs_{name}.csv', index=False)
        

if __name__ == "__main__":
    main()