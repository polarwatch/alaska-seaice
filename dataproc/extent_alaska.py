#!/usr/bin/env python
# coding: utf-8

import xarray as xr
import numpy as np
import geopandas as gpd
import pandas as pd
from pathlib import Path
import logging
from dask.diagnostics import ProgressBar
from utils.procHelper  import *
from pathlib import Path
from utils.sic import pwSIC25k
from utils.clm import CLM
import configparser

def main():

    # Get project info from config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    PROJ_DIR  = config['DEV']['PROJ_DIR']
    
    # initiate SIC
    crs = 'epsg:3413'
    cdr_id = 'nsidcG02202v4nh1day' #cdr
    nrt_id = 'nsidcG10016v2nh1day' # near-real-time
    var_name = 'cdr_seaice_conc'

    sic_cdr = pwSIC25k(crs, cdr_id, var_name)
    sic_nrt = pwSIC25k(crs, nrt_id, var_name)
    
#    sic_cdr_dataset_id = 'nsidcG02202v4nhmday'
#     sic_nrt_dataset_id = 'nsidcG10016v2nhmday'
#     grid_area_id = 'pstere_gridcell_N25k'
#     var_name = 'cdr_seaice_conc_monthly'

    

#     # Load multiple files
#     fdir = f"{PROJ_DIR}downloaded_files" 
    


#     PROJ_DIR = Path("/Users/sunbak/PolarWatch/codebase/seaice_data_stats")
#     # arctic_sf.shp, ebering_sf, nbering_sf
#     region_title = "ebering"
#     shapefile_path = PROJ_DIR / 'data' / 'akmarineeco' / 'ebering_sf.shp'

#     # Set data urls
#     cdr_url = f'{server}/{data_type}/{sic_cdr_dataset_id}'
#     nrt_url = f'{server}/{data_type}/{sic_nrt_dataset_id}'
#     gridarea_url = f'{server}/{data_type}/{grid_area_id}'

#     # Load datasets with specified chunks and clipping
#     da_cdr = load_and_process_data(server, var_name, data_type, sic_cdr_dataset_id, chunks={'time': 'auto'}, clip_range=(0, 1))
#     da_nrt = load_and_process_data(server, var_name, data_type, sic_nrt_dataset_id, chunks={'time': 'auto'}, clip_range=(0, 1))
#     da_area = load_and_process_data(server, 'cell_area', data_type, grid_area_id, chunks={'x': 'auto', 'y': 'auto'})
#     da_area = da_area.rename({'x': 'xgrid', 'y': 'ygrid'})
#     da_area = set_geo_specs(da_area, xdim="xgrid", ydim="ygrid", crs=crs_project)
#     da_nrt = set_geo_specs(da_nrt, xdim="xgrid", ydim="ygrid", crs=crs_project)
#     da_cdr = set_geo_specs(da_cdr, xdim="xgrid", ydim="ygrid", crs=crs_project)

#     # Clip data to area of interest defined by the shapefile
#     da_cdr_clipped = clip_data_to_shapefile(da_cdr, alaska_shp_proj.geometry, alaska_shp_proj.crs)
#     da_nrt_clipped = clip_data_to_shapefile(da_nrt, alaska_shp_proj.geometry, alaska_shp_proj.crs)
#     area_clipped = clip_data_to_shapefile(da_area, alaska_shp_proj.geometry, alaska_shp_proj.crs)

#     # get the last TIME
#     cdr_latest = format_datetime(da_cdr_clipped['time'].max().item())
#     nrt_latest = format_datetime(da_nrt_clipped['time'].max().item())
#     cdr_latest = da_cdr_clipped['time'][-1].values
#     nrt_latest = da_nrt_clipped['time'][-1].values

#     # Subset CDR data from 1985-01-01 to the latest
#     ice_conc = subset_by_time(da_cdr_clipped, "1985-01-01", cdr_latest)

#     # Append NRT data of the dates later than cdr data
#     if cdr_latest < nrt_latest:
#         start_from = cdr_latest+pd.Timedelta(days=1)
#         ice_conc_nrt = subset_by_time(da_nrt_clipped, start_from, None)
#         ice_conc = append_data(ice_conc, ice_conc_nrt)

#     ice_conc_ext = convert_frac_to_binary(ice_conc, 0.15)

#     ice_ext = compute_extent(ice_conc_ext, area_clipped)

#     write_to_netcdf(ice_ext)
    
#     with ProgressBar():
#         ice_ext.compute()  

#     ice_ext_ts = compute_monthly_extent(ice_ext, dim=["time", "xgrid", "ygrid"])

#     with ProgressBar():
#         ice_ext_ts.compute()
    

#     #Convert to DataFrame and write to file
#     ice_ext_ts = (ice_ext_ts / 1000000) 
#     ice_ext_ts.name = 'seaice_extent'

#     # Convert from square m to square km
    
#     ice_ext_df = (ice_ext_ts.round(decimals=2)
#                         .to_dataframe()
#                         .reset_index()
#                         .drop(['time_year_month','spatial_ref'], axis='columns'))

#     # Write to csv
#     ice_ext_df.to_csv(f'{region_title}_yearly.csv', index=False)  

#     ice_ext_baseline = compute_month_baseline(ice_ext_ts, years = [1985, 2005])

#     with ProgressBar():
#         ice_ext_baseline.compute()
        
#     ice_ext_baseline.name = 'seaice_extent'

#     ice_ext_std = compute_month_stdev(ice_ext_ts, years= [1985, 2005])


#     with ProgressBar():
#         ice_ext_std.compute()

#     ice_ext_stats = xr.Dataset({
#         'ext_baseline': ice_ext_baseline,
#         'ext_std': ice_ext_std
#     })

#     print(".. Converting Xarray to dataframe")
#     ice_ext_df = (ice_ext_stats
#                       .to_dataframe()
#                       .reset_index()
#                       .drop(['spatial_ref'], axis='columns'))

#     # Write to csv
#     ice_ext_df.to_csv(f'{region_title}_baseline.csv', index=False)  

if __name__ == "__main__":
    main()