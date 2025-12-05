import geopandas as gp
import ee
import pickle
import os
import sys
from shapely import Polygon

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..")

isl_path = os.path.join(project_folder, "data/filtered/final", "islands_3.gpkg")
gdf = gp.read_file(isl_path)
gdf = gdf.sort_values(by='IslandArea', ascending=False)

config_path = os.path.join(current_folder, "config.py")
sys.path.append(os.path.dirname(config_path))
import config
proj = config.proj
ee.Initialize(project=proj)

# Load data if exist, else initialize dictionaries
output_folder = os.path.join(project_folder, "data/final_data")
os.makedirs(output_folder, exist_ok=True)
output_path = os.path.join(output_folder, "res_area.pkl")
if os.path.exists(output_path):
    with open(output_path, 'rb') as file:
        res_area = pickle.load(file)
    output_path = os.path.join(output_folder, "ele_max.pkl")
    with open(output_path ,  'rb') as file:
        ele_max = pickle.load(file)
else:
    res_area = {}
    ele_max = {}

# Datasets
wdpa_polygons = ee.FeatureCollection('WCMC/WDPA/current/polygons')
lc100_collection = ee.ImageCollection("COPERNICUS/Landcover/100m/Proba-V-C3/Global")
lc_image = ee.Image(lc100_collection.sort('system:time_start', False).first())
# Codes relative to not valid land
excluded_values = [0, 40, 50, 70, 80, 111, 112, 113, 114, 115, 116]
ele=ee.ImageCollection("JAXA/ALOS/AW3D30/V4_1")       
        
# Iterate for islands
print(f"{len(gdf)} total islands")
problem_list = []
for k, (i, isl) in enumerate(gdf.iterrows(), 1):
    # Periodic exportation
    if k%100 == 0 or k == len(gdf):
        print(f"{k} islands made")
        print(f"Island area: {isl.IslandArea}")
    if k % 10 == 0:
        output_path = os.path.join(output_folder, "res_area.pkl")
        with open(output_path, "wb") as f:
            pickle.dump(res_area, f)
        output_path = os.path.join(output_folder, "ele_max.pkl")
        with open(output_path, "wb") as f:
            pickle.dump(ele_max, f)
    ID = isl.ALL_Uniq
    if ID not in res_area:
        try:
            # Simplify big geometries
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

            # Elevation intersecting images
            collection = ele.filterBounds(ee_geometry_original)
            # Completly contained island
            if collection.size().getInfo() == 1:
                # Image clip
                ele_clip = collection.first().clip(ee_geometry_original).select('DSM')
                # Max value
                max_value_dict = ele_clip.reduceRegion(
                    reducer = ee.Reducer.max(),
                    geometry = ee_geometry_original,
                    scale = ele_clip.projection().nominalScale(),
                    bestEffort = True,
                    maxPixels = 1e9
                ).get('DSM')
                e_max = max_value_dict.getInfo()
                # Dictionary update
                ele_max[ID] = e_max
                scale = ele_clip.projection().nominalScale().getInfo()
                ee_geometry = ee_geometry_original
                if e_max > 2000:
                    # Create mask, extract and subtract geometry from the roginal one
                    ele_mask = ele_clip.gt(2000)
                    vectors_ele = ele_mask.selfMask().reduceToVectors(
                        geometry = ele_mask.geometry(),
                        scale = scale,
                        crs = ele_mask.projection().crs(),
                        eightConnected = True,
                        bestEffort = True
                    )
                    ele_geometry = vectors_ele.union(ee.ErrorMargin(1)).geometry()
                    ee_geometry = ee_geometry.difference(ele_geometry)   
            # If more images same process iterated
            else:
                list = collection.toList(collection.size())
                ee_geometry = ee_geometry_original
                e_max = 0
                for j in range(collection.size().getInfo()):
                    img = ee.Image(list.get(j)).clip(ee_geometry_original).select('DSM')
                    max_value_dict = img.reduceRegion(
                        reducer = ee.Reducer.max(),
                        geometry = ee_geometry_original,
                        scale = img.projection().nominalScale(),
                        bestEffort = True,
                        maxPixels = 1e9
                    ).get('DSM')
                    e_max1 = max_value_dict.getInfo()
                    if e_max1 is not None:
                        if e_max1 > e_max:
                            e_max = e_max1
                        scale = img.projection().nominalScale().getInfo()
                        if e_max1 > 2000:
                            ele_mask = img.gt(2000)
                            vectors_ele = ele_mask.selfMask().reduceToVectors(
                                geometry = ele_mask.geometry(),
                                scale = scale,
                                crs = ele_mask.projection().crs(),
                                eightConnected = True,
                                bestEffort = True
                            )
                            ele_geometry = vectors_ele.union(ee.ErrorMargin(1)).geometry()
                            ee_geometry = ee_geometry.difference(ele_geometry)
                ele_max[ID] = e_max

            #Intersecting protected areas
            intersecting_wdpa = wdpa_polygons.filter(ee.Filter.intersects('.geo', ee_geometry_original))
            union_of_intersecting_wdpa = intersecting_wdpa.union()
            ee_geometry = ee_geometry.difference(union_of_intersecting_wdpa)
            # If remaining area too small, STOP
            area = ee_geometry.area().getInfo()
            if area < 20000:
                res_area[ID] = 0
                continue

            # Land occupation
            lc_clipped = lc_image.clip(ee_geometry)
            # Mask creation
            lc_mask = lc_clipped.select('discrete_classification').eq(excluded_values[0])
            scale = lc_mask.select('discrete_classification').projection().nominalScale().getInfo()
            for val in excluded_values[1:]:
                lc_mask = lc_mask.Or(lc_clipped.select('discrete_classification').eq(val))
            vectors = lc_mask.selfMask().reduceToVectors(
                geometry = lc_mask.geometry(),
                scale = scale,
                crs = lc_mask.projection().crs(),
                eightConnected = True,
                bestEffort = True
            )
            # Geometry extraction
            lc_geometry=vectors.union(ee.ErrorMargin(1)).geometry()
            # For big islands area subtraction, geometric difference too computationally expensive
            if isl.IslandArea > 2000:
                deleted_area = lc_geometry.area().getInfo()
                final_area = max(area-deleted_area, 0)
            # For other islands geometric subtraction
            else:
                ee_geometry = ee_geometry.difference(lc_geometry)
                final_area = ee_geometry.area().getInfo()
            # RES area too small
            if final_area < 20000:
                res_area[ID] = 0
                continue
            # Dictionary update
            res_area[ID] = min(((final_area/area0)*100),100)
        except Exception as e:
            problem_list.append(k)
            print(e)

#Repeat for problematic islands, the problem is in protected islands and their union
print(f'Problematic islands: {len(problem_list)}')
h = 0
for k, (i, isl) in enumerate(gdf.iterrows(), 1):
    if k in problem_list:
        ID = isl.ALL_Uniq
        if ID not in res_area:
            print(k)
            try:
                if isl.IslandArea > 10000:
                    geom = isl.geometry.simplify(tolerance = 0.005, preserve_topology = True)
                elif isl.IslandArea>5000:
                    geom = isl.geometry.simplify(tolerance = 0.003, preserve_topology = True)
                elif isl.IslandArea>2000:
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

                collection = ele.filterBounds(ee_geometry_original)
                if collection.size().getInfo() == 1:
                    ele_clip = collection.first().clip(ee_geometry_original).select('DSM')
                    max_value_dict = ele_clip.reduceRegion(
                        reducer = ee.Reducer.max(),
                        geometry = ee_geometry_original,
                        scale = ele_clip.projection().nominalScale(),
                        bestEffort = True,
                        maxPixels = 1e9
                    ).get('DSM')
                    e_max = max_value_dict.getInfo()
                    ele_max[ID] = e_max
                    scale = ele_clip.projection().nominalScale().getInfo()
                    ee_geometry = ee_geometry_original
                    if e_max > 2000:
                        ele_mask = ele_clip.gt(2000)
                        vectors_ele = ele_mask.selfMask().reduceToVectors(
                            geometry = ele_mask.geometry(),
                            scale = scale,
                            crs = ele_mask.projection().crs(),
                            eightConnected = True,
                            bestEffort = True
                        )
                        ele_geometry = vectors_ele.union(ee.ErrorMargin(1)).geometry()
                        ee_geometry = ee_geometry.difference(ele_geometry)   
                else:
                    list = collection.toList(collection.size())
                    ee_geometry = ee_geometry_original
                    e_max = 0
                    for j in range(collection.size().getInfo()):
                        img=ee.Image(list.get(j)).clip(ee_geometry_original).select('DSM')
                        max_value_dict = img.reduceRegion(
                            reducer = ee.Reducer.max(),
                            geometry = ee_geometry_original,
                            scale = img.projection().nominalScale(),
                            bestEffort = True,
                            maxPixels = 1e9
                        ).get('DSM')
                        e_max1 = max_value_dict.getInfo()
                        if e_max1 is not None:
                            if e_max1 > e_max:
                                e_max = e_max1
                            scale = img.projection().nominalScale().getInfo()
                            if e_max1 > 2000:
                                ele_mask = img.gt(2000)
                                vectors_ele = ele_mask.selfMask().reduceToVectors(
                                    geometry = ele_mask.geometry(),
                                    scale = scale,
                                    crs = ele_mask.projection().crs(),
                                    eightConnected = True,
                                    bestEffort = True
                                )
                                ele_geometry = vectors_ele.union(ee.ErrorMargin(1)).geometry()
                                ee_geometry = ee_geometry.difference(ele_geometry)
                    ele_max[ID] = e_max

                intersecting_wdpa = wdpa_polygons.filter(ee.Filter.intersects('.geo', ee_geometry_original))
                feature_list = intersecting_wdpa.toList(intersecting_wdpa.size().getInfo())
                for i in range(intersecting_wdpa.size().getInfo()):
                    geometry = ee.Feature(feature_list.get(i)).geometry()
                    ee_geometry = ee_geometry.difference(ee_geometry)
                area = ee_geometry.area().getInfo()
                if area < 20000:
                    res_area[ID] = 0
                    continue

                lc_clipped = lc_image.clip(ee_geometry)
                lc_mask = lc_clipped.select('discrete_classification').eq(excluded_values[0])
                scale = lc_mask.select('discrete_classification').projection().nominalScale().getInfo()
                for val in excluded_values[1:]:
                    lc_mask = lc_mask.Or(lc_clipped.select('discrete_classification').eq(val))
                vectors = lc_mask.selfMask().reduceToVectors(
                    geometry = lc_mask.geometry(),
                    scale = scale,
                    crs = lc_mask.projection().crs(),
                    eightConnected = True,
                    bestEffort = True
                )
                lc_geometry = vectors.union(ee.ErrorMargin(1)).geometry()
                if isl.IslandArea > 2000:
                    area_eliminabile = lc_geometry.area().getInfo()
                    area_finale = max(area-area_eliminabile,0)
                else:
                    ee_geometry = ee_geometry.difference(lc_geometry)
                    area_finale = ee_geometry.area().getInfo()
                if area_finale < 20000:
                    res_area[ID] = 0
                    continue
                res_area[ID] = min(((area_finale/area0)*100),100)
            
            except Exception as e:
                problem_list.append(k)
                print(e)
        h += 1
        print(f'{h} isole svolte')

# Expo
folder_out = os.path.join(project_folder, "data/final_data")
os.makedirs(folder_out, exist_ok=True)
percorso_file=os.path.join(folder_out, "res_area.pkl")
with open(percorso_file, "wb") as f:
    pickle.dump(res_area, f)
percorso_file=os.path.join(folder_out, "ele_max.pkl")
with open(percorso_file, "wb") as f:
    pickle.dump(ele_max, f)