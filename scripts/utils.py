# utils.py

import xarray as xr
import geopandas as gpd
import rasterio
import pandas as pd
import rioxarray
from shapely.geometry import mapping
import numpy as np

class pwData:

    def __init__(self, id, varname, crs, server="https://polarwatch.noaa.gov/erddap/griddap", shape=None):      
        """_summary_

        Args:
            id (str): polarwatch erddap id
            varname (str): variable name 
            crs (str): epsg or proj4text
            server (str, optional)
            shape (geopandas, optional): shape geometries transformed into projection of data. Defaults to None.
        """

        self.crs = crs
        self.varname = varname
        self.shape = shape
        self.server = server
        if shape is not None:
            ds = self._load_data(id)
            self.ds = self._clip_data(ds, shape)
        else:       
            self.ds = self._load_data(id)


    def _load_data(self, id):
        """loads ERDDAP sea ice data from polarwatch and returns data of the data range with geo_specs

        Args:
            id (str): erddap id

        Returns:
            xarray.Dataset: seaice data

        """

        full_URL = '/'.join([self.server,id])

        da = xr.open_dataset(full_URL, chunks={"time":"auto"})
        da = da[self.varname]
        da.rio.set_spatial_dims(x_dim="xgrid", y_dim="ygrid", inplace=True)
        da.rio.write_crs(self.crs, inplace=True)
        da = da.clip(min=0, max=1)
        return da


    def _clip_data(self, dat, shape:gpd.GeoDataFrame):
        """clips data using the shape geometry and returned clipped data

        Args:
            shape (gpd.GeoDataFrame): crs transformed shape geometry in GeoDataFrame 
        """
        clipped_da = dat.rio.clip(shape.geometry.apply(mapping), shape.crs)
        return clipped_da
     

class SIC25k(pwData):

    def __init__(self, id, varname, crs, 
                 server="https://polarwatch.noaa.gov/erddap/griddap", 
                 shape=None):      
        super().__init__(id, varname, crs, server, shape)

        if shape is not None:
            ds = self._load_data(id)
            self.ds = self._clip_data(ds, shape)
        else:       
            self.ds = self._load_data(id, varname)

    def get_total_area_km(self, area_id):
        if area_id is None:
            raise ValueError("erddap id for the grid cell area data must be provided")

        try:
            area = self._load_area(area_id)
            ds = self.ds.isel(time=0)
            
            ds1 = xr.where(ds.isnull(), np.nan, 1)
            ice_ext = ds1 * area
            ice_ext.name = 'extent'
            ice_area = ice_ext.sum(dim=["xgrid", "ygrid"], skipna = True).values 
        
            return ice_area /1000000           
            
        except Exception as e:
            print(f'Failed to load grid area and compute total area {e}')


    def compute_extent_km(self, area_id, dates):
        """computes sea ice extent and standard deviations using daily data from
        given date range

        Args:
            area_id (str): erddap id for associated area
            dates (list): start and end date

        Raises:
            TypeError: raise error if computed extent variable is not xr.DataArray
            Exception: raise error when fails to compute extent

        Returns:
            float: sea ice extent in square km
        """


        try:
            ds = self.ds.sel(time=slice(dates[0], dates[1]))
            area = self._load_area(area_id)
            # Create Sea Ice Extent Values 0 and 1 based on threshold, retaining Nan values
            ice_conc_ext_yearly = xr.where(ds >= 0.15, 1, 0)
            ice_conc_ext_yearly = xr.where(ds.isnull(), np.nan, ice_conc_ext_yearly)
            # Calculate sea ice extent of each cell by multiplying binary value to grid cell area
            ice_ext_yearly = ice_conc_ext_yearly * area

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
                
    def _load_area(self, id):
        """loads grid cell area from polarwatch erddap
        Args:
            area_id (str): erddap id for associated area

        Returns:
            xr.Dataset: returns gridcell area optionally clipped
        """
        try:

            full_URL = '/'.join([self.server,id])

            da = xr.open_dataset(full_URL, chunks={"time":"auto"})
            da = da['cell_area']
            da.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)
            da = da.rename({'x': 'xgrid', 'y': 'ygrid'})
            da.rio.write_crs(self.crs, inplace=True)

            if self.shape is not None:
                clipped_area = self._clip_data(da, self.shape)
                return clipped_area
            else:
                return da
        except Exception as e:
            print(f"Error processing area data: {e}")
            raise 





