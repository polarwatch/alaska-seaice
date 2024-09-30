#!/usr/bin/env python
# coding: utf-8

# Import necessary libraries
from pw_data import SIC25k  # Custom class to handle sea ice concentration data (NSIDC 25k)
import numpy as np  # For numerical operations
import pandas as pd  # For working with DataFrames and exporting data
import geopandas as gpd
from pathlib import Path

#from dask.distributed import Client  # Dask for distributed computing

def main():
 
    regions = dict(config.items('regions'))
    print(regions)


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
    for name, shp in regions.items():
        # List to store annual sea ice extent for each region and year
        extents = []
        # Load the shapefile for the region and transform it to the dataset's CRS
        alaska_shp = gpd.read_file(f'resources/akmarineeco/{shp}')  # Read shapefile
        alaska_shp_proj = alaska_shp.to_crs(crs)  # Reproject the shapefile to match the dataset CRS

        # Loop over each year from 1995 to 2010, computing sea ice extent for each September 1 to August 31 period
        for year in range(2023, 2024):

            ds, area = sic_m.subset_dim([f'{year}-01-01', f'{year}-12-31'], alaska_shp_proj)

            # Format the sea ice concentration data to binary (0 or 1) using a threshold of 0.15
            sic = sic_m.format_sic(ds, 0.15)  # Sea ice concentration thresholding

            # Compute the sea ice extent in square kilometers for the subset data
            ext = sic_m.compute_extent_km(sic, area)

            # Store the computed extent along with the region name and year in the list
            extents.append({''year': year, 'extent': np.mean(ext.values)})

            # Clean up memory after each iteration to avoid excessive memory usage
            del ds, sic, ext
            
        # Convert the list of extents into a pandas DataFrame and export it to a CSV file
        df = pd.DataFrame(extents)
        df.to_csv(f'annualized_extent_{name}.csv', index=False)  # Save the results for each region

        # Clean up memory after processing each region
        del alaska_shp_proj

    for name, shp in REGIONS.items():
        print(f'name is {name}, and shape file is {shp}')

        print("reading shapefile : ")
        alaska_shp = gpd.read_file(RESOURCE_DIR / shp)

    # Transform projection to Polar Stereographic Projection
        alaska_shp_proj = alaska_shp.to_crs(crs)

        sic_m = PIC(crs, cdr_id, var_name, alaska_shp_proj)
        ext = sic_m.compute_extent_km(['1991-01-01', '1993-12-31'])
        ext_df = (ext
                .to_dataframe()
                .reset_index()
                .drop(['spatial_ref'], axis='columns'))
        ext_df.to_csv(f'ext_{name}.csv', index=False)

        # SAVE THE DATA
        df = pd.read_csv(f'ext_all{name}.csv')

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