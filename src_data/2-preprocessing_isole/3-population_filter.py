import geopandas as gp
import os
import sys
import rasterio
import rasterio.mask
from shapely.geometry import mapping
import numpy as np

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..")

file_path = os.path.join(project_folder, "data/filtered/area/islands.gpkg")
gdf = gp.read_file(file_path)
print(f'initial file length: {len(gdf)}')

# Population file
path_pop = os.path.join(project_folder, "files", "population.tif")
src = rasterio.open(path_pop)

# New columns
gdf['pop'] = 0
gdf['pop_density'] = 0

# Iterate for islands
print(f'{len(gdf)} total islands')
for k,(i,isl) in enumerate(gdf.iterrows(), 0):
    if k%1000 == 0 or k == len(gdf)-1:
        print(f'{k} islands made')
    multi = isl.geometry
    # Valid pixels sum
    out_image, out_transform = rasterio.mask.mask(src, [mapping(multi)], crop = True, all_touched = True)
    no_data_value = src.nodata
    valid_pixels = out_image[out_image != no_data_value]
    island_pop = np.sum(valid_pixels)
    # gdf update
    gdf.loc[i,'pop'] = island_pop
    gdf.loc[i,'pop_density'] = island_pop/gdf.loc[i,'IslandArea']

config_path = os.path.join(current_folder, "..", "config.py")
sys.path.append(os.path.dirname(config_path))
import config
min_pop = config.MIN_POPULATION
max_pop = config.MAX_POPULATION

# Filter
gdf_populated = gdf[(gdf['pop'] > max_pop)]
print(f'Islands too populated: {len(gdf_populated)}')
gdf = gdf[(gdf['pop'] >= min_pop) & (gdf['pop'] <= max_pop)]
print(f'Islands remainind: {len(gdf)}')

# Expo
output_folder = os.path.join(project_folder, "data/filtered/population")
os.makedirs(output_folder, exist_ok = True)
out_path = os.path.join(output_folder, "islands.gpkg")
gdf.to_file(out_path, driver = "GPKG")

out_path = os.path.join(project_folder, "data/excluded/populated_islands.gpkg")
gdf_populated.to_file(out_path, driver = "GPKG")

IDs = list(gdf.ALL_Uniq)
populations = list(gdf.Popolazione)
pop_densities = list(gdf.Densità_pop)

# Apply filter to rounded dataframes
out_path = os.path.join(project_folder, "data/filtered/area", "islands_4.gpkg")
gdf = gp.read_file(out_path)
for i,isl in gdf.iterrows():
    if isl.ALL_Uniq not in IDs : 
        gdf = gdf.drop(i)
# Features addition
gdf['pop'] = populations
gdf['pop_density'] = pop_densities
out_path = os.path.join(output_folder, "islands_4.gpkg")
gdf.to_file(out_path, driver = "GPKG")

out_path = os.path.join(project_folder, "data/filtered/area", "islands_3.gpkg")
gdf = gp.read_file(out_path)
for i,isl in gdf.iterrows():
    if isl.ALL_Uniq not in IDs : 
        gdf = gdf.drop(i)
gdf['pop'] = populations
gdf['pop_density'] = pop_densities
output_path = os.path.join(output_folder, "islands_3.gpkg")
gdf.to_file(output_path, driver = "GPKG")

out_path = os.path.join(project_folder, "data/filtered/area", "islands_2.gpkg")
gdf = gp.read_file(out_path)
for i,isl in gdf.iterrows():
    if isl.ALL_Uniq not in IDs : 
        gdf = gdf.drop(i)
gdf['pop'] = populations
gdf['pop_density'] = pop_densities
out_path = os.path.join(output_folder, "islands_2.gpkg")
gdf.to_file(out_path, driver = "GPKG")