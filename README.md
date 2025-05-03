20250418
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

