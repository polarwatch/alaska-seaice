# import os, sys
import pandas as pd
import numpy as np
from datetime import date
import geopandas as gpd
from utils import *
import xarray as xr

SERVER="https://polarwatch.noaa.gov/erddap/griddap"

def main():
        
    # PolarWatch dataset ID of the NSIDC near real time 
    # sea ice conc in the northern hemisphere (nh)
    nrt_id = 'nsidcG10016v2nh1day'

    # EPSG code used for polar stereographic projection (nh)
    crs = 'epsg:3413'
    var_name = 'cdr_seaice_conc'

    # Define regions and corresponding shapefiles for spatial subsetting
    regions = dict([
       ('AlaskanArctic', 'arctic_sf.shp'),  # Alaskan Arctic region
       ('NorthernBering', 'nbering_sf.shp'),  # Northern Bering Sea region
       ('EasternBering', 'ebering_sf.shp'),  # Eastern Bering Sea region
        ('SoutheasternBering', 'se_bering_sf.shp') # Southeastern Bering Sea region
    ])

    # Get the latest date from recently updated file
    recent_dat = pd.read_csv("data/nrt_extent_NorthernBering.csv", parse_dates=['date'])
    start_date = (recent_dat['date'].max() + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = date.today().strftime('%Y-%m-%d')

    # Get most recent sea ice data
    sic = get_var_data(SERVER, nrt_id, crs, var_name, [start_date, end_date])

    # If new data are available, continue
    if sic.size > 0:

        # Loop through regions
        for name, shp in regions.items():
            print(f'Processing:  {name}')
            
            # load regional shapefile
            alaska_shp = gpd.read_file(f'resources/alaska_shapefiles/{shp}')

            # transform the shape to the data projection
            alaska_shp_proj = alaska_shp.to_crs(crs)

            # Load regional grid cell area data
            ds_area = get_area(name)
            
            # Clip sic data using shape
            clipped_sic = clip_data(sic, alaska_shp_proj)

            # Compute extent with sic and grid cell area
            ext = compute_extent_km(clipped_sic, ds_area)

            # Format the dataset and append to csv file
            ext_df = (ext
                    .to_dataframe()
                    .reset_index()
                    .drop(['spatial_ref'], axis='columns')
                    .rename(columns={'time': 'date'}))
            try:
                ext_df.to_csv(f'data/nrt_extent_{name}.csv', mode='a', index=False, header=False)
                print('Successfully updated ext_recent files')
            except : 
                print(f'Failed to update the ext_recent files for {name}')
    else:
        print("Processing Stopped: No new data available. ")

if __name__ == "__main__":
    main()
