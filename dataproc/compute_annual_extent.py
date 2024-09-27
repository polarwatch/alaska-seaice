#!/usr/bin/env python
# coding: utf-8

# Import necessary libraries
from pw_data import SIC25k  # Custom class to handle sea ice concentration data (NSIDC 25k)
import numpy as np  # For numerical operations
import pandas as pd  # For working with DataFrames and exporting data
import geopandas as gpd  # For handling geospatial data (e.g., shapefiles)
from dask.distributed import Client  # Dask for distributed computing

def main():
    """
    Main function to load sea ice data, compute annual sea ice extent for specific regions,
    and export the results to CSV files.

    The data used is sea ice concentration from PolarWatch ERDDAP (https://polarwatch.noaa.gov/).
    For data information: 
    - Daily data: 'nsidcG10016v2nh1day' (cdr_seaice_conc_monthly)
    
    The output will be CSV files containing the most current annual sea ice extent for the specified regions.
    """

    # Initialize Dask Client for parallel computing. You can customize the cluster if needed.
    # cluster = LocalCluster(n_workers=4, threads_per_worker=2)  # Optional: custom cluster configuration
    client = Client()  # Start a Dask client using the default settings
    print(f"Dashboard is running on: {client.dashboard_link}")  # Print Dask dashboard link for monitoring

    # Define dataset and variable information
    erddap_id = 'nsidcG10016v2nh1day'  # ERDDAP ID for NRT daily sea ice concentration data
    area_id = 'pstere_gridcell_N25k'  # ID for the corresponding area grid
    crs = 'epsg:3413'  # EPSG code for the polar stereographic projection
    var_name = 'cdr_seaice_conc'  # The variable name in the dataset

    # Define regions and corresponding shapefiles for spatial subsetting
    regions = dict([
        ('AlaskanArctic', 'arctic_sf.shp'),  # Alaskan Arctic region
        ('NorthernBering', 'nbering_sf.shp'),  # Northern Bering Sea region
        ('EasternBering', 'ebering_sf.shp')  # Eastern Bering Sea region
    ])
    # regions = dict([('AlaskanArctic', 'arctic_sf.shp')])  # Uncomment if only analyzing one region

    # Instantiate an SIC25k object and load sea ice concentration and grid data
    sic_m = SIC25k(erddap_id, var_name, crs)  # Initialize SIC25k with ERDDAP data
    sic_m.load_area(area_id)  # Load the corresponding grid cell area data

    # List to store annual sea ice extent for each region and year
    extents = []

    # Loop over each region and its corresponding shapefile
    for name, shp in regions.items():
        # Load the shapefile for the region and transform it to the dataset's CRS
        alaska_shp = gpd.read_file(f'resources/akmarineeco/{shp}')  # Read shapefile
        alaska_shp_proj = alaska_shp.to_crs(crs)  # Reproject the shapefile to match the dataset CRS

        # Loop over each year from 1995 to 2010, computing sea ice extent for each September 1 to August 31 period
        for year in range(2023, 2024):
            # Subset the dataset by time (September 1 to August 31) and region (clip to the shapefile)
            ds, area = sic_m.subset_dim([f'{year}-09-01', f'{year+1}-08-31'], alaska_shp_proj)

            # Format the sea ice concentration data to binary (0 or 1) using a threshold of 0.15
            sic = sic_m.format_sic(ds, 0.15)  # Sea ice concentration thresholding

            # Compute the sea ice extent in square kilometers for the subset data
            ext = sic_m.compute_extent_km(sic, area)

            # Store the computed extent along with the region name and year in the list
            extents.append({'region': name, 'year': year, 'extent': np.mean(ext.values)})

            # Clean up memory after each iteration to avoid excessive memory usage
            del ds, sic, ext
            
        # Convert the list of extents into a pandas DataFrame and export it to a CSV file
        df = pd.DataFrame(extents)
        df.to_csv(f'{name}_annual_extent.csv', index=False)  # Save the results for each region

        # Clean up memory after processing each region
        del alaska_shp_proj

# Entry point of the script
if __name__ == "__main__":
    main()  # Run the main function
