import rasterio
import rasterio.mask
from shapely.geometry import box, mapping
import numpy as np
import geopandas as gp
import pickle
import os

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..")

# Solar data, annual and monthly
fie_path = os.path.join(project_folder, "files", "PVOUT-year.tif")
src = rasterio.open(fie_path)
for i in range(1,13):
    if i<10:
        fie_path = os.path.join(project_folder, "files", f"PVOUT_month/PVOUT_0{i}.tif")
    else:
        fie_path = os.path.join(project_folder, "files", f"PVOUT_month/PVOUT_{i}.tif")
    globals()[f"src{i}"] = rasterio.open(fie_path)
#bordi del file
bounds = box(*src.bounds)
maxx = bounds.exterior.coords[0][0]
minx = bounds.exterior.coords[2][0]
maxy = bounds.exterior.coords[1][1]
miny = bounds.exterior.coords[0][1]

file_path = os.path.join(project_folder, "data/filtered/final", "islands.gpkg")
gdf = gp.read_file(file_path)

# Mean value for input geometry and file
def mean(multi,sr):
    out_image, _ = rasterio.mask.mask(sr, [mapping(multi)], crop = True, all_touched = True)
    no_data_value = src.nodata
    valid_pixels = out_image[(out_image != no_data_value) & (out_image != 0)]
    list_len = np.count_nonzero(~np.isnan(valid_pixels))
    return np.nanmean(valid_pixels) if list_len > 0 else np.nan

# Annual mean and Solar Seasonality Index
def request(multip):
    out = mean(multip, src)
    months = []
    for i in range(1,13):
        months.append(mean(multip,globals()[f"src{i}"]))
    sea_index = max(months)/min(months)
    return out, sea_index

# Dictionaries to stoe computed data
pvout_mean = {}
pvout_ind = {}
isl_out = {}
# Iterate for islands
print(f'Total islands:{len(gdf)}')
for k,(i,isl) in enumerate(gdf.iterrows(),1):
    if k%10 == 0 or k == len(gdf):
        print(f'{k} islands made')
    ID = isl.ALL_Uniq
    multi = isl.geometry
    # Island not contained
    if multi.disjoint(bounds):
        pvout_mean[ID] = np.nan
        pvout_ind[ID] = np.nan
        isl_out[ID] = 1
    else:
        out,s_ind = request(multi)
        pvout_mean[ID] = out
        pvout_ind[ID] = s_ind
        # No data
        if np.isnan(out):
            isl_out[ID] = 1
        else:
            isl_out[ID] = 0

# Expo
folder_out = os.path.join(project_folder, "data/final_data")
os.makedirs(folder_out, exist_ok = True)
out_path = os.path.join(folder_out, "solar_pow.pkl")
with open(out_path, "wb") as f:
    pickle.dump(pvout_mean, f)
out_path = os.path.join(folder_out, "solar_seas_ind.pkl")
with open(out_path, "wb") as f:
    pickle.dump(pvout_ind, f)
out_path = os.path.join(folder_out, "solar_nodata.pkl")
with open(out_path, "wb") as f:
    pickle.dump(isl_out, f)