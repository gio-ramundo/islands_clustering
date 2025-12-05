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

# Protected area dataset
wdpa_polygons = ee.FeatureCollection('WCMC/WDPA/current/polygons')
# New df column
gdf['area_protected'] = 0

# Iterate for islands
for k, (i, isl) in enumerate(gdf.iterrows(), 1):
    if (k-1)%10 == 0:
        print(f'{k-1} index')
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

        # Intersecting area
        intersecting_wdpa = wdpa_polygons.filter(ee.Filter.intersects('.geo', ee_geometry_original))
        union_of_intersecting_wdpa = intersecting_wdpa.union()
        # Protected area elimination
        ee_geometry_protected = ee_geometry_original.difference(union_of_intersecting_wdpa)
        # Area calculation and df update
        area1 = ee_geometry_protected.area().getInfo()
        gdf.loc[i,'area_protected'] = area1/area0
    else:
        gdf = gdf.drop(i)

print(f'Mean area ratio f{np.mean(gdf['area_protected'])}')