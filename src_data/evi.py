import numpy as np
import geopandas as gp
import ee
import pickle
import os
import sys
from shapely import MultiPolygon, Polygon
import datetime

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..")

isl_path = os.path.join(project_folder, "data/filtered/final", "islands_4.gpkg")
gdf = gp.read_file(isl_path)

config_path = os.path.join(current_folder, "config.py")
sys.path.append(os.path.dirname(config_path))
import config
proj = config.proj
ee.Initialize(project = proj)

dataset = ee.ImageCollection("MODIS/061/MOD13A3")
# Most recent image
sorted_collection = dataset.sort('system:time_start', False)
last_image = sorted_collection.first()
timestamp_ms = last_image.get('system:time_start').getInfo()
last_date = datetime.datetime.fromtimestamp(timestamp_ms/1000.0)
print(f"Last image date: {last_date}")
# Two years window
dataset = dataset.filterDate("2022-01-01", "2024-12-31")

def mean_evi(image):
    stats = image.reduceRegion(
        reducer = ee.Reducer.mean(),
        geometry = multip_geo,
        bestEffort = True
    )
    return image.set("mean_evi", stats.get("EVI"), "date", image.date().format())

# Data load if existing, else initialize dictionaries
output_folder = os.path.join(project_folder, "data/final_data")
os.makedirs(output_folder, exist_ok = True)
output_path = os.path.join(output_folder, "evi.pkl")
if os.path.exists(output_path):
    with open(output_path, 'rb') as file:
        evi = pickle.load(file)
    output_path = os.path.join(output_folder, "evi_nodata.pkl")
    with open(output_path ,  'rb') as file:
        evi_nodata = pickle.load(file)
else:
    evi = {}
    evi_nodata = {}

# Iterate for islands
print(f'Total islands: {len(gdf)}')
for k, (i, isl) in enumerate(gdf.iterrows(), 1):
    if k%100 == 0 or k == len(gdf):
        print(f'{k} islands made')
    if k % 10 == 0:
        # Periodic exportation
        output_path = os.path.join(output_folder, "evi.pkl")
        with open(output_path, "wb") as f:
            pickle.dump(evi, f)
        output_path = os.path.join(output_folder, "evi_nodata.pkl")
        with open(output_path, "wb") as f:
            pickle.dump(evi_nodata, f)
    ID = isl.ALL_Uniq
    if ID not in evi:
        # Simplify big islands geometry, exceed max payload
        if isl.IslandArea > 15000:
            simpli = isl.geometry.simplify(tolerance=0.005, preserve_topology=True)
            if isinstance(simpli, MultiPolygon):
                multi = simpli
            if isinstance(simpli, Polygon):
                multi = MultiPolygon([simpli])
        else:
            multipoli = isl.geometry
        multip_list = [
            [list(vert) for vert in poly.exterior.coords]
            for poly in multipoli.geoms
        ]
        multip_geo = ee.Geometry.MultiPolygon(multip_list)
        # Intersecting images
        collection=dataset.filterBounds(multip_geo)
        evi_means = dataset.map(mean_evi)
        evi_list = evi_means.aggregate_array("mean_evi").getInfo()
        # No data
        if evi_list==[]:
            evi[ID]=np.nan
            evi_nodata[ID]=1
        else:
            # Mean of monthly means
            evi[ID]=np.mean(evi_list)
            evi_nodata[ID]=0

# Expo
output_path=os.path.join(output_folder, "evi.pkl")
with open(output_path, "wb") as f:
    pickle.dump(evi, f)
output_path=os.path.join(output_folder, "evi_nodata.pkl")
with open(output_path, "wb") as f:
    pickle.dump(evi_nodata, f)