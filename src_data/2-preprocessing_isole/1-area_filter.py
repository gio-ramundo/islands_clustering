import geopandas as gp
import os
import sys

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..")

# Setup
file_path = os.path.join(project_folder, "files", "isl_4326.gpkg")
gdf = gp.read_file(file_path)
print(f'Length file: {len(gdf)}')

config_path = os.path.join(current_folder, "..", "config.py")
sys.path.append(os.path.dirname(config_path))
import config
min_surface = config.MIN_AREA
max_surface = config.MAX_AREA

# Area filter, not relevenat columns drop
gdf_big_islands = gdf[(gdf['IslandArea']>max_surface)]
print(f'Big islands excluded: {len(gdf_big_islands)}')
gdf = gdf[(gdf['IslandArea'] >= min_surface) & (gdf['IslandArea'] <= max_surface)]
print(f'Remaining islands: {len(gdf)}')
gdf = gdf[['ALL_Uniq', 'Name_USGSO', 'Shape_Leng', 'IslandArea', 'geometry']]
gdf_big_islands = gdf_big_islands[['ALL_Uniq', 'Name_USGSO', 'Shape_Leng', 'IslandArea', 'geometry']]

# Exportation
percorso_folder_out = os.path.join(project_folder, "data/filtered/area")
os.makedirs(percorso_folder_out, exist_ok = True)
percorso_out = os.path.join(percorso_folder_out, "islands.gpkg")
gdf.to_file(percorso_out, driver = "GPKG")

percorso_folder_out = os.path.join(project_folder, "data/excluded")
os.makedirs(percorso_folder_out, exist_ok = True)
percorso_out = os.path.join(percorso_folder_out, "big_islands.gpkg")
gdf_big_islands.to_file(percorso_out, driver = "GPKG")