import geopandas as gp
import ee
import os
import sys
import pickle

project_folder = os.path.dirname(os.path.abspath(__file__))
current_folder = os.path.join(project_folder, "..", "..")

isl_path = os.path.join(current_folder, "data/filtered/final", "islands_3.gpkg")
gdf = gp.read_file(isl_path)

config_path = os.path.join(project_folder, "..", "config.py")
sys.path.append(os.path.dirname(config_path))
import config
proj = config.proj
ee.Initialize(project = proj)

countries_dataset = ee.FeatureCollection('FAO/GAUL_SIMPLIFIED_500m/2015/level0')

# Load eventually existing data, dictionary initialization
output_folder = os.path.join(project_folder, "data/filtered")
os.makedirs(output_folder, exist_ok = True)
output_path = os.path.join(output_folder, "nations.pkl")
if os.path.exists(output_path):
    with open(output_path, 'rb') as file:
        countries = pickle.load(file)
else:
    countries = {}
    # Manually checked intersection, not identified
    countries[88882] = ['Maldives']
    countries[89785] = ['Bangladesh']
    countries[89792] = ['Bangladesh']
    countries[89794] = ['Bangladesh']
    countries[89937] = ['Pakistan']
    countries[89982] = ['Pakistan']
    countries[90195] = ['China']
    countries[90433] = ['Republic of Korea']
    countries[277103] = ['Brazil']
    countries[277105] = ['Brazil']
    countries[277104] = ['Brazil']
    countries[277239] = ['Fiji']
    countries[277594] = ['Indonesia']
    countries[277763] = ['Indonesia']
    countries[277386] = ['Indonesia']
    countries[277901] = ['Indonesia']
    countries[277946] = ['Indonesia']
    countries[283862] = ['Indonesia']
    countries[280098] = ['Bangladesh']
    countries[280538] = ['Viet Nam']
    countries[280549] = ['Viet Nam']
    countries[280552] = ['Viet Nam']
    countries[280664] = ['China']
    countries[283115] = ['Solomon Islands']
    countries[289686] = ['Viet Nam']
    countries[290776] = ['Norway']
    countries[340640] = ['China']
    countries[340642] = ['China']
    countries[370285] = ['Viet Nam']
    countries[289908] = ['Japan']

# Intersecting countries function
def island_feature(feature):
    geom = feature.geometry()
    intersects = countries_dataset.filterBounds(geom)
    names = intersects.aggregate_array('ADM0_NAME')
    return feature.set({'intersecting_countries': names})

# Functions that map previous function
def get_gdf_dict(df):
    feats = []
    for idx, row in df.iterrows():
        ID = row['ALL_Uniq']
        if ID  in countries:
            continue  # Already computed island
        geojson = row['geometry'].__geo_interface__
        feats.append(
            ee.Feature(ee.Geometry(geojson), {'_idx': idx, 'name': row['ALL_Uniq']})
        )
    # Create a feature collection to map previous function
    fc = ee.FeatureCollection(feats)
    result_fc = fc.map(island_feature)
    features = result_fc.getInfo()['features']
    # Dictionary update
    for f in features:
        name = f['properties']['name']
        country_list = f['properties']['intersecting_countries']
        countries[name] = list(dict.fromkeys(country_list))

# df subdivision for not exceed max payload
print(f'Total islands: {len(gdf)}')
gdf1 = gdf[(gdf['IslandArea'] <= 500)]
print(f'Very small islands: {len(gdf1)}')
imp = 50
a = 0
b = a+imp
while True:
    if b%200 == 0 or b == len(gdf1):
        print(f'{b} islands made')
    gd = gdf1.iloc[a:b]
    get_gdf_dict(gd)
    # Expo
    output_path = os.path.join(output_folder, "nations.pkl")
    with open(output_path, "wb") as f:
        pickle.dump(countries, f)
    if b == (len(gdf1)):
        break
    else:
        a += imp
        b += imp
        b = min(b,(len(gdf1)))
print('Very small islands finished')

gdf1 = gdf[(gdf['IslandArea'] > 500) & (gdf['IslandArea'] <= 1000)]
print(f'Small islands: {len(gdf1)}')
imp = 20
a = 0
b = a + imp 
while True:
    if b%40 == 0 or b == len(gdf1):
        print(f'{b} islands made')
    gd = gdf1.iloc[a:b]
    get_gdf_dict(gd)
    output_path = os.path.join(output_folder, "nations.pkl")
    with open(output_path, "wb") as f:
        pickle.dump(countries, f)
    if b == (len(gdf1)):
        break
    else:
        a += imp
        b += imp
        b = min(b,(len(gdf1)))
print('Small islands finished')

gdf1 = gdf[(gdf['IslandArea'] > 1000) & (gdf['IslandArea'] <= 3000)]
print(f'Medium islands: {len(gdf1)}')
imp = 10
a = 0
b = a + imp
while True:
    print(f'{b} islands made')
    gd = gdf1.iloc[a:b]
    get_gdf_dict(gd)
    output_path = os.path.join(output_folder, "nations.pkl")
    with open(output_path, "wb") as f:
        pickle.dump(countries, f)
    if b == (len(gdf1)):
        break
    else:
        a += imp
        b += imp
        b = min(b,(len(gdf1)))
print('Medium islands finished')

gdf1 = gdf[(gdf['IslandArea']>3000) & (gdf['IslandArea']<=5000)]
print(f'Medium-big islands: {len(gdf1)}')
imp = 4
a = 0
b = a + imp 
while True:
    print(f'{b} islands made')
    gd = gdf1.iloc[a:b]
    get_gdf_dict(gd)
    output_path = os.path.join(output_folder, "nations.pkl")
    with open(output_path, "wb") as f:
        pickle.dump(countries, f)
    if b == (len(gdf1)):
        break
    else:
        a += imp
        b += imp
        b = min(b,(len(gdf1)))
print('Medium-big islands finished')

gdf1 = gdf[(gdf['IslandArea'] > 5000) & (gdf['IslandArea'] <= 10000)]
print(f'Big islands: {len(gdf1)}')
imp = 3
a = 0
b = a + imp 
while True:
    print(f'{b} islands made')
    gd = gdf1.iloc[a:b]
    get_gdf_dict(gd)
    output_path = os.path.join(output_folder, "nations.pkl")
    with open(output_path, "wb") as f:
        pickle.dump(countries, f)
    if b == (len(gdf1)):
        break
    else:
        a += imp
        b += imp
        b = min(b,(len(gdf1)))
print('Big islands finished')

# Simplification of a very big island, it exceeds max payload
ID = gdf.query("ALL_Uniq == 273766").index[0]
multi = gdf.loc[ID, 'geometry']
multi1 = (multi.simplify(tolerance = 0.005, preserve_topology = True))
gdf.loc[ID, 'geometry'] = multi1
gdf1 = gdf[(gdf['IslandArea'] >= 10000)]
print(f'Very big islands: {len(gdf1)}')
imp = 1
a = 0
b = a + imp
while True:
    print(f'{b} islands made')
    gd = gdf1.iloc[a:b]
    get_gdf_dict(gd)
    output_path = os.path.join(output_folder, "nations.pkl")
    with open(output_path, "wb") as f:
        pickle.dump(countries, f)
    if b == (len(gdf1)):
        break
    else:
        a += imp
        b += imp
        b = min(b,(len(gdf1)))
print('Very big islands finished')

# Final check
for i,isl in gdf.iterrows():
    if isl.ALL_Uniq not in countries:
        print(isl.geometry.centroid)
        print(isl.ALL_Uniq)
    else:
        if countries[isl.ALL_Uniq] == []:
            print(isl.geometry.centroid)
            print(isl.ALL_Uniq)