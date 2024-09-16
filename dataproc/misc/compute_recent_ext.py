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

from utils.sic import pwSIC25k

def main():
    # server and data set info
    
    crs = 'epsg:3413'
    nrt_id = 'nsidcG10016v2nh1day' # nrt daily
    cdr_id = 'nsidcG10016v2nhmday' # monthly
    var_name = 'cdr_seaice_conc'

    #regions = dict([('AlaskanArctic', 'arctic_sf.shp'),('NorthernBering', 'nbering_sf.shp'), ('EasternBering', 'ebering_sf.shp')])
    regions = dict([('AlaskanArctic', 'arctic_sf.shp')])
    crs = 'epsg:3413'
    for name, shp in regions.items():

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
        # ext_df.to_csv(f'ext_recent_{name}.csv', index=False)


if __name__ == "__main__":
    main()