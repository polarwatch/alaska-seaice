#!/usr/bin/env python
# coding: utf-8

# Import necessary libraries
from pw_data import SIC25k  # Custom class to handle sea ice concentration data (NSIDC 25k)
import numpy as np  # For numerical operations
import pandas as pd  # For working with DataFrames and exporting data
import geopandas as gpd
from pathlib import Path
import xarray as xr

#from dask.distributed import Client  # Dask for distributed computing

def main():
 

    # Define dataset and variable information
    CDR_DAILY_ID = 'nsidcG02202v5nh1day'  # CDR (Climate Data Record) daily sea ice conc
    GRID_AREA_ID = 'pstere_gridcell_N25k'  # Grid cell area
    CRS = 'epsg:3413'  # EPSG code for the polar stereographic (north) projection
    VAR_NAME = 'cdr_seaice_conc'  # The variable name in the daily dataset
    RESOURCE_DIR = "resources/akmarineeco"

    # Define regions and corresponding shapefiles
    REGIONS = dict([('AlaskanArctic', 'arctic_sf.shp'),
                    ('NorthernBering', 'nbering_sf.shp'),
                    ('EasternBering', 'ebering_sf.shp'),
                    ('SoutheasternBering', 'se_bering_sf.shp')])

   # Instantiate an SIC25k object and load sea ice concentration and grid data
    sic_m = SIC25k(CDR_DAILY_ID, VAR_NAME, CRS)  # Initialize SIC25k with ERDDAP data
    sic_m.load_area(GRID_AREA_ID)  # Load the corresponding grid cell area data


    # Loop over each region and its corresponding shapefile
    for name, shp in REGIONS.items():
        # Load the shapefile for the region and transform it to the dataset's CRS
        print(f'name is {name}, and shape file is {shp}')
        alaska_shp = gpd.read_file(f'{RESOURCE_DIR}/{shp}')
        alaska_shp_proj = alaska_shp.to_crs(CRS)

        # List to store annual sea ice extent for each region and year
        extents = []
        # Baseline from 1991 to 2020
        for year in range(1991, 2021):

            # Subset the dataset by time (September 1 to August 31) and region (clip to the shapefile)
            ds, area = sic_m.subset_dim([f'{year}-01-01', f'{year}-12-31'], alaska_shp_proj)

            # Format the sea ice concentration data to binary (0, 1, or nan) using a threshold of 0.15
            sic = sic_m.format_sic(ds, 0.15)  # Sea ice concentration thresholding

            # Compute the sea ice extent in square kilometers for the subset data
            ext = sic_m.compute_extent_km(sic, area)

            # Append to the list of all years data
            extents.append(ext)

            # Clean up memory after each iteration to avoid excessive memory usage
            del ds, sic, ext
        
        # Combine each year data into one dataset
        combined_ext = xr.concat(extents, dim = 'time')

        # Transform to data frame 
        ext_df = (combined_ext
                .to_dataframe()
                .reset_index()
                .drop(['spatial_ref'], axis='columns'))
        
        # For saving the data into csv file
#
        #ext_df.to_csv(f'ext_{name}.csv', index=False)

        # Reformat date
        ext_df['time'] = pd.to_datetime(ext_df['time'])
        ext_df['month'] = ext_df['time'].dt.month
        ext_df['day'] = ext_df['time'].dt.day
        ext_df = ext_df.drop(columns=['time'])

        # Group by month and day, then compute the mean for each group
        # mean_values = df.groupby(['month', 'day']).mean().reset_index()
        stats = ext_df.groupby(['month', 'day']).agg(['mean', 'std']).reset_index()
        stats = stats.round(2)
        stats.columns = ['_'
                         .join(col).strip() if col[1] else col[0] for col in stats.columns.values]     
        stats['month_day'] = stats.apply(lambda row: f"{row['month'].astype(int):02d}-{row['day'].astype(int):02d}", axis=1)
        stats.to_csv(f'bs_extent_{name}.csv', index=False)

if __name__ == "__main__":
    main()  
