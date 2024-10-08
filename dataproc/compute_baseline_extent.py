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
    CDR_DAILY_ID = 'nsidcG02202v4nh1day'  # CDR (Climate Data Record) daily sea ice conc
    GRID_AREA_ID = 'pstere_gridcell_N25k'  # Grid cell area
    CRS = 'epsg:3413'  # EPSG code for the polar stereographic (north) projection
    VAR_NAME = 'cdr_seaice_conc'  # The variable name in the dataset
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
        print(f'Processing: name is {name}')

        alaska_shp = gpd.read_file(f'{RESOURCE_DIR}/{shp}')

    # Transform projection to Polar Stereographic Projection
        alaska_shp_proj = alaska_shp.to_crs(CRS)
        extents = []
        for year in range(1991, 2011):
            # Subset the dataset by time (Jan 1 to Dec 31) and region (clip to the shapefile)
            ds, area = sic_m.subset_dim([f'{year}-01-01', f'{year}-12-31'], alaska_shp_proj)

            # Format the sea ice concentration data to binary (0 or 1) using a threshold of 0.15
            sic = sic_m.format_sic(ds, 0.15)  # Sea ice concentration thresholding

            del ds

            # Compute the sea ice extent in square kilometers for the subset data
            ext = sic_m.compute_extent_km(sic, area)

            # append computed data
            extents.append(ext)

        # Combine ext data along time dimension
        ext_xr = xr.concat(extents, dim="time")
        ext_df = (ext_xr
            .to_dataframe()
            .reset_index()
            .drop(['spatial_ref'], axis='columns'))
              
        ext_df.to_csv(f'ext_{name}.csv', index=False) 
        del sic, ext, area


    # # Create new columns for month and day
        ext_df['time'] = pd.to_datetime(ext_df['time'])
   
        ext_df['month'] = ext_df['time'].dt.month
        ext_df['day'] = ext_df['time'].dt.day

        # Drop the original time column
        ext_df = ext_df.drop(columns=['time'])

        # Group by 'month' and 'day', then calculate mean and std, and reset the index
        stats = ext_df.groupby(['month', 'day']).agg(['mean', 'std']).reset_index()

        # Flatten the MultiIndex columns
        stats.columns = ['_'.join(col).strip() if col[1] else col[0] for col in stats.columns.values]

        # Round the values
        stats = stats.round(2)

        # Create a 'date' column from 'month' and 'day'
        stats['month_day'] = stats.apply(lambda row: f"{int(row['month']):02d}-{int(row['day']):02d}", axis=1)

        # Save to CSV without the index
        stats.to_csv(f'bs_extent_{name}.csv', index=False)


if __name__ == "__main__":
    main()  
