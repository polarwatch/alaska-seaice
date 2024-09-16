import os, sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.insert(0, parent_dir)

import pandas as pd
import numpy as np
from datetime import date
import geopandas as gpd
from utils.pw_data import SIC25k

def main():
        
    crs = 'epsg:3413'
    nrt_id = 'nsidcG10016v2nh1day'
    var_name = 'cdr_seaice_conc'
    a_id = 'pstere_gridcell_N25k'
    server="https://polarwatch.noaa.gov/erddap/griddap"
 
    
    regions = dict([('AlaskanArctic', 'arctic_sf.shp'), ('NorthernBering', 'nbering_sf.shp'), ('EasternBering', 'ebering_sf.shp')])
    single = dict([('AlaskanArctic', 'arctic_sf.shp')])

    recent_dat = pd.read_csv("data/ext_recent_AlaskanArctic.csv", parse_dates=['time'])
    start_date = (recent_dat['time'].max() + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = date.today().strftime('%Y-%m-%d')

    for name, shp in single.items():
        print(f'Processing:  {name}')
        alaska_shp = gpd.read_file(f'resources/alaska_shapefiles/{shp}')

        alaska_shp_proj = alaska_shp.to_crs(crs)

        sic = SIC25k(crs=crs, id=nrt_id, varname = var_name, server = server, shape = alaska_shp_proj)
        ext = sic.compute_extent_km(area_id = a_id, dates=[start_date, end_date])

        ext_df = (ext
        .to_dataframe()
        .reset_index()
        .drop(['spatial_ref'], axis='columns'))
        ext_df.to_csv(f'data/ext_recent_{name}.csv', mode='a', index=False, header=False)
    
if __name__ == "__main__":
    main()