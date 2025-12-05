import geopandas as gp
import os
from rtree import index
import pickle

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..")

isl_path = os.path.join(project_folder, "data/filtered/final", "islands.gpkg")
gdfisl = gp.read_file(isl_path)

hydro_path = os.path.join(project_folder, "files", "hydro.gpkg")
gdfh = gp.read_file(hydro_path)

# Index to facilitate intersection iteration
print(f'Hydro sites: {len(gdfh)}')
idx = index.Index()
for k,(i, row) in enumerate(gdfh.iterrows(),1):
    if k%100000 == 0 or k == len(gdfh):
        print(f'{k} hydro sites analyzed')
    bbox = row.geometry.bounds
    idx.insert(i, bbox)

# Dictionary to store values
hydro = {}
# Iterate for islands
print(f'Total islands: {len(gdfisl)}')
for k,(i, isl) in enumerate(gdfisl.iterrows(),1):
    if k%100==0 or k==len(gdfisl):
        print(f'{k} islands made')
    ID=isl.ALL_Uniq
    poly = isl.geometry
    bbox_isl = poly.bounds
    # Hydro sites contained in island bounds
    potentials = list(idx.intersection(bbox_isl))
    power_sum = 0.0
    # Potentials contained check
    for cand in potentials:
        points = gdfh.loc[cand].geometry
        if poly.contains(points):
            power_sum += gdfh.loc[cand, 'kWh_year_1']
            idx.delete(cand, points.bounds)
    hydro[ID] = power_sum

# Expo
percorso_folder_out = os.path.join(project_folder, "data/final_data")
os.makedirs(percorso_folder_out, exist_ok=True)
percorso_file = os.path.join(percorso_folder_out, "hydro.pkl")
with open(percorso_file, "wb") as f:
    pickle.dump(hydro, f)