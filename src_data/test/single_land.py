import geopandas as gp
import ee
import os
import sys
import numpy as np
from shapely import Polygon

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..")

isl_path = os.path.join(project_folder, "data/filtered/final", "islands_3.gpkg")
gdf = gp.read_file(isl_path)
gdf = gdf.sort_values(by='IslandArea', ascending=True)

config_path = os.path.join(current_folder, "..", "config.py")
sys.path.append(os.path.dirname(config_path))
import config
proj = config.proj
ee.Initialize(project=proj)

# Land dataset and more recent image
lc100_collection = ee.ImageCollection("COPERNICUS/Landcover/100m/Proba-V-C3/Global")
lc_image = ee.Image(lc100_collection.sort('system:time_start', False).first())
# Codes relative to not valid land
excluded_values = [0, 40, 50, 70, 80, 111, 112, 113, 114, 115, 116]

# New df columns
for h in range(len(excluded_values)):
    gdf[f'Type land {h}'] = 0

# Iterate for islands
for k, (i, isl) in enumerate(gdf.iterrows(), 1):
    if (k-1)%10 == 0:
        print(f'{k-1} index')
        print(f'{isl.IslandArea} current area')
        # Geometry simplification
        if isl.IslandArea > 10000:
            geom = isl.geometry.simplify(tolerance = 0.005, preserve_topology = True)
        elif isl.IslandArea > 5000:
            geom = isl.geometry.simplify(tolerance = 0.003, preserve_topology = True)
        elif isl.IslandArea > 2000:
            geom = isl.geometry.simplify(tolerance = 0.002, preserve_topology = True)
        else:
            geom = isl.geometry.simplify(tolerance = 0.001, preserve_topology = True)
        if isinstance(geom, Polygon):
            vert_list = [vert for vert in geom.exterior.coords]
            ee_geometry_original = ee.Geometry.Polygon(vert_list)
        else:
            multip_list = [
                [vert for vert in poly.exterior.coords]
                for poly in geom.geoms
            ]
            ee_geometry_original = ee.Geometry.MultiPolygon(multip_list)
        area0 = ee_geometry_original.area().getInfo()
        
        lc_clipped = lc_image.clip(ee_geometry_original)
        # Not valid values mask and geometry extraction
        # Area calculation and df update
        scale = lc_image.select('discrete_classification').projection().nominalScale().getInfo()
        for j in range(len(excluded_values)):
            lc_mask = lc_clipped.select('discrete_classification').eq(excluded_values[j])
            vectors = lc_mask.selfMask().reduceToVectors(
                geometry = ee_geometry_original,
                scale = scale,
                crs = lc_mask.projection().crs(),
                eightConnected = True,
                bestEffort = True
                )
            lc_geometry = vectors.union(ee.ErrorMargin(1)).geometry()
            ee_geometry_valid_land = ee_geometry_original.difference(lc_geometry, ee.ErrorMargin(1))
            area1 = ee_geometry_valid_land.dissolve().area().getInfo()
            gdf.loc[i,f'Type land {j}'] = area1/area0
    else:
        gdf = gdf.drop(i)

for h in range(len(excluded_values)):
    print(f'Land code {excluded_values[h]}, mean area ratio {np.mean(gdf[f'Type land {h}'])}')