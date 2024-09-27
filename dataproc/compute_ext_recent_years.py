#!/usr/bin/env python
# coding: utf-8

# import matplotlib.pyplot as plt
import os, sys
import geopandas as gpd
import datetime
import matplotlib.pyplot as plt

# Import the utils module from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '../..'))
sys.path.insert(0, parent_dir)

from pw_data import pwSIC25k

def main():
    # server and data set info
    
    CRS = 'epsg:3413'
    NRT_DAILY_ID = 'nsidcG10016v2nh1day'
    VAR_NAME = 'cdr_seaice_conc'

    REGIONS = dict([('AlaskanArctic', 'arctic_sf.shp'),('NorthernBering', 'nbering_sf.shp'), ('EasternBering', 'ebering_sf.shp')])
    

    for name, shp in REGIONS.items():
        # print(f'name is {name}, and shape file is {shp}')

        # print("reading shapefile : ")
        alaska_shp = gpd.read_file(f'resources/akmarineeco/{shp}')

    # Transform projection to Polar Stereographic Projection
        alaska_shp_proj = alaska_shp.to_crs(crs)

    # Get SIC data
        sic_m = pwSIC25k(crs, nrt_id, var_name, alaska_shp_proj)
        total_area = sic_m.get_total_area_km()
        print(f'total area for {name}: {total_area}')

        # thisyear = datetime.date.today().year
        # lastyear = thisyear - 1
        # ext = sic_m.compute_extent_km([f'{lastyear}-01-01', f'{thisyear}-12-31'])
        # ext_df = (ext
        #         .to_dataframe()
        #         .reset_index()
        #         .drop(['spatial_ref'], axis='columns'))
        # ext_df.to_csv(f'nrt_extent_{name}.csv', index=False)


if __name__ == "__main__":
    main()