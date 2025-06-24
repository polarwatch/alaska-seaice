"""
This script computes sea ice extent for multiple regions in the Alaskan Arctic and Bering Sea
using the SIC25k class from the `pw_data` module. It reads region-specific shapefiles, 
transforms them into the proper coordinate reference system (CRS), and processes sea ice concentration data 
from the NSIDC dataset to calculate the sea ice extent within the regions.

Sea ice extent is computed for each region for the time period of September 1 (last year) to December 31 (this year). 
The results are saved as CSV files, where sea ice concentration is thresholded into binary values (0 or 1) 
and sea ice extent is computed in square kilometers.

Dependencies:
- os
- sys
- geopandas
- datetime
- matplotlib
- pw_data (specifically, the SIC25k class)

Author: Sunny Bak Hospital
Date: September 27, 2024

"""

import os, sys
import geopandas as gpd
import datetime
import matplotlib.pyplot as plt
from pw_data import SIC25k

def main():
    """
    Main function to process sea ice extent for multiple regions in Alaska.

    """

    # Define constants
    CRS = 'epsg:3413'  # Polar Stereographic North projection
    NRT_DAILY_ID = 'nsidcG10016v3nh1day'  # Dataset ID for near real-time sea ice data
    VAR_NAME = 'cdr_seaice_conc'  # Variable name for sea ice concentration
    GRID_CELL_AREA_ID = 'pstere_gridcell_N25k'  # Grid cell area ID for sea ice extent calculations

    # Define regions and corresponding shapefiles
    REGIONS = dict([('AlaskanArctic', 'arctic_sf.shp'),
                    ('NorthernBering', 'nbering_sf.shp'),
                    ('EasternBering', 'ebering_sf.shp'),
                    ('SoutheasternBering', 'se_bering_sf.shp')])

    # Instantiate SIC25k object and load grid area data
    sic_m = SIC25k(NRT_DAILY_ID, VAR_NAME, CRS)
    sic_m.load_area(GRID_CELL_AREA_ID)  


    # If the current month is September (9) or later, use the current year, otherwise use the previous year.
    today = datetime.date.today()
    lastyear = today.year if today.month > 8 else today.year - 1

    # Loop over each region and its corresponding shapefile
    for name, shp in REGIONS.items():
        # Load the shapefile and project it to the dataset's CRS
        alaska_shp = gpd.read_file(f'resources/akmarineeco/{shp}')
        alaska_shp_proj = alaska_shp.to_crs(CRS)

        # Subset the dataset by time and region (ex: 2023-09-01 to 2025-08-31)
        ds, area = sic_m.subset_dim([f'{lastyear-1}-09-01', f'{lastyear+1}-12-31'], alaska_shp_proj)

        # Format sea ice concentration data to binary using a 0.15 threshold
        sic = sic_m.format_sic(ds, 0.15)

        # Compute sea ice extent in square kilometers
        ext = sic_m.compute_extent_km(sic, area)
        
        # Clean up memory to avoid excessive usage
        del alaska_shp, alaska_shp_proj, ds, sic 

        # Convert xarray object to a dataframe, reformat, and save as CSV
        ext_df = (ext
                  .to_dataframe()
                  .reset_index()
                  .drop(['spatial_ref'], axis='columns')
                  .rename(columns={'time': 'date'}))
        
        ext_df.to_csv(f'nrt_extent_{name}.csv', index=False)  


if __name__ == "__main__":
    main()
