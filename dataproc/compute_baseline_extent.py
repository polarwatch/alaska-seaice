#!/usr/bin/env python
# coding: utf-8

# Import necessary libraries
from pw_data import SIC25k  # Custom class to handle sea ice concentration data (NSIDC 25k)
import numpy as np  # For numerical operations
import pandas as pd  # For working with DataFrames and exporting data
import geopandas as gpd
import configparser
from pathlib import Path

from dask.distributed import Client  # Dask for distributed computing

def main():
 
    config = configparser.ConfigParser()
    regions = dict(config.items('regions'))
    print(regions)


    # Define dataset and variable information
    CDR_DAILY_ID = 'nsidcG02202v4nh1day'  # CDR (Climate Data Record) daily sea ice conc
    NRT_DAILY_ID = 'nsidcG10016v2nh1day' # NRT (Near-real-time data) daily sea ice conc
    GRID_AREA_ID = 'pstere_gridcell_N25k'  # Grid cell area
    CRS = 'epsg:3413'  # EPSG code for the polar stereographic (north) projection
    VAR_NAME = 'cdr_seaice_conc'  # The variable name in the dataset
    RESOURCE_DIR = "resources/akmarineeco"

    # Define regions and corresponding shapefiles
    REGIONS = dict([('AlaskanArctic', 'arctic_sf.shp'),
                    ('NorthernBering', 'nbering_sf.shp'),
                    ('EasternBering', 'ebering_sf.shp'),
                    ('SoutheasternBering', 'se_bering_sf.shp')])
  
    for name, shp in REGIONS.items():
        print(f'name is {name}, and shape file is {shp}')

        print("reading shapefile : ")
        alaska_shp = gpd.read_file(RESOURCE_DIR / shp)

    # Transform projection to Polar Stereographic Projection
        alaska_shp_proj = alaska_shp.to_crs(crs)

        sic_m = pwSIC25k(crs, cdr_id, var_name, alaska_shp_proj)
        ext = sic_m.compute_extent_km(['1985-01-01', '2015-12-31'])
        ext_df = (ext
                .to_dataframe()
                .reset_index()
                .drop(['spatial_ref'], axis='columns'))
        ext_df.to_csv(f'ext_{name}.csv', index=False)

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