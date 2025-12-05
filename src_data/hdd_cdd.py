import numpy as np
import geopandas as gp
import ee
import os
import sys
import pickle
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
ee.Initialize(project = proj)

dataset = ee.ImageCollection("ECMWF/ERA5/DAILY")
# Most recent date
sorted_collection = dataset.sort('system:time_start', False)
last_image = sorted_collection.first()
timestamp_ms = last_image.get('system:time_start').getInfo()
last_date = datetime.datetime.fromtimestamp(timestamp_ms/1000.0)
print(f"Last image date: {last_date}")
dataset = dataset.filterDate("2016-06-01", "2020-05-31")

def mean_temp(image):
    stats = image.reduceRegion(
        reducer = ee.Reducer.mean(),  # Mean temperature
        geometry = multip_geo,
        bestEffort = True
    )
    return image.set("mean_temp", stats.get("mean_2m_air_temperature"), "date", image.date().format())

# Load data if already exisisting, else initialize dictionaries
output_folder = os.path.join(project_folder, "data/final_data")
os.makedirs(output_folder, exist_ok = True)
output_path = os.path.join(output_folder, "hdd.pkl")
if os.path.exists(output_path):
    with open(output_path, 'rb') as file:
        hdd = pickle.load(file)
    output_path = os.path.join(output_folder, "hdd_nodata.pkl")
    with open(output_path ,  'rb') as file:
        hdd_nodata = pickle.load(file)
    output_path = os.path.join(output_folder, "cdd.pkl")
    with open(output_path ,  'rb') as file:
        cdd = pickle.load(file)
    output_path = os.path.join(output_folder, "cdd_nodata.pkl")
    with open(output_path ,  'rb') as file:
        cdd_nodata = pickle.load(file)
else:
     hdd = {}
     hdd_nodata = {}
     cdd = {}
     cdd_nodata = {}

# Iterate for islands
print(f'Total islands: {len(gdf)}')
for k, (i, isl) in enumerate(gdf.iterrows(), 1):
    if k % 100 == 0 or k == len(gdf):
        print(f'{k} islands made')
    if k % 10 == 0:
        # Periodic exportation
        output_path = os.path.join(output_folder, "hdd.pkl")
        with open(output_path, "wb") as f:
            pickle.dump(hdd, f)
        output_path = os.path.join(output_folder, "hdd_nodata.pkl")
        with open(output_path, "wb") as f:
            pickle.dump(hdd_nodata, f)
        output_path = os.path.join(output_folder, "cdd.pkl")
        with open(output_path, "wb") as f:
            pickle.dump(cdd, f)
        output_path = os.path.join(output_folder, "cdd_nodata.pkl")
        with open(output_path, "wb") as f:
            pickle.dump(cdd_nodata, f)
    ID = isl.ALL_Uniq
    if ID not in hdd:
        # Simplify big geometries
        if isl.IslandArea > 10000:
            simpli = isl.geometry.simplify(tolerance = 0.005, preserve_topology = True)
        elif isl.IslandArea > 5000:
            simpli = isl.geometry.simplify(tolerance = 0.003, preserve_topology = True)
        elif isl.IslandArea > 2000:
            simpli = isl.geometry.simplify(tolerance = 0.002, preserve_topology = True)
        else:
            simpli = isl.geometry.simplify(tolerance = 0.001, preserve_topology = True)
        if isinstance(simpli, MultiPolygon):
            multi = simpli
        if isinstance(simpli, Polygon):
            multi = MultiPolygon([simpli])
        multip_list = [
            [list(vert) for vert in poly.exterior.coords]
            for poly in multi.geoms
        ]
        multip_geo = ee.Geometry.MultiPolygon(multip_list)
        collection=dataset.filterBounds(multip_geo)
        temp_means = collection.map(mean_temp)
        # Daily mean temperatures list
        mean_list = temp_means.aggregate_array("mean_temp").getInfo()
        # No data
        if mean_list == []:
            hdd[ID] = np.nan
            hdd_nodata[ID] = 1
            cdd[ID] = np.nan
            cdd_nodata[ID] = 1
        else:
            # HDD and CDD counters
            k1 = 0
            k2 = 0
            for i in range(len(mean_list)):
                #288,291,294,297 HDD and CDD thresholds in kelvin
                if mean_list[i] < 288:
                    k1 += 291 - mean_list[i]
                if mean_list[i] > 297:
                    k2 += mean_list[i] - 294
            # Annual values, 4 year window
            hdd[ID] = k1/4
            hdd_nodata[ID] = 0
            cdd[ID] = k2/4
            cdd_nodata[ID] = 0

# Expo
output_path = os.path.join(output_folder, "hdd.pkl")
with open(output_path, "wb") as f:
    pickle.dump(hdd, f)
output_path = os.path.join(output_folder, "hdd_nodata.pkl")
with open(output_path, "wb") as f:
    pickle.dump(hdd_nodata, f)
output_path = os.path.join(output_folder, "cdd.pkl")
with open(output_path, "wb") as f:
    pickle.dump(cdd, f)
output_path = os.path.join(output_folder, "cdd_nodata.pkl")
with open(output_path, "wb") as f:
    pickle.dump(cdd_nodata, f)