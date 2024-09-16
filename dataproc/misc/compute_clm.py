#!/usr/bin/env python
# coding: utf-8

import xarray as xr
import matplotlib.pyplot as plt
import os, sys
import geopandas as gpd
import rasterio
import pandas as pd
import rioxarray
from shapely.geometry import mapping
import time

# Import the utils module from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '../..'))
sys.path.insert(0, parent_dir)

from utils.sic import pwSIC25k
from utils.clm import CLM

def main():
    # server and data set info
    
    ### compute climatology
    # get daily data
    # data processing (processed data as a class)
    
    # call CLM(data:pwData, varname:str,dates:list, freq:str):
    # _computeTimeSeries()
    # _computeAnomalies()
    # _computeTrends()
    # getTimeSeries()
    # getAnomalies()
    # getTrends()
    # plotTimeSeries()


    crs = 'epsg:3413'
    cdr_id = 'nsidcG02202v4nh1day'
    var_name = 'cdr_seaice_conc'

    regions = dict([('AlaskanArctic', 'arctic_sf.shp'), ('NorthernBering', 'nbering_sf.shp'), ('EasternBering', 'ebering_sf.shp')])
    
    crs = 'epsg:3413'
    for name, shp in regions.items():
        print(f'name is {name}, and shape file is {shp}')

        alaska_shp = gpd.read_file(f'resources/akmarineeco/{shp}')

    # Transform projection to Polar Stereographic Projection
        alaska_shp_proj = alaska_shp.to_crs(crs)

        sic_m = pwSIC25k(crs, cdr_id, var_name, alaska_shp_proj)
        ext = sic_m.compute_extent_km(['1985-01-01', '2015-12-31'])
        ext_df = (ext
                .to_dataframe()
                .reset_index()
                .drop(['spatial_ref'], axis='columns'))
        ext_df.to_csv(f'ext_{name}.csv', index=False)
   #     bs.to_csv(f'baseline_{name}.csv', index=False)
 

    # #clm.compute_ts()

    # anom = clm.compute_anom(['2013-01-01', '2013-12-31'])
    # anom[0].plot()


if __name__ == "__main__":
    main()