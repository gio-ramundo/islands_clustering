import geopandas as gp
import ee
import os
import sys
import geemap
from shapely import Polygon

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..")

isl_path = os.path.join(project_folder, "data/filtered/final", "islands_3.gpkg")
gdf = gp.read_file(isl_path)

config_path = os.path.join(current_folder, "..", "config.py")
sys.path.append(os.path.dirname(config_path))
import config
proj = config.proj
ee.Initialize(project = proj)

output_folder = os.path.join(project_folder, "data/final_data/test_maps/urban")
os.makedirs(output_folder, exist_ok = True)

# Dataset load and most recent image selection
urban_collection = ee.ImageCollection("JRC/GHSL/P2023A/GHS_SMOD_V2-0")
filtered_collection = urban_collection.filterDate('2000-01-01', '2025-01-01')
sorted_collection = filtered_collection.sort('system:time_start', False)
urban_image = ee.Image(sorted_collection.first())
# Urban pixels values
urban_values = [30, 23, 22]

gdf = gdf.sort_values(by = 'IslandArea', ascending = False)
#Iterate for islands
print(f'{len(gdf)} total slands')
for k, (i, isl) in enumerate(gdf.iterrows(), 1):
    if k%100 == 0:
        print(f'{k} islands amde')
        geom = isl.geometry.simplify(tolerance = 0.005, preserve_topology = True)
        if isinstance(geom, Polygon):
            vertici_list = [vert for vert in geom.exterior.coords]
            ee_geometry_original = ee.Geometry.Polygon(vertici_list)
        else:
            multip_list = [
                [vert for vert in poly.exterior.coords]
                for poly in geom.geoms
            ]
            ee_geometry_original = ee.Geometry.MultiPolygon(multip_list)
        # Map creation
        m = geemap.Map()
        # Island geometry
        m.add_layer(ee_geometry_original, {'color': 'green'}, f'Isola originale')
        m.centerObject(ee_geometry_original,zoom = 10)
        # Urban geometry extraction
        clipped_image = urban_image.clip(ee_geometry_original)
        urban_mask = clipped_image.eq(urban_values[0])
        urban_mask = urban_mask.Or(clipped_image.eq(urban_values[1]))
        urban_mask = urban_mask.Or(clipped_image.eq(urban_values[2]))
        vectors = urban_mask.selfMask().reduceToVectors(
            geometry = urban_mask.geometry(),
            scale = clipped_image.projection().nominalScale().getInfo(),
            eightConnected = True,
            bestEffort = True
        )
        urban_geometry = vectors.union(ee.ErrorMargin(1)).geometry()
        urban_geometry = urban_geometry.intersection(ee_geometry_original)
        m.add_layer(urban_geometry, {'color': 'blue'}, f'Urban')
        # Expo
        m.centerObject(ee_geometry_original,zoom = 10)
        output_path = os.path.join(output_folder, f"map{k}.html")
        m.to_html(output_path)