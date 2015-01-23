Global Temperature Time Series. Global monthly mean and annual mean temperature anomalies in degrees Celsius from 1880 to the present. Data is included from the [GISS Surface Temperature (GISTEMP) analysis][gistemp] and the [global component of Climate at a Glance (GCAG)][gcag].

## Data
1. GISS Surface Temperature Analysis (GISTEMP):

  Base period: 1951-1980

  Sources: [GHCN-M][ghcn-m], [ERSST][ersst]

  Citation: *GISTEMP: NASA Goddard Institute for Space Studies (GISS) Surface Temperature Analysis.*

1. Global component of Climate at a Glance (GCAG):

  Base period: 20th century

  Sources: [GHCN-M][ghcn-m], [ICOADS][icoads]

  Citation: *NOAA National Climatic Data Center (NCDC), Global component of Climate at a Glance (GCAG).*

*Additional Data*

The [HadCRUT4 time series: ensemble medians and uncertainties][hadcrut4] is not included in the published Data Package at this time because of it's restrictive [terms and conditions][hadcrut4-terms]. However, processing the dataset is supported by the script.

[gistemp]: http://data.giss.nasa.gov/gistemp/
[gcag]: http://www.ncdc.noaa.gov/cag/data-info/global
[hadcrut4]: http://www.metoffice.gov.uk/hadobs/hadcrut4/data/current/download.html#regional_series
[hadcrut4-terms]: http://www.metoffice.gov.uk/hadobs/hadcrut4/terms_and_conditions.html
[ghcn-m]: http://www.ncdc.noaa.gov/ghcnm/v3.php
[ersst]: http://www.ncdc.noaa.gov/data-access/marineocean-data/extended-reconstructed-sea-surface-temperature-ersst-v3b
[icoads]: http://icoads.noaa.gov/

## Preparation

The data are prepared with a Python script.

The HadCRUT4 processing script, which is not run by default, requires the external `lxml` module.

In the GISTEMP dataset, hundredths of degrees Celsius are converted to degrees Celsius.

Run the following script to download the data and write them to annual and monthly CSV files:

`python scripts/process.py`

The raw data are output to `./tmp`. The processed data are output to `./data`.

## License

This Data Package is made available under the Public Domain Dedication and License v1.0 whose full text can be found at: http://www.opendatacommons.org/licenses/pddl/1.0/
