import geopandas as gp
import ee
import pickle
import os
import sys
from shapely import MultiPolygon, Polygon
import datetime

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..")

isl_path = os.path.join(project_folder, "data/filtered/final", "islands_3.gpkg")
gdf = gp.read_file(isl_path)

config_path = os.path.join(current_folder, "config.py")
sys.path.append(os.path.dirname(config_path))
import config
proj = config.proj
ee.Initialize(project=proj)

urban_collection = ee.ImageCollection("JRC/GHSL/P2023A/GHS_SMOD_V2-0")
# Most recent image
sorted_collection = urban_collection.sort('system:time_start', False)
last_image = sorted_collection.first()
timestamp_ms = last_image.get('system:time_start').getInfo()
last_date = datetime.datetime.fromtimestamp(timestamp_ms/1000.0)
print(f"Last image date: {last_date}")
# Least recent image
sorted_collection = urban_collection.sort('system:time_start', True)
first_image = sorted_collection.first()
timestamp_ms = first_image.get('system:time_start').getInfo()
first_date = datetime.datetime.fromtimestamp(timestamp_ms/1000.0)
print(f"First image date: {first_date}")

filtered_collection = urban_collection.filterDate('2000-01-01', '2025-01-01')
sorted_collection = filtered_collection.sort('system:time_start', False)
urban_image = ee.Image(sorted_collection.first())
# Urban pixels values
urban_values = [30, 23, 22]

# Load data if exisisting, else initialize dictionaries
output_folder = os.path.join(project_folder, "data/final_data")
os.makedirs(output_folder, exist_ok = True)
output_path = os.path.join(output_folder, "urban_area.pkl")
if os.path.exists(output_path):
    with open(output_path, 'rb') as file:
        urban = pickle.load(file)
    output_path = os.path.join(output_folder, "urban_area_rel.pkl")
    with open(output_path ,  'rb') as file:
            urban_rel = pickle.load(file)
else:
    urban = {}
    urban_rel = {}

gdf = gdf.sort_values(by = 'IslandArea', ascending=False)
print(f'Total islands: {len(gdf)}')
# Iterate for islands
for k, (i, isl) in enumerate(gdf.iterrows(), 1):
    if k%100 == 0:
        print(f'{k} islands made')
        print(isl.IslandArea)
    # Periodic exportation
    if k % 10 == 0:
        output_path = os.path.join(output_folder, "urban_area.pkl")
        with open(output_path, "wb") as f:
            pickle.dump(urban, f)
        output_path = os.path.join(output_folder, "urban_area_rel.pkl")
        with open(output_path, "wb") as f:
            pickle.dump(urban_rel, f)
    ID = isl.ALL_Uniq
    if ID not in urban:
        # Geomtry simplification
        if isl.IslandArea > 30000 or isl.ALL_Uniq == 273837:
            simpli=isl.geometry.simplify(tolerance = 0.005, preserve_topology = True)
            if isinstance(simpli, MultiPolygon):
                multi = simpli
            if isinstance(simpli, Polygon):
                multi = MultiPolygon([simpli])
        else:
            multi = isl.geometry
        multip_list = [ 
                [list(vert) for vert in poly.exterior.coords]
                for poly in multi.geoms
            ]   
        ee_geometry = ee.Geometry.MultiPolygon(multip_list)
        area0=ee_geometry.area().getInfo()    
        # Create urban mask and extract geometry
        clipped_image = urban_image.clip(ee_geometry)
        urban_mask = clipped_image.eq(urban_values[0])
        urban_mask = urban_mask.Or(clipped_image.eq(urban_values[1]))
        urban_mask = urban_mask.Or(clipped_image.eq(urban_values[2]))
        vectors = urban_mask.selfMask().reduceToVectors(
            geometry = urban_mask.geometry(),
            scale = clipped_image.projection().nominalScale().getInfo(),
            eightConnected = True,
            bestEffort = True
        )
        urban_geometry = vectors.union(ee.ErrorMargin(1)).geometry()
        urban_geometry = urban_geometry.intersection(ee_geometry)
        urban_area = urban_geometry.area().getInfo()
        # km2 conversion
        urban_area = (urban_area/1000000)
        # % value
        urban_relative = (urban_area/area0)*100
        
        urban[ID] = urban_area
        urban_rel[ID] = urban_relative

# Expo
output_path = os.path.join(output_folder, "urban_area.pkl")
with open(output_path, "wb") as f:
    pickle.dump(urban, f)
output_path = os.path.join(output_folder, "urban_area_rel.pkl")
with open(output_path, "wb") as f:
    pickle.dump(urban_rel, f)