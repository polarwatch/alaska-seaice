# utils.py


import xarray as xr
import geopandas as gpd
import rasterio
import pandas as pd
import rioxarray
from shapely.geometry import mapping
import numpy as np


def get_var_data(server, id, crs, varname, dates):
    """
    Loads ERDDAP sea ice data from PolarWatch and returns data for the specified date range with geographic specifications.

    Args:
        server (str): The server URL.
        id (str): The ERDDAP dataset ID.
        crs (str): The coordinate reference system (CRS) to be used.
        varname (str): The variable name within the dataset to extract.
        dates (list): A list containing the start and end dates in 'YYYY-MM-DD' format.

    Returns:
        xarray.DataArray: The sea ice data for the specified variable and date range.
    """

    full_URL = '/'.join([server,id])
    start_date, end_date = dates[0], dates[1]

    da = xr.open_dataset(full_URL, chunks={"time":"auto"})
    da = da[varname]
    da.rio.set_spatial_dims(x_dim="xgrid", y_dim="ygrid", inplace=True)
    da.rio.write_crs(crs, inplace=True)
    da = da.clip(min=0, max=1).sel(time=slice(start_date, end_date))
    return da

def clip_data(dat, shape:gpd.GeoDataFrame):
    """
    Clips the given data using the shape geometry and returns the clipped data.

    Args:
        dat (xarray.DataArray or xarray.Dataset): The data to be clipped.
        shape (gpd.GeoDataFrame): The GeoDataFrame containing the shape geometry with CRS.

    Returns:
        xarray.DataArray or xarray.Dataset: The clipped data.
    """
    clipped_da = dat.rio.clip(shape.geometry.apply(mapping), shape.crs)
    return clipped_da

def get_area(name):
    """
    Loads the area dataset for a given region and returns the cell area data.

    Args:
        name (str): The name of the region.

    Returns:
        xarray.DataArray: The cell area data for the specified region.

    Raises:
        Exception: If the regional area dataset cannot be opened.
    """
    try:
        ds = xr.open_dataset(f'data/area_{name}.nc')
        return ds.cell_area
    except: 
        raise("Cannot open regional area dataset")
 

def compute_extent_km(ds, area_ds):
    """
    Computes sea ice extent and using daily data from the given date range.

    Args:
        ds (xarray.DataArray): The sea ice concentration data.
        area_ds (xarray.DataArray): The area of each grid cell.

    Raises:
        TypeError: If the computed extent variable is not an xarray.DataArray.
        Exception: If the extent computation fails for any reason.

    Returns:
        xarray.DataArray: The sea ice extent in square kilometers.
    """


    try:

        # Create Sea Ice Extent Values 0 and 1 based on threshold, retaining Nan values
        ice_conc_ext_yearly = xr.where(ds >= 0.15, 1, 0)
        ice_conc_ext_yearly = xr.where(ds.isnull(), np.nan, ice_conc_ext_yearly)
        
        # Calculate sea ice extent of each cell by multiplying binary value to grid cell area
        ice_ext_yearly = ice_conc_ext_yearly * area_ds
        print(ice_ext_yearly[0])
        # Add name
        if isinstance(ice_ext_yearly, xr.DataArray):
            ice_ext_yearly.name = 'seaice_extent'
        else:
            raise TypeError(f"extent values should be an xarray.DataArray {type(ice_ext_yearly)}")


        ice_ext_yearly_ts = (ice_ext_yearly
                            .groupby("time")
                            .sum(dim=["xgrid", "ygrid"])) 
        
        # Add year-month 
        # ice_ext_yearly['time_ymd'] = ice_ext_yearly['time'].dt.strftime('%Y-%m-%d')
        return ice_ext_yearly_ts/1000000
            
    
    except Exception as e:
        print(f"Unable to compute extent : {e}")
        raise
                

