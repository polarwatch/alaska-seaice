"""
Title: Annualized Sea Ice Extent Computation for Alaska Regions
Author: Sunny Bak Hospital
Date: October 8, 2024
Description:
    This script computes the 'annualized' sea ice extent for multiple regions in Alaska from 1985 to the 
    most current year, using the SIC25k class from the `pw_data` module. Region-specific shapefiles for 
    Alaska Fisheries Ecosystem Management Regions are read, reprojected to the Polar Stereographic 
    coordinate system (EPSG:3413), and used to subset and process sea ice concentration data from the NSIDC dataset.

    The annual sea ice extent is calculated over the period from September 1 of each year to August 31 of the following 
    year (e.g., September 2023 to August 2024 for Year 2024). Monthly sea ice extent values are averaged 
    to produce an annualized sea ice extent value. The results are saved in CSV format for each defined region.

    The sea ice extent values for all years, except the most recent, were computed using the CDR 
    sea ice concentration data. Values for the most recent year were calculated using Near-Real-Time data.


Regions:
- Alaskan Arctic
- Northern Bering Sea
- Eastern Bering Sea
- Southeastern Bering Sea

Dependencies:
- pw_data (specifically, SIC25k class for sea ice concentration data handling)
- numpy (numerical operations)
- pandas (data handling and CSV export)
- geopandas (geospatial data processing)
- dask (for parallel computing) 
- gc (garbage collection)
- datetime (for managing date ranges)

Parameters:
- CRS: EPSG:3413 (Polar Stereographic)
- NRT_DAILY_ID: 'nsidcG10016v2nh1day' for near-real-time daily data
- GRID_CELL_AREA_ID: 'pstere_gridcell_N25k'
- VAR_NAME: 'cdr_seaice_conc'

Usage:
    Run this script to compute and export the annual sea ice extent for each defined Alaska region to CSV files.

"""


# Import necessary libraries
from pw_data import SIC25k  # Custom class to handle sea ice concentration data (NSIDC 25k)
import numpy as np  # For numerical operations
import pandas as pd  # For working with DataFrames and exporting data
import geopandas as gpd  # For handling geospatial data (e.g., shapefiles)
from dask.distributed import Client  # Dask for distributed computing
import gc
from datetime import datetime 

def main():
    """
    Main function to load sea ice data, compute annual sea ice extent for specific regions,
    and export the results to CSV files.

    The data used is sea ice concentration from PolarWatch ERDDAP (https://polarwatch.noaa.gov/).
    For data information: 
    - Monthly Near-real-time data: 'nsidcG10016v2nhmday' (variable name: cdr_seaice_conc_monthly)
    - Monthly CDR data: 'nsidcG02202v4nhmday'(variable name: cdr_seaice_conc_monthly)
    
    The output will be CSV files containing annual sea ice extent for the specified regions.
    """

    # Initialize Dask Client for parallel computing. You can customize the cluster if needed.
    # cluster = LocalCluster(n_workers=4, threads_per_worker=2)  # Optional: custom cluster configuration
    client = Client()  # Start a Dask client using the default settings
    print(f"Dashboard is running on: {client.dashboard_link}")  # Print Dask dashboard link for monitoring

    # Define dataset and variable information
    CDR_DATA_ID = 'nsidcG02202v4nhmday'  # ERDDAP ID for CDR monthly sea ice conc data
    NRT_DATA_ID = 'nsidcG10016v2nhmday' # ERDDAP ID for NRT monthly sea ice conc data
    AREA_ID = 'pstere_gridcell_N25k'  # ID for the corresponding area grid
    CRS = 'epsg:3413'  # EPSG code for the polar stereographic projection
    VAR_NAME = 'cdr_seaice_conc_monthly'  # The variable name in the dataset
    thisyear = datetime.now().year
    
    # Define regions and corresponding shapefiles for spatial subsetting
    regions = dict([
       ('AlaskanArctic', 'arctic_sf.shp')  ])
    
      # Alaskan Arctic region
    #    ('NorthernBering', 'nbering_sf.shp'),  # Northern Bering Sea region
    #    ('EasternBering', 'ebering_sf.shp'),  # Eastern Bering Sea region
    #     ('SoutheasternBering', 'se_bering_sf.shp') # Southeastern Bering Sea region
    # ])

    # Instantiate an SIC25k object and load sea ice concentration and grid data
    sic_m = SIC25k(CDR_DATA_ID, VAR_NAME, CRS)  # Initialize SIC25k with ERDDAP data
    sic_m.load_area(AREA_ID)  # Load the corresponding grid cell area data


    # Loop over each region and its corresponding shapefile
    for name, shp in regions.items():
        # Load the shapefile for the region and transform it to the dataset's CRS
        alaska_shp = gpd.read_file(f'resources/akmarineeco/{shp}')  # Read shapefile
        alaska_shp_proj = alaska_shp.to_crs(CRS)  # Reproject the shapefile to match the dataset CRS

        # List to store annual sea ice extent for each region and year
        extents = [] 
        # Loop over each year from 1985-09-01 to 2023-08-31, 
        # computing sea ice extent for each September 1 to August 31 period
        for year in range(1985, thisyear):
            # Subset the dataset by time (September 1 to August 31) and region (clip to the shapefile)
            ds, area = sic_m.subset_dim([f'{year-1}-09-01', f'{year}-08-31'], alaska_shp_proj)

            # Format the sea ice concentration data to binary (0 or 1) using a threshold of 0.15
            sic = sic_m.format_sic(ds, 0.15)  # Sea ice concentration thresholding

            # Compute the sea ice extent in square kilometers for the subset data
            ext = sic_m.compute_extent_km(sic, area)

            # Store the computed extent along with the region name and year in the list
            extents.append({'region': name, 'year': year, 'extent': np.mean(ext.values)})

            # Clean up memory after each iteration to avoid excessive memory usage
            del ds, sic, ext

        # Get the latest from NRT dataset (e.g. Year 2024 refers to 2023-09-01 to 2024-08-31)
        year = thisyear
        sic_latest = SIC25k(NRT_DATA_ID, VAR_NAME, CRS)  # Initialize SIC25k with ERDDAP data
        ds, area = sic_m.subset_dim([f'{year-1}-09-01', f'{year}-08-31'], alaska_shp_proj)
        sic = sic_latest.format_sic(ds, 0.15)  # convert values to be 0 or 1 based on threshold

        # Compute the sea ice extent in square kilometers for the subset data
        ext = sic_latest.compute_extent_km(sic, area)

        # Store the computed extent along with the region name and year in the list
        extents.append({'region': name, 'year': year, 'extent': np.mean(ext.values)})

        # Clean up memory after each iteration to avoid excessive memory usage
        del ds, sic, ext
        gc.collect()

        # Convert the list of extents into a pandas DataFrame and export it to a CSV file
        df = pd.DataFrame(extents)
        df.to_csv(f'annualized_extent_{name}.csv', index=False)  # Save the results for each region

        # Clean up memory after processing each region
        del alaska_shp_proj
        
# Entry point of the script
if __name__ == "__main__":
    main()  # Run the main function
