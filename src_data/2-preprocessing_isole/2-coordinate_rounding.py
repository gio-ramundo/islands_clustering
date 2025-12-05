import geopandas as gp
import os
from shapely.geometry import MultiPolygon, Polygon
from collections import OrderedDict

# Setup
current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..")

file_path = os.path.join(project_folder, "data/filtered/area", "islands.gpkg")
gdf = gp.read_file(file_path)

# Simplify coordinates
def round(polygon, figure):
    rounded_vertexes = [(round(x, figure), round(y, figure)) for x, y in polygon.exterior.coords]
    return(Polygon(rounded_vertexes))
# Delete duplicate points
def remove(polygon):
    no_dup_vert = list(OrderedDict.fromkeys(polygon.exterior.coords))
    if (len(no_dup_vert)>2):
        return Polygon(no_dup_vert)
    else:
        return 0
# Union of previous functions
def simplify(polygon, figure):
    rounded_poly = round(polygon, figure)
    simplified_poly = remove(rounded_poly)
    return simplified_poly

# Islands iteration
print(f'{len(gdf)} total islands')
for k,(i,isl) in enumerate(gdf.iterrows(), 0):
    if k%2000 == 0 or k == len(gdf)-1:
        print(f'{k} islands made')
    original = isl.geometry
    polygons = []
    for h in range(len(original.geoms)):
        poly = simplify(original.geoms[h], 4)
        if poly != 0:
            polygons.append(poly)
    # gdf update
    gdf.loc[i,'geometry'] = MultiPolygon(polygons)
# Expo
percorso_out = os.path.join(project_folder, "data/filtered/area/islands_4.gpkg")
gdf.to_file(percorso_out, driver = "GPKG")

# Repeat with 2 and 3 figure round
print('3 figures')
for k,(i,isl) in enumerate(gdf.iterrows(), 0):
    if k%2000 == 0 or k == len(gdf)-1:
        print(f'{k} islands made')
    original = isl.geometry
    polygons = []
    for h in range(len(original.geoms)):
        polygon = simplify(original.geoms[h], 3)
        if polygon != 0:
            polygons.append(polygon)
    gdf.loc[i,'geometry'] = MultiPolygon(polygons)
percorso_out = os.path.join(project_folder, "data/filtered/area/islands_3.gpkg")
gdf.to_file(percorso_out, driver = "GPKG")

print('2 figures')
for k,(i,isl) in enumerate(gdf.iterrows(), 0):
    if k%2000 == 0 or k == len(gdf)-1:
        print(f'{k} islands made')
    original = isl.geometry
    polygons = []
    for h in range(len(original.geoms)):
        polygon = simplify(original.geoms[h], 2)
        if polygon != 0:
            polygons.append(polygon)
    gdf.loc[i,'geometry'] = MultiPolygon(polygons)
percorso_out = os.path.join(project_folder, "data/filtered/area/islands_2.gpkg")
gdf.to_file(percorso_out, driver = "GPKG")