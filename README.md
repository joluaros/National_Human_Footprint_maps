20250418

Human Footprint (HF) maps score human pressures by their influence and integrate them into a single spatial index to assess ecosystem naturalness. We produced a historical series of national HF maps for Peru and Ecuador for Sustainable Development Goal 15 (SDG15) reporting, integrating pressures from built environments, land cover (agriculture, pasture, tree plantations), roads and railways, population density, electrical infrastructure, oil and gas, and mining. The dataset includes HF maps and pressure rasters for Peru (2012–2021) and Ecuador (2014, 2016, 2018, 2020, 2022). These maps reveal spatiotemporal patterns of human influence at national and subnational levels and support biodiversity monitoring, modelling, and conservation in these highly biodiverse countries.


Conda Environment Setup
conda config --add channels conda-forge  
conda create --name hh_py39 python=3.9 gdal matplotlib seaborn pandas geopandas scikit-image rasterio xarray rioxarray rasterstats spyder  

To generate the HF maps:
1.	In HF_main.py, uncomment the country to be processed and comment out the other one (lines 59/60).
2.	Uncomment the HF version to be processed and comment out the other ones (lines 43-45). Recommended: only leave SDG 15 uncommented.
3.	Ensure the required inputs are available.
4.	Run HF_main.py, which will call all necessary scripts.

Contact information:
Jose Aragon-Osejo
aragon@unbc.ca  | jose.luis.aragon.ec@gmail.com 