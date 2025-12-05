import numpy as np
import geopandas as gp
import ee
import pickle
import os
import sys
import datetime

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..")

isl_path = os.path.join(project_folder, "data/filtered/final", "islnds_3.gpkg")
gdf = gp.read_file(isl_path)

config_path = os.path.join(current_folder, "config.py")
sys.path.append(os.path.dirname(config_path))
import config
proj = config.proj
ee.Initialize(project = proj)

dataset = ee.ImageCollection("ECMWF/ERA5/MONTHLY")

# Most recent date
sorted_collection = dataset.sort('system:time_start', False)
last_image = sorted_collection.first()
timestamp_ms = last_image.get('system:time_start').getInfo()
last_date = datetime.datetime.fromtimestamp(timestamp_ms/1000.0)
print(f"Last image date:{last_date}")
# Four years window
dataset = dataset.filterDate("2016-06-01", "2020-05-31")

def mean_temp(image):
    stats = image.reduceRegion(
        reducer = ee.Reducer.mean(),  # mean temp
        geometry = multip_geo,
        scale = 1000,  # MODIS resolution
        bestEffort = True
    )
    return image.set("mean_temp", stats.get("mean_2m_air_temperature"), "date", image.date().format())
def mean_prec(image):
    stats = image.reduceRegion(
        reducer = ee.Reducer.mean(),  # precipitation mean
        geometry = multip_geo,
        bestEffort = True
    )
    return image.set("mean_prec", stats.get("total_precipitation"), "date", image.date().format())

# Load data if exist, else initialize dictionary
output_folder = os.path.join(project_folder, "data/final_data")
os.makedirs(output_folder, exist_ok = True)
output_path = os.path.join(output_folder, "temp.pkl")
if os.path.exists(output_path):
    with open(output_path, 'rb') as file:
            temp = pickle.load(file)
    output_path = os.path.join(output_folder, "temp_nodata.pkl")
    with open(output_path ,  'rb') as file:
            temp_nodata = pickle.load(file)
    output_path = os.path.join(output_folder, "prec.pkl")
    with open(output_path ,  'rb') as file:
            prec = pickle.load(file)
    output_path = os.path.join(output_folder, "prec_nodata.pkl")
    with open(output_path ,  'rb') as file:
            prec_nodata = pickle.load(file)
else:
    temp = {}
    temp_nodata = {}
    prec = {}
    prec_nodata = {}

# Iterate for islands
print(f'Total islands: {len(gdf)}')
for k, (i, isl) in enumerate(gdf.iterrows(), 1):
    if k % 100 == 0 or k==len(gdf):
        print(f'{k} islands made')
    if k % 10 == 0:
        # Periodic exportation
        output_path = os.path.join(output_folder, "temp.pkl")
        with open(output_path, "wb") as f:
            pickle.dump(temp, f)
        output_path = os.path.join(output_folder, "temp_nodata.pkl")
        with open(output_path, "wb") as f:
            pickle.dump(temp_nodata, f)
        output_path = os.path.join(output_folder, "prec.pkl")
        with open(output_path, "wb") as f:
            pickle.dump(prec, f)
        output_path = os.path.join(output_folder, "prec_nodata.pkl")
        with open(output_path, "wb") as f:
            pickle.dump(prec_nodata, f)
    ID = isl.ALL_Uniq
    if ID not in temp:
        multi = isl.geometry
        multip_list = [
            [list(vert) for vert in poly.exterior.coords]
            for poly in multi.geoms
        ]
        multip_geo = ee.Geometry.MultiPolygon(multip_list)
        # Images clip
        collection = dataset.filterBounds(multip_geo)
        # Map previously defined functions on the collection
        temp_means = collection.map(mean_temp)
        mean_list1 = temp_means.aggregate_array("mean_temp").getInfo()
        # No data
        if mean_list1 == []:
            temp[ID] = np.nan
            temp_nodata[ID] = 1
        else:
            # Kelvin-Celsius conversion
            temp[ID] = np.mean(mean_list1)-273
            temp_nodata[ID] = 0
    
        prec_means = collection.map(mean_prec)
        mean_list2 = prec_means.aggregate_array("mean_prec").getInfo()
        if mean_list2 == []:
            prec[ID] = np.nan
            prec_nodata[ID] = 1
        else:
            # Annual mean (4 years window)
            prec[ID] = (np.sum(mean_list2))/4
            prec_nodata[ID] = 0

# Expo
percorso_file = os.path.join(output_folder, "temp.pkl")
with open(percorso_file, "wb") as f:
    pickle.dump(temp, f)
percorso_file = os.path.join(output_folder, "temp_nodata.pkl")
with open(percorso_file, "wb") as f:
    pickle.dump(temp_nodata, f)
percorso_file = os.path.join(output_folder, "prec.pkl")
with open(percorso_file, "wb") as f:
    pickle.dump(prec, f)
percorso_file = os.path.join(output_folder, "prec_nodata.pkl")
with open(percorso_file, "wb") as f:
    pickle.dump(prec_nodata, f)