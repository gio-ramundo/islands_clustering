import geopandas as gp
import os
from pyproj import CRS, Transformer
import utm
from shapely.ops import transform
from rtree import index
from shapely import box

current_path = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_path, "..", "..")

file_path = os.path.join(project_folder, "data/filtered/population", "islands_4.gpkg")
gdf = gp.read_file(file_path)

# Coordinate system
crs_4326 = CRS.from_epsg(4326)

# Buffer generation function
def buffer_isl(multi):
    lon, lat = multi.centroid.x, multi.centroid.y
    # UTM zone identification
    utm_zone = utm.from_latlon(lat, lon)
    utm_crs = 32600 + utm_zone[2]
    crs_m = CRS.from_epsg(utm_crs)
    transformer_dir = Transformer.from_crs(crs_4326, crs_m, always_xy = True)
    transformer_inv = Transformer.from_crs(crs_m, crs_4326, always_xy = True)
    # Coordinate system conversion
    project_to_utm = lambda x, y: transformer_dir.transform(x, y)
    project_to_wgs84 = lambda x, y: transformer_inv.transform(x, y)
    
    # Conversion, buffer, reconversion
    multi_utm = transform(project_to_utm, multi)
    buffer_utm = multi_utm.buffer(1000)
    multi_4326 = transform(project_to_wgs84, buffer_utm)
    return multi_4326

# Islands iteration
print(f'{len(gdf)} total islands')
for k,(i,isl) in enumerate(gdf.iterrows(), 1):
    if k%100 == 0 or k == len(gdf):
        print(f'{k} islands made')
    buffer = buffer_isl(gdf.loc[i,'geometry'])
    # Earth limits check
    if buffer.bounds[0]*buffer.bounds[2] > 0:
        gdf.loc[i,'geometry'] = buffer
    else:
        gdf.loc[i,'geometry'] = gdf.loc[i,'geometry'].buffer(0.009)

# Object to simplify intersection research
idx = index.Index()
for i, isl in gdf.iterrows():
    idx.insert(i, isl.geometry.bounds)

# Continents
file_path = os.path.join(project_folder, "files", "continents.gpkg")
gdf1 = gp.read_file(file_path)
print(f'Islands before distance filter: {len(gdf)}')
# Continents iteration
print(f'Iterate for {len(gdf1)} continents')
# Excluded islands counter
j = 0
for k,(i,cont) in enumerate(gdf1.iterrows(),1):
    candidates = list(idx.intersection(cont.geometry.bounds))
    print(f'Continent {k}')
    print(f'Islands to check: {len(candidates)}')
    for h, cand in enumerate(candidates, 1):
        if h % 100 == 0 or h == (len(candidates)):
            print(f'{h} islands checked')
        geom = gdf.loc[cand].geometry
        rect = box(geom.bounds[0], geom.bounds[1], geom.bounds[2], geom.bounds[3])
        if rect.intersects(cont.geometry):
            if geom.intersects(cont.geometry):
                j += 1
                idx.delete(cand, gdf.loc[cand].geometry.bounds)
                gdf = gdf.drop(cand)
print(f'Islands excluded: {j}')

# Too big islands
out_path = os.path.join(project_folder, "data/excluded", "big_islands.gpkg")
gdf1 = gp.read_file(out_path)
print(f'Iterate for {len(gdf1)} excluded big islands')
j = 0
for k,(i,isl) in enumerate(gdf1.iterrows(), 1):
    if k%5 == 0 or k == len(gdf1):
        print(f'{k} excluded islands checked')
    candidates = list(idx.intersection(isl.geometry.bounds))
    for cand in candidates:
        geom = gdf.loc[cand].geometry
        if geom.intersects(isl.geometry):
            j += 1
            idx.delete(cand, geom.bounds)
            gdf = gdf.drop(cand)
print(f'Too near islands: {j}')

# Too populated islands
out_path = os.path.join(project_folder, "data/excluded", "populated_islands.gpkg")
gdf1 = gp.read_file(out_path)
print(f'Iterate for {len(gdf1)} excluded populated islands')
j = 0
for k,(i,isl) in enumerate(gdf1.iterrows(), 1):
    if k%10 == 0 or k == len(gdf1):
        print(f'{k} excluded islands checked')
    candidates = list(idx.intersection(isl.geometry.bounds))
    for cand in candidates:
        geom = gdf.loc[cand].geometry
        if geom.intersects(isl.geometry):
            j += 1
            idx.delete(cand, geom.bounds)
            gdf = gdf.drop(cand)
print(f'Too near islands: {j}')

# Expo
out_folder = os.path.join(project_folder, "data/filtered/final")
os.makedirs(out_folder, exist_ok = True)
out_path = os.path.join(out_folder, 'islands_4.gpkg')
gdf.to_file(out_path, driver = "GPKG")

IDs = list(gdf.ALL_Uniq)

# Update different round dataframe
file_path = os.path.join(project_folder, "data/filtered/population", "islands.gpkg")
gdf = gp.read_file(file_path)
for i,isl in gdf.iterrows():
    if isl.ALL_Uniq not in IDs:
        gdf = gdf.drop(i)
out_path = os.path.join(project_folder, "data/filtered/final/islands.gpkg")
gdf.to_file(out_path, driver = "GPKG")

file_path = os.path.join(project_folder, "data/filtered/population", "islands_3.gpkg")
gdf = gp.read_file(file_path)
for i,isl in gdf.iterrows():
    if isl.ALL_Uniq not in IDs:
        gdf = gdf.drop(i)
out_path = os.path.join(project_folder, "data/filtered/final/islands_3.gpkg")
gdf.to_file(out_path, driver = "GPKG")

file_path = os.path.join(project_folder, "data/filtered/population", "islands_2.gpkg")
gdf = gp.read_file(file_path)
for i,isl in gdf.iterrows():
    if isl.ALL_Uniq not in IDs:
        gdf = gdf.drop(i)
out_path = os.path.join(project_folder, "data/filtered/final/islands_2.gpkg")
gdf.to_file(out_path, driver = "GPKG")