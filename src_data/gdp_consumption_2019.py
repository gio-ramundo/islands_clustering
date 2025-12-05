import rasterio
import rasterio.mask
from shapely.geometry import box, mapping
import numpy as np
import geopandas as gp
import pickle
import os

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..")

# Consumption file load
file_folder = os.path.join(project_folder, "files")
file_path = os.path.join(file_folder, "EC2019.tif")
src = rasterio.open(file_path)
bounds = box(*src.bounds)

isl_path=os.path.join(project_folder, "data/filtered/final", "islands.gpkg")
df = gp.read_file(file_path)

# CRS conversion
if df.crs != src.crs:
    df = df.to_crs(src.crs)

# Function for pixel inside a geometry sum
def richiesta(multi):
    try:
        out_image, _ = rasterio.mask.mask(src, [mapping(multi)], crop=True, all_touched=True)
        no_data_value = src.nodata
        valid_pixels = out_image[(out_image != no_data_value) & (out_image != 0)]
        # No valid pixels
        if valid_pixels.size == 0:
            raise ValueError("No valid pixels found within the geometry.")
        sum = np.sum(valid_pixels)
        # Binary indicator for geometry contained in the file
        indicator = int(not multi.within(bounds))
        return float(sum), indicator
    except Exception:
        return np.nan, 1

# Initialize dictionaries and iterate for islands
consumption={}
no_data={}
print(f'Total islands:{len(df)}')
for k,(i,isl) in enumerate(df.iterrows(),1):
    if k%250==0 or k==len(df):
        print(f'{k} islands made')
    ID=isl.ALL_Uniq
    multi=isl.geometry
    sum,nodata=richiesta(multi)
    consumption[ID]=sum
    no_data[ID]=nodata

# Repeat for GDP
percorso_file = os.path.join(file_folder, "2019GDP.tif")
src = rasterio.open(percorso_file)
bounds = box(*src.bounds)

gdp={}
no_data1={}
print(f'Total islands:{len(df)}')
for k,(i,isl) in enumerate(df.iterrows(),1):
    if k%250==0 or k==len(df):
        print(f'{k} islands made')
    ID = isl.ALL_Uniq
    multi = isl.geometry
    sum,nodata = richiesta(multi)
    gdp[ID] = sum
    no_data1[ID] = nodata

# Expo
output_folder = os.path.join(project_folder, "data/final_data")
os.makedirs(output_folder, exist_ok=True)
output_path=os.path.join(output_folder, "consumption.pkl")
with open(output_path, "wb") as f:
    pickle.dump(consumption, f)
output_path=os.path.join(output_folder, "cons_nodata.pkl")
with open(output_path, "wb") as f:
    pickle.dump(no_data, f)
output_path=os.path.join(output_folder, "gdp_2019.pkl")
with open(output_path, "wb") as f:
    pickle.dump(gdp, f)
output_path=os.path.join(output_folder, "gdp_2019_nodata.pkl")
with open(output_path, "wb") as f:
    pickle.dump(no_data1, f)