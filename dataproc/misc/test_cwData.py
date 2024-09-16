import pytest
import xarray as xr
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import box
from pw_data import SIC25k

@pytest.fixture
def mock_sic25k():
    """fixture for initializing SIC25k instance with mocked data.
    """

    id = 'nsidcG10016v2nhmday'
    varname = 'cdr_seaice_conc_monthly'
    crs = 'epsg:3413'
    server = "https://polarwatch.noaa.gov/erddap/griddap"

    data = np.random.rand(10, 5, 5) # shape 3 rand
    times = pd.date_range("2005-01-01", periods = 10)
    xgrid = np.linspace(0, 4, 5)
    ygrid = np.linspace(0, 4, 5)

    ds = xr.Dataset(
        {varname: (["time", "xgrid", "ygrid"], data),
         },
         coords = {
             "time": (["time"], times),
             "xgrid": (["xgrid"], xgrid),
             "ygrid": (["ygrid"], ygrid),
         }
    )

    mock_sic = SIC25k(id, varname, crs, server)
    mock_sic.ds = ds
    ds.rio.write_crs(crs, inplace=True)

    area_data = np.ones((5, 5)) * 625
    area_ds = xr.Dataset(
        {
        "cell_area" : (["x", "y"], area_data)
    },
    coords = {
        "x": (["x"], xgrid),
        "y": (["y"], ygrid),
    }

    )

    ds = ds.rio.set_spatial_dims(x_dim='xgrid', y_dim='ygrid', inplace=False)
    area_ds = area_ds.rio.set_spatial_dims(x_dim='x', y_dim='y', inplace=False)
    
    mock_sic.area = area_ds
    return mock_sic

@pytest.fixture
def mock_shape():
    shape = gpd.read_file(f'resources/akmarineeco/arctic_sf.shp')
    return shape


def test_load_data(mock_sic25k):
    # check return value 
    assert isinstance(mock_sic25k.ds, xr.Dataset)

    # check dim values
    assert mock_sic25k.ds['cdr_seaice_conc_monthly'].dims == ('time', 'xgrid', 'ygrid')

def test_clip_data(mock_sic25k, mock_shape):
    """Test the data clipping 
    Args:
        mock_sic25k (_type_): _description_
        mock_shape (_type_): _description_
    """
  #  clipped = mock_sic25k.clip_data(mock_sic25k.ds['cdr_seaice_conc_monthly'], mock_shape)
 