"""
Title: Compute total area in square km for Alaska Ecosystem Regions

Description: 
    For each defined region, it calculates the total sea ice extent in square kilometers
    based on 25K polar stereographic projection and the regional shapefiles.
    The results are printed for each region.

Regions:
- Alaskan Arctic
- Northern Bering Sea
- Eastern Bering Sea
- Southeastern Bering Sea

Dependencies:
- os
- sys
- geopandas
- datetime
- matplotlib
- pw_data (specifically, the pwSIC25k class)

Parameters:
- CRS: EPSG:3413 (Polar Stereographic)
- NRT_DAILY_ID: 'nsidcG10016v2nh1day'
- GRID_CELL_AREA_ID: 'pstere_gridcell_N25k'
- VAR_NAME: 'cdr_seaice_conc'

Usage:
    Run this script to compute and display total sea ice extent for each region.

Author: Sunny Bak Hospital
Date: October 8, 2024
"""
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

    # Define regions and corresponding shapefiles for spatial subsetting
    REGIONS = dict([
       ('AlaskanArctic', 'arctic_sf.shp'),  # Alaskan Arctic region
       ('NorthernBering', 'nbering_sf.shp'),  # Northern Bering Sea region
       ('EasternBering', 'ebering_sf.shp'),  # Eastern Bering Sea region
        ('SoutheasternBering', 'se_bering_sf.shp') # Southeastern Bering Sea region
    ])

    for name, shp in REGIONS.items():
        # print(f'name is {name}, and shape file is {shp}')

        # print("reading shapefile : ")
        alaska_shp = gpd.read_file(f'resources/akmarineeco/{shp}')

    # Transform projection to Polar Stereographic Projection
        alaska_shp_proj = alaska_shp.to_crs(CRS)

    # Get SIC data
        sic_m = pwSIC25k(CRS, NRT_DAILY_ID, VAR_NAME, alaska_shp_proj)
        total_area = sic_m.get_total_area_km()
        print(f'total area for {name}: {total_area}')


if __name__ == "__main__":
    main()