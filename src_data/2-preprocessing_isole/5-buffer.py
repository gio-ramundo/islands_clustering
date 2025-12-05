import geopandas as gp
from shapely.ops import transform
import os
from pyproj import CRS, Transformer
import utm

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..")

isl_path = os.path.join(project_folder, "data/filtered/final", "islands.gpkg")
gdf = gp.read_file(isl_path)

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
    # Coordinate system conversion functions
    project_to_utm = lambda x, y: transformer_dir.transform(x, y)
    project_to_wgs84 = lambda x, y: transformer_inv.transform(x, y)
    # Conversion, buffer, reconversion
    multi_utm = transform(project_to_utm, multi)
    buffer_utm = multi_utm.buffer(60000)
    multi_4326 = transform(project_to_wgs84, buffer_utm)
    return multi_4326

print(f'File length: {len(gdf)}')
for k,(i,isl) in enumerate(gdf.iterrows(), 1):
    if k%500 == 0 or k == len(gdf):
        print(f'{k} islands made')
    buffer = buffer_isl(gdf.loc[i,'geometry'])
    # Earth limits check
    if buffer.bounds[0]*buffer.bounds[2]>0:
        gdf.loc[i,'geometry'] = buffer
    else:
        gdf.loc[i,'geometry'] = gdf.loc[i,'geometry'].buffer(0.54)

# Expo
percorso_folder_out = os.path.join(project_folder, "data/filtered/final")
os.makedirs(percorso_folder_out, exist_ok = True)
percorso_out = os.path.join(percorso_folder_out, "islands_buffer.gpkg")
gdf.to_file(percorso_out, driver = "GPKG")