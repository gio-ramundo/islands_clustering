import numpy as np
import geopandas as gp
import ee
import pickle
import os
import sys
from shapely import MultiPolygon, Polygon

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..")

isl_path = os.path.join(project_folder, "data/filtered/final", "islands_4.gpkg")
gdf = gp.read_file(isl_path)

config_path = os.path.join(current_folder, "config.py")
sys.path.append(os.path.dirname(config_path))
import config
proj = config.proj
ee.Initialize(project = proj)

# Dataser and variables selection
dataset = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR")
dataset = dataset.select(['u_component_of_wind_10m','v_component_of_wind_10m'])
dataset1 = ee.ImageCollection("ECMWF/ERA5/DAILY")
dataset1 = dataset1.select(['u_component_of_wind_10m','v_component_of_wind_10m'])

# More recent image
sorted_collection = dataset1.sort('system:time_start', False)
last_image = sorted_collection.first()
timestamp_ms = last_image.get('system:time_start').getInfo()
import datetime
last_date = datetime.datetime.fromtimestamp(timestamp_ms/1000.0)
print(f"Last image date: {last_date}")

# Most recent 4 year period
dataset = dataset.filterDate("2016-07-01", "2020-06-30")
dataset1 = dataset1.filterDate("2016-07-01", "2020-06-30")

# Function to add a band containing the cube of wind speed
def wind_power(image):
    u = image.select('u_component_of_wind_10m')
    v = image.select('v_component_of_wind_10m')
    wind_speed = u.pow(2).add(v.pow(2)).sqrt()
    wind_power = wind_speed.pow(3).rename('wind_power')
    return image.addBands(wind_power)
#Function to compute mean power
def mean_power(image):
    stats = image.reduceRegion(
        reducer = ee.Reducer.mean(),
        geometry = multip_geo,
        bestEffort = True
    )
    return image.set("mean_power", stats.get("wind_power"), "date", image.date().format())
#Function to compute standard deviation
def dev_std(collection):
    # List containing mean powers for every month
    power_list = []
    for i in range(1,13):
        collection_month = collection.filter(ee.Filter.calendarRange(i, i, 'month'))
        power_means_month = collection_month.map(mean_power)
        mean_list = power_means_month.aggregate_array("mean_power").getInfo()
        power_list.append(np.mean(mean_list))
    standard_dev = np.std(power_list)
    return standard_dev

# Data load if existing, else initialize dictionaries
output_folder = os.path.join(project_folder, "data/final_data")
os.makedirs(output_folder, exist_ok=True)
output_path = os.path.join(output_folder, "wind_power.pkl")
if os.path.exists(output_path):
    with open(output_path, 'rb') as file:
        wind = pickle.load(file)
    output_path = os.path.join(output_folder, "wind_nodata.pkl")
    with open(output_path , 'rb') as file:
        wind_nodata = pickle.load(file)
    output_path = os.path.join(output_folder, "wind_std.pkl")
    with open(output_path ,  'rb') as file:
        std = pickle.load(file)
else:
    wind = {}
    wind_nodata = {}
    std = {}

gdf = gdf.sort_values(by = 'IslandArea', ascending = False)
# Iterate for islands
for k, (i, isl) in enumerate(gdf.iterrows(), 1):
    if k%100 == 0 or k == len(gdf):
        print(f'{k} islands made')
    if k % 10 == 0:
        # Periodic exportation
        output_path = os.path.join(output_folder, "wind_power.pkl")
        with open(output_path, "wb") as f:
            pickle.dump(wind, f)
        output_path = os.path.join(output_folder, "wind_nodata.pkl")
        with open(output_path, "wb") as f:
            pickle.dump(wind_nodata, f)
        output_path = os.path.join(output_folder, "wind_std.pkl")
        with open(output_path, "wb") as f:
            pickle.dump(std, f)
    ID = isl.ALL_Uniq
    if ID not in wind or k == 1:
        # Big islands geometry simplification
        if isl.IslandArea>10000:
            simpli = isl.geometry.simplify(tolerance = 0.005, preserve_topology = True)
        elif isl.IslandArea>5000:
            simpli = isl.geometry.simplify(tolerance = 0.003, preserve_topology = True)
        elif isl.IslandArea>2000:
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
        # Images intersection and power band addition
        collection = dataset.filterBounds(multip_geo)
        power_collection = collection.map(wind_power)
        # Mean power
        power_means = power_collection.map(mean_power)
        mean_list = power_means.aggregate_array("mean_power").getInfo()
        # Mean, deviation and nodata update if data gathered
        if len(mean_list) > 0:
            wind[ID] = np.mean(mean_list)
            wind_nodata[ID] = 0
            std[ID] = (dev_std(power_means))/(np.mean(mean_list))
        # If no data for ERA-5 land try ERA5
        else:
            collection = dataset1.filterBounds(multip_geo)
            power_collection = collection.map(wind_power)
            power_means = power_collection.map(mean_power)
            mean_list  =  power_means.aggregate_array("mean_power").getInfo()
            if len(mean_list)>0:
                wind[ID] = np.mean(mean_list)
                wind_nodata[ID] = 0
                std[ID] = (dev_std(power_means))/(np.mean(mean_list))
            # No data
            else:
                wind[ID] = np.nan
                wind_nodata[ID] = 1
                std[ID] = np.nan

# Expo
output_path = os.path.join(output_folder, "wind_power.pkl")
with open(output_path, "wb") as f:
    pickle.dump(wind, f)
output_path = os.path.join(output_folder, "wind_nodata.pkl")
with open(output_path, "wb") as f:
    pickle.dump(wind_nodata, f)
output_path = os.path.join(output_folder, "wind_std.pkl")
with open(output_path, "wb") as f:
    pickle.dump(std, f)