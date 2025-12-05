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
gdf = gdf.sort_values(by = 'IslandArea', ascending = False)

config_path = os.path.join(current_folder, "..", "config.py")
sys.path.append(os.path.dirname(config_path))
import config
proj = config.proj
ee.Initialize(project = proj)

ele = ee.ImageCollection("JAXA/ALOS/AW3D30/V3_2")
# New column
gdf['area_alt'] = 0

# Iterate for islands
for k, (i, isl) in enumerate(gdf.iterrows(), 1):
    if (k-1)%10 == 0:
        print(f'{k-1} islands made')
        print(f'{isl.IslandArea} current area')
        # Geomtry simplification
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

        # Images itersecting the island
        collection = ele.filterBounds(ee_geometry_original)
        # One image
        if collection.size().getInfo() == 1:
            ele_clip = collection.first().clip(ee_geometry_original)
            ele_mask = ele_clip.select('DSM').gt(2000)
            scale = ele_clip.select('DSM').projection().nominalScale().getInfo()
            vectors_alt = ele_mask.selfMask().reduceToVectors(
                geometry = ele_mask.geometry(),
                scale = scale,
                crs = ele_mask.projection().crs(),
                eightConnected = True,
                bestEffort = True
            )
            ele_geometry = vectors_alt.union(ee.ErrorMargin(1)).geometry()
            ee_geometry_alt = ee_geometry_original.difference(ele_geometry, ee.ErrorMargin(1))
        # Different images
        else:
            list = collection.toList(collection.size())
            for j in range(collection.size().getInfo()):
                img = ee.Image(list.get(j)).clip(ee_geometry_original)
                mask_alt = img.select('DSM').gt(2000)
                scale = img.select('DSM').projection().nominalScale().getInfo()
                vectors_alt = mask_alt.selfMask().reduceToVectors(
                    geometry = mask_alt.geometry(),
                    scale = scale,
                    crs = mask_alt.projection().crs(),
                    eightConnected = True,
                    bestEffort = True
                )
                ele_geometry = vectors_alt.union(ee.ErrorMargin(1)).geometry()
                if j == 0:
                    ee_geometry_alt = ee_geometry_original.difference(ele_geometry, ee.ErrorMargin(1))
                else:
                    ee_geometry_alt = ee_geometry_alt.difference(ele_geometry, ee.ErrorMargin(1))
        # Area calculation and df update
        area1 = ee_geometry_alt.area().getInfo()
        if area1 < area0:
            print(k-1)
        gdf.loc[i,'area_alt'] = area1/area0
    else:
        gdf = gdf.drop(i)

print(f'Mean area ratio {np.mean(gdf['area_alt'])}')