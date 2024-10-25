<a className="gh-badge" href="https://datahub.io/core/global-temp"><img src="https://badgen.net/badge/icon/View%20on%20datahub.io/orange?icon=https://datahub.io/datahub-cube-badge-icon.svg&label&scale=1.25" alt="badge" /></a>

Global Temperature Time Series. Data are included from the GISS Surface Temperature (GISTEMP) analysis and the global component of Climate at a Glance (GCAG). Two datasets are provided: 1) global monthly mean and 2) annual mean temperature anomalies in degrees Celsius from 1880 to the present as for the GCAG data is available from 1850 to the present.

## Data

### Description

1. [GISTEMP Global Land-Ocean Temperature Index][gistemp]:

  > Combined Land-Surface Air and Sea-Surface Water Temperature Anomalies [i.e. deviations from the corresponding 1951-1980 means]. Global-mean monthly [...] and annual means, 1880-present, updated through most recent month.

1. [Global component of Climate at a Glance (GCAG)][gcag]:

  > Global temperature anomaly data come from the Global Historical Climatology Network-Monthly (GHCN-M) data set and International Comprehensive Ocean-Atmosphere Data Set (ICOADS), which have data from 1880 to the present. These two datasets are blended into a single product to produce the combined global land and ocean temperature anomalies. The available timeseries of global-scale temperature anomalies are calculated with respect to the 20th century average [...].

### Citations

1. *GISTEMP: NASA Goddard Institute for Space Studies (GISS) Surface Temperature Analysis, Global Land-Ocean Temperature Index.*
1. *NOAA National Climatic Data Center (NCDC), global component of Climate at a Glance (GCAG).*

### Sources

1. 
  * Name: GISTEMP Global Land-Ocean Temperature Index
  * Web: https://data.giss.nasa.gov/gistemp/
1. 
  * Name: Global component of Climate at a Glance (GCAG)
  * Web: https://www.metoffice.gov.uk/hadobs/hadcrut5/data/HadCRUT.5.0.2.0/download.html

### Additional Data

* Upstream datasets:
  * [GHCN-M][ghcn-m]
  * [ERSST][ersst]
  * [ICOADS][icoads]
* Other:
  * [HadCRUT5][hadcrut5]

## Preparation

### Requirements

Python 3 is required for data preparation.

### Processing

#### Locally
Run the following script from this directory to download and process the data:

```bash
make data
```

#### Automated Workflow
Current script is automated using Github Workflows


Hundredths of degrees Celsius in the GISTEMP Global Land-Ocean Temperature Index data are converted to degrees Celsius.

A HadCRUT4 processing script is available but not run by default.

### Resources

The processed data are output to `./data`.

## License

### ODC-PDDL-1.0

This Data Package and these datasets are made available under the Public Domain Dedication and License v1.0 whose full text can be found at: http://www.opendatacommons.org/licenses/pddl/1.0/

## References

1. Morice, C. P., Kennedy, J. J., Rayner, N. A., Winn, J. P., Hogan, E., Killick, R. E., et al. (2021). An updated assessment of near-surface temperature change from 1850: the HadCRUT5 data set. *Journal of Geophysical Research: Atmospheres*, 126, e2019JD032361. [https://doi.org/10.1029/2019JD032361](https://doi.org/10.1029/2019JD032361)

2. GISTEMP Team. (2024). GISS Surface Temperature Analysis (GISTEMP), version 4. NASA Goddard Institute for Space Studies. Dataset accessed 20YY-MM-DD at [https://data.giss.nasa.gov/gistemp/](https://data.giss.nasa.gov/gistemp/).

3. Lenssen, N., Schmidt, G. A., Hendrickson, M., Jacobs, P., Menne, M., & Ruedy, R. (2024). A GISTEMPv4 observational uncertainty ensemble. *Journal of Geophysical Research: Atmospheres*, 129(17), e2023JD040179. [https://doi.org/10.1029/2023JD040179](https://doi.org/10.1029/2023JD040179).

### Notes

The upstream datasets do not impose any specific restrictions on using these data in a public or commercial product:

* [GHCN-N](http://www.esrl.noaa.gov/psd/data/gridded/data.ghcncams.html)
* [ERSST](http://www.esrl.noaa.gov/psd/data/gridded/data.noaa.ersst.html)
* [ICOADS](http://icoads.noaa.gov/data.icoads.html)

[gistemp]: http://data.giss.nasa.gov/gistemp/
[gcag]: https://www.ncei.noaa.gov/node/6696
[hadcrut5]: https://www.metoffice.gov.uk/hadobs/hadcrut5/index.html
[ghcn-m]: http://www.ncdc.noaa.gov/ghcnm/v3.php
[ersst]: http://www.ncdc.noaa.gov/data-access/marineocean-data/extended-reconstructed-sea-surface-temperature-ersst-v3b
[icoads]: http://icoads.noaa.gov/