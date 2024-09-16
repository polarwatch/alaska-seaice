# pw_data.py
import pandas as pd
import rioxarray
from shapely.geometry import mapping
import numpy as np
import xarray as xr
import geopandas as gpd
import rasterio

import dask 
from typing import Tuple


class cwData:
    def __init__(self, id, varname, crs, server, grids = None, shape=None):      
        """
        Initializes the cwData object, loads sea ice data, and optionally clips it to a shape.

        Args:
            id (str): PolarWatch ERDDAP dataset ID.
            varname (str): Variable name to load from the dataset (e.g., 'cdr_seaice_conc').
            crs (str): Coordinate reference system (EPSG code or Proj4 string).
            server (str): The base URL of the ERDDAP server.
            grids (dict, optional): A dictionary with 'x' and 'y' key names for grid dimensions (e.g., xgrid, ygrid for sic data).
            shape (geopandas.GeoDataFrame, optional): Shape geometries projected to the data's CRS. Defaults to None.
        """
        
        # Store the provided arguments as instance variables.
        self.crs = crs
        self.varname = varname
        self.shape = shape
        self.server = server
        self.grids = grids
        self.id = id
        try: 
            if shape is not None:
                ds = self.load_data()
                self.ds = clip_data(ds, shape)
            else:       
                self.ds = self.load_data()
        except Exception as e:
            print(f'Unable to load data: {e}')
            
    
    def __str__(self):
        """String representation of the cwData object, showing key metadata."""

        return (f"cwData:\nid={self.id}\n, varname={self.varname}\n, crs={self.crs}\n, "
                f"server={self.server}\n, grids={self.grids}\n, shape={self.shape}\n"
                f"metadata = {self.ds}")

    def load_data(self):
        """Loads sea ice data from the PolarWatch ERDDAP server.
        The dataset is loaded using the provided ERDDAP ID, variable name, 
        and grid details. The data is then clipped to a valid range of 0-1.

        Returns:
            xarray.Dataset: Loaded sea ice concentration data, spatially aware and ready for further operations.
        """

        full_URL = '/'.join([self.server,self.id])

        ds = xr.open_dataset(full_URL, chunks={"time":"auto"})
        ds = ds[self.varname]
        ds.rio.set_spatial_dims(x_dim=self.grids['x'], y_dim=self.grids['y'], inplace=True)
        ds.rio.write_crs(self.crs, inplace=True)
        ds = ds.clip(min=0, max=1)
        return ds
 
    def compute_clim(self, year_range: list, frequency: str)-> xr.Dataset:
        """Computes climatology (long-term mean) for a given time period and frequency.

        Args:
            year_range (list): Start and end years to define the time period for climatology.
            frequency (str): Frequency to group the data by ('15D', 'W', 'D', 'M', 'Q').

        Raises:
            ValueError: If the provided year range is out of bounds or if the frequency is not valid.

        Returns:
            xarray.Dataset: Climatology data averaged over the specified frequency.
        """
        start_year = pd.Timestamp(self.ds['time'].min().values).year
        end_year = pd.Timestamp(self.ds['time'].max().values).year

        if year_range[0] < start_year or year_range[1] > end_year:
            raise ValueError("Year range provided must be within the dataset's date range.")
      
        ds_selected = self.ds.sel(time=slice(f"{year_range[0]}-01-01", f"{year_range[1]}-12-31"))

        if frequency == "15D":
            ds_clim = ds_selected.groupby(custom_15day_interval(ds_selected.time)).mean("time")
        elif frequency in ["W", "D", "M", "Q"]:
            ds_clim = ds_selected.resample(time=frequency).mean()
        else:
            raise ValueError("Frequency should be one of ['15D', 'W', 'D', 'M', 'Q']")
        return ds_clim

class SIC25k(cwData):
    """ Class that handles sea ice concentration (SIC) data at 25 km resolution, inherited from cwData class.

    Args:
        cwData (class): Base class for loading and processing ERDDAP data.
    """
    def __init__(self, id, varname, crs, 
                 server="https://polarwatch.noaa.gov/erddap/griddap", shape=None):      
        """
        Initializes the SIC25k object, loads data, and optionally clips it to a shape if provided.

        Args:
            id (str): PolarWatch ERDDAP dataset ID for sea ice concentration.
            varname (str): Variable name (e.g., 'cdr_seaice_conc').
            crs (str): Coordinate reference system (EPSG code or Proj4 string).
            server (str, optional): ERDDAP server URL. Defaults to PolarWatch ERDDAP server.
            shape (gpd.GeoDataFrame, optional): Shape geometries projected to the data's CRS. Defaults to None.
        """
        super().__init__(id, varname, crs, server)
        self.grids = {'x': 'xgrid', 'y':'ygrid'}
        self.area = None

        if shape is not None:
            ds = self.load_data()
            self.ds = clip_data(ds, shape)
        else:       
            self.ds = self.load_data()

    def has_area(self):
        if self.area is None: 
            return 0
        return 1

    def get_total_area_km(self):
        """ Computes the total area (in square kilometers) of the grid cells in the dataset.

        Raises:
            ValueError: If the grid cell area is not loaded.

        Returns:
            float: Total area in square kilometers.
        """
        if self.area is None:
            raise ValueError("Grid cell area is not loaded")
        try:    
            ds = self.ds.isel(time=0)
            
            ds1 = xr.where(ds.isnull(), np.nan, 1)
            ice_ext = ds1 * self.area
            ice_ext.name = 'extent'
            ice_area = ice_ext.sum(dim=["xgrid", "ygrid"], skipna = True).values 
        
            return ice_area / 1e6           
            
        except Exception as e:
            print(f'Failed to load grid area and compute total area {e}')


    def subset_dim(self, dates: list, shp: gpd.GeoDataFrame)-> Tuple[xr.Dataset, ...]:
        """Subsets the dataset by time range and optional shape geometry.

        Args:
            dates (list): List of two dates (start and end) in 'YYYY-MM-DD' format.
            shp (gpd.GeoDataFrame): Shape geometries for spatial subset.

        Returns:
            tuple: A tuple of (subset dataset, subset area).
        """
        ds = self.ds.sel(time=slice(dates[0], dates[1]))
        if shp is not None and not shp.empty:
            ds, area = clip_data(ds, shp), clip_data(self.area, shp)
            return (ds, area)
        else:
            return (ds, self.area)
        
    def format_sic(self, ds: xr.Dataset, threshold=0.15)-> xr.Dataset:
        """
        Transforms sea ice concentration data to binary (0 and 1) based on the threshold value.

        Args:
            ds (xr.Dataset): Sea ice concentration dataset.
            threshold (float): Threshold value for sea ice concentration (e.g., 0.15).

        Returns:
            xr.Dataset: Binary sea ice concentration dataset (0 for below threshold, 1 for above).
        """
        ds_binary = xr.where(ds >= threshold, 1, 0)
        ds_transformed = xr.where(ds_binary.isnull(), np.nan, ds_binary)           
        
        return ds_transformed

    def compute_extent_km(self, ds: xr.Dataset, area: xr.Dataset)->float:
        """ Computes sea ice extent in square kilometers.

        Args:
            ds (xr.Dataset): Binary sea ice concentration dataset.
            area (xr.Dataset): Grid cell area dataset.

        Returns:
            float: Sea ice extent in square kilometers.
        """

        if isinstance(ds, xr.Dataset):
            if len(ds.data_vars) == 1:
                ds = ds[list(ds.datavars)[0]]
            else:
                raise TypeError(f"Input `ds` is a multi-variable xarray. Provide a DataArray or single variable dataset")

        # Multiply sea ice concentration data by grid cell area to compute extent
        ice_cell = ds * area / 1e6 # Convert area to square m
        if isinstance(ice_cell, xr.DataArray):
            # Sum sea ice extent overxgrid and ygrid, group by time
            ice_cell.name = 'seaice_extent'  
            ice_ext = (ice_cell
                    .groupby("time")
                    .sum(dim=["xgrid", "ygrid"])) 
            return ice_ext
        
        else:
            raise TypeError(f"extent values should be in an xarray.DataArray {type(ice_cell)}")
  

    def load_area(self, id: str):
        """loads grid cell area from polarwatch erddap
        Args:
            area_id (str): erddap id for associated area

        Returns:
            None
        """
        try:

            full_URL = '/'.join([self.server,id])

            ds = xr.open_dataset(full_URL, chunks={"time":"auto"})
            da = ds['cell_area']
            da.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)
            da = da.rename({'x': 'xgrid', 'y': 'ygrid'})
            da.rio.write_crs(self.crs, inplace=True)

            if self.shape is None:
                self.area = da
            else: 
                clipped_area = clip_data(da, self.shape)
                self.area = clipped_area

        except Exception as e:
            print(f"Error loading grid area data: {e}")
            raise 

## Helper Functions

def clip_data(ds: xr.Dataset, shape:gpd.GeoDataFrame)-> xr.Dataset:
    """clips data using the shape geometry and returned clipped data

    Args:
        shape (gpd.GeoDataFrame): crs transformed shape geometry in GeoDataFrame 
    """
    
    # Check if CRS match, if not transform the shape geometry to match data CRS

    if shape.crs != ds.rio.crs:
        print("Shape CRS does not match data CRS. Performing CRS transformation")
        shape = shape.to_crs(ds.rio.crs)

    # Perform the clipping operation
    clipped_ds = ds.rio.clip(shape.geometry.apply(mapping), shape.crs)
    
    return clipped_ds


     



