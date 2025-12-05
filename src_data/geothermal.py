from shapely.geometry import box, mapping
import numpy as np
import geopandas as gp
import pickle
import os

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..")

# SETUP
file_path = os.path.join(project_folder, "files", "geothermal_potential.gpkg")
dfgeo = gp.read_file(file_path)
file_path = os.path.join(project_folder, "data/filtered/final", "islands.gpkg")
dfisl = gp.read_file(file_path)
file_path = os.path.join(project_folder, "data/filtered/final", "islands_buffer.gpkg")
dfbuf = gp.read_file(file_path)

# Dictionary for storing islands potentials
geotherm = {elemento: 0 for elemento in list(dfisl.ALL_Uniq)}
# Dictionary for storing associations geotherm site-island
geotherm1 = {}

# Iterate fo rislands
print(f'Total islands: {len(dfisl)}')
for k,(index_isl, isl) in enumerate(dfisl.iterrows(), 1):
    if k%100 == 0 or k == len(dfisl):
        print(f'{k} isole made')
    multi = isl.geometry
    ID = isl.ALL_Uniq
    buffer = dfbuf[dfbuf['ALL_Uniq'] == ID].iloc[0]['geometry']
    # Iterate for geothermal sites
    for index_geo, geo_point in dfgeo.iterrows():
        point = geo_point.geometry
        # Point contained
        if multi.contains(point):
            # Number extraction from geo file columns
            a = float(geo_point.q.replace(",", "."))
            # Eventual previous association deleted
            if index_geo in geotherm1:
                isl2 = dfisl.loc[geotherm1[index_geo]]
                geotherm[isl2.ALL_Uniq] -= a
            # Dictionary addition and point deletion (point contained no other association possible)
            geotherm[ID] += a
            dfgeo = dfgeo.drop(index_geo)
        
        # Point contained in buffer geometry
        elif buffer.contains(geo_point):
            a = float(geo_point.q.replace(",", "."))
            # No previous association
            if index_geo not in geotherm1:
                geotherm[ID] += a
                geotherm1[index_geo] = index_isl
            # Check wich island is closer to the point
            else:
                dist1 = isl.geometry.distance(geo_point)
                isl2 = dfisl.loc[geotherm1[index_geo]]
                dist2 = isl2.geometry.distance(geo_point)
                if dist1 < dist2:
                    geotherm[ID] += a
                    geotherm[isl2.ALL_Uniq] -= a
                    geotherm1[index_geo] = index_isl

# Expo
folder_out = os.path.join(project_folder, "data/final_data")
os.makedirs(folder_out, exist_ok = True)
percorso_file = os.path.join(folder_out, "geothermal_potential.pkl")
with open(percorso_file, "wb") as f:
    pickle.dump(geotherm, f)