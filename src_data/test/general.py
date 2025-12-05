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
gdf = gdf.sort_values(by = 'IslandArea', ascending = False)

config_path = os.path.join(current_folder, "..", "config.py")
sys.path.append(os.path.dirname(config_path))
import config
proj = config.proj
ee.Initialize(project = proj)

# Maps exportation folder
output_folder = os.path.join(project_folder, "data/final_data/test_maps/res")
os.makedirs(output_folder, exist_ok = True)

# Protected areas dataset
wdpa_polygons = ee.FeatureCollection('WCMC/WDPA/current/polygons')
# Land dataset
lc100_collection = ee.ImageCollection("COPERNICUS/Landcover/100m/Proba-V-C3/Global")
lc_image = ee.Image(lc100_collection.sort('system:time_start', False).first())
# Codes relative to not valid terrain
excluded_values = [0, 40, 50, 70, 80, 111, 112, 113, 114, 115, 116]
# Elevation dataset
ele = ee.ImageCollection("JAXA/ALOS/AW3D30/V3_2")

# Iterate for islands
for k, (i, isl) in enumerate(gdf.iterrows(), 1):
    if (k-1)%50 == 0:
        print(f'{k-1} index')
        print(f'{isl.IslandArea} area df')
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
            vertex_list = [vert for vert in geom.exterior.coords]
            ee_geometry_original = ee.Geometry.Polygon(vertex_list)
        else:
            multip_list = [
                [vert for vert in poly.exterior.coords]
                for poly in geom.geoms
            ]
            ee_geometry_original = ee.Geometry.MultiPolygon(multip_list)
        # Area caculation and map exportation
        area0 = ee_geometry_original.area().getInfo()
        print(f'{area0} area ee')
        m = geemap.Map()
        m.add_layer(ee_geometry_original, {'color': 'white'}, f'Original island')

        # Protected islands
        intersecting_wdpa = wdpa_polygons.filter(ee.Filter.intersects('.geo', ee_geometry_original))
        union_of_intersecting_wdpa = intersecting_wdpa.union()
        ee_geometry_protected = ee_geometry_original.difference(union_of_intersecting_wdpa)
        # Area caculation and layer addiction
        area1 = ee_geometry_protected.area().getInfo()
        print(f'{area1} protected areas eliminated')
        m.add_layer(ee_geometry_protected, {'color': 'yellow'}, f'No protected island')

        # Elevation
        collection = ele.filterBounds(ee_geometry_original)
        # One image
        if collection.size().getInfo() == 1:
            ele_clip = collection.first().clip(ee_geometry_original).select('DSM')
            ele_mask = ele_clip.gt(2000)
            scale = ele_clip.projection().nominalScale().getInfo()
            vectors_alt = ele_mask.selfMask().reduceToVectors(
                geometry = ele_mask.geometry(),
                scale = scale,
                crs = ele_mask.projection().crs(),
                eightConnected = True,
                bestEffort = True
            )
            ele_geometry = vectors_alt.union(ee.ErrorMargin(1)).geometry()
            ee_geometry_alti = ee_geometry_original.difference(ele_geometry, ee.ErrorMargin(1))
        # Different images
        else:
            list = collection.toList(collection.size())
            ee_geometry_alti = ee_geometry_original
            for j in range(collection.size().getInfo()):
                img = ee.Image(list.get(j)).clip(ee_geometry_original).select('DSM')
                mask_alt = img.gt(2000)
                scale = img.projection().nominalScale().getInfo()
                vectors_alt = mask_alt.selfMask().reduceToVectors(
                    geometry = mask_alt.geometry(),
                    scale = scale,
                    crs = mask_alt.projection().crs(),
                    eightConnected = True,
                    bestEffort = True
                )
                ele_geometry = vectors_alt.union(ee.ErrorMargin(1)).geometry()
                ee_geometry_alti = ee_geometry_alti.difference(ele_geometry, ee.ErrorMargin(1))

        # Area caculation and layer addiction
        area1 = ee_geometry_alti.area().getInfo()
        print(f'{area1} altitudine area')
        m.add_layer(ee_geometry_alti, {'color': 'orange'}, f'No altitudine island')
        
        # Intersection, final geometry
        ee_geometry_final = ee_geometry_protected.intersection(ee_geometry_alti)

        # Land dataset
        # Big island different process, too computational expensive
        if isl.IslandArea>2000:
            lc_clipped = lc_image.clip(ee_geometry_final)
        else:
            lc_clipped = lc_image.clip(ee_geometry_original)
        # Not valid mask and geometry extraction
        lc_mask = lc_clipped.select('discrete_classification').eq(excluded_values[0])
        for val in excluded_values[1:]:
            lc_mask = lc_mask.Or(lc_clipped.select('discrete_classification').eq(val))
        scale = lc_mask.select('discrete_classification').projection().nominalScale().getInfo()
        vectors = lc_mask.selfMask().reduceToVectors(
            geometry = lc_mask.geometry(),
            scale = scale,
            crs = lc_mask.projection().crs(),
            eightConnected = True,
            bestEffort = True
        )
        lc_geometry = vectors.union(ee.ErrorMargin(1)).geometry()
        if isl.IslandArea > 2000:
            m.add_layer(lc_geometry, {'color' : 'green'}, 'Disposable land zones')
            disposable_area = lc_geometry.area().getInfo()
            area = ee_geometry_final.area().getInfo()
            final_area = max(area-disposable_area, 0)
        # Other islands
        else:
            # Geomtry extraction
            ee_geometry_land = ee_geometry_original.difference(lc_geometry, ee.ErrorMargin(1))
            area1 = ee_geometry_land.area().getInfo()
            print(f'{area1} valid land area')
            m.add_layer(ee_geometry_land, {'color': 'green'}, f'Valid land area')
            
            # Final geometry
            ee_geometry_final = ee_geometry_final.intersection(ee_geometry_land)
            area_final = ee_geometry_final.area().getInfo()
        
        print(f'{area_final} final area')
        m.add_layer(ee_geometry_final, {'color': 'blue'}, f'Final island')
            
        # Map set and exportation
        m.centerObject(ee_geometry_original,zoom = 10)
        output_path = os.path.join(output_folder, f"map_{k-1}.html")
        m.to_html(output_path)