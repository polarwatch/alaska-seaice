## DataProc/
This folder contains scripts that compute sea ice extent and generate summary data in CSV format. These CSV files are used to create Plotly time series charts, which illustrate sea ice extent trends on the Alaska Sea Ice page.

## Scripts
`pw_data.py`: Contains modules for data loading, processing, computing sea ice extent.

`annualized_timeseries.py`:    Main function to load sea ice data, compute annual sea ice extent for specific regions,
    and export the results to CSV files. The annual sea ice extent is calculated for the period starting on September 1 and ending on August 31 of the following year from 1985 to the most recent year'

