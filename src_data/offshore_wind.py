import geopandas as gp
import numpy as np
import os
import pickle
from rtree import index
from shapely.geometry import Polygon, MultiPolygon
import utm
from affine import Affine
import rasterio
from rasterio.features import rasterize

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..")

# SETUP
isl_path=os.path.join(project_folder, "data/filtered/final", "islands_buffer.gpkg")
gdf = gp.read_file(isl_path)
percorso_pkl=os.path.join(project_folder, "data/filtered", "nations.pkl")
with open(percorso_pkl, 'rb') as file:
    islands_nation = pickle.load(file)
# Countries with different notations
translate = {
    'Republic of Korea': 'South Korea',
    "Dem People's Rep of Korea" : "North Korea",
    "Viet Nam" : "Vietnam",
    "Kuril islands" : "Russia",
    "Russian Federation" : "Russia",
    "U.K. of Great Britain and Northern Ireland" : "United Kingdom",
    "Svalbard and Jan Mayen Islands" : "Svalbard",
    "Faroe Islands" : "Denmark",
    "Isle of Man" : "United Kingdom",
    "Jersey" : "United Kingdom",
    "Guernsey" : "United Kingdom",
    "Turks and Caicos islands" : "United Kingdom",
    "Btates Virgin Islands" : "United Kingdom",
    "United States Virgin Islands" : "United States",
    "United States of America" : "United States",
    'Guadeloupe' : "France",
    "Anguilla" : "United Kingdom",
    "Netherlands Antilles" : "Netherlands",
    "Aruba" : "Netherlands",
    "Montserrat" : "United Kingdom",
    "Saint Pierre et Miquelon" : "France",
    "Somalia" : "Federal Republic of Somalia",
    "Mauritius" : "Republic of Mauritius",
    "Northern Mariana Islands" : "United States",
    "Guam" : "United States",
    "Azores Islands" : "Azores"
    }

# Functions to reproject geometries and calculate areas
def reproject(geom, utm_crs=0):
    # UTM identification
    if utm_crs==0:
        lon, lat = geom.centroid.x, geom.centroid.y
        utm_zone = utm.from_latlon(lat, lon)
        utm_crs = f"EPSG:{32600 + utm_zone[2]}"
    gf = gp.GeoDataFrame(geometry = [geom], crs = "EPSG:4326")
    gf = gf.to_crs(utm_crs)
    return gf.iloc[0]['geometry'], utm_crs
def compute_area(geom):
    gf = gp.GeoDataFrame(geometry = [geom])
    return gf.area.iloc[0]

offshore = {element: 0 for element in list(gdf.ALL_Uniq)}

# Function to apply to every shapefile, shapefile name is the input
def function(name):
    print(f'Analizing file: {name}')
    # Shapefile load
    path = os.path.join(project_folder, "files\offshore", name)
    gdf1 = gp.read_file(path)
    # Filter
    gdf1 = gdf1[(gdf1['InstallCap']>0.001)]
    # List for associated islands
    gdf1["associated_islands"] = [[] for _ in range(len(gdf1))]

    # Shape crossed by first or last meridian, duplicated from both sides to avoid conflict
    if name == "eap\FloatingFoundation.shp":
        prob_index = [5271,6073,6124,6137,6405]
        for i in prob_index:
            shape = gdf1.loc[i,'geometry']
            # Polygons
            if type(shape) == Polygon:
                point_list1 = list(shape.exterior.coords)
                point_list2 = list(shape.exterior.coords)
                for h in range(len(point_list1)):
                    if point_list1[h][0] > 0:
                        point_list1[h] = (point_list1[h][0]-360, point_list1[h][1])
                    else:
                        point_list2[h] = (point_list2[h][0]+360, point_list2[h][1])
                poli1 = Polygon(point_list1)
                poli2 = Polygon(point_list2)
                gdf1.loc[i,'geometry'] = MultiPolygon([poli1,poli2])
            # Multipolygons
            if type(shape) == MultiPolygon:
                poly_list = list(shape.geoms)
                for k in range(len(poly_list)):
                    if poly_list[k].bounds[0]*poly_list[k].bounds[2] < 0:
                        point_list1 = list(poly_list[k].exterior.coords)
                        point_list2 = list(poly_list[k].exterior.coords)
                        for h in range(len(point_list1)):
                            if point_list1[h][0] < 0:
                                point_list1[h] = (point_list1[h][0]+360,point_list1[h][1])
                            else:
                                point_list2[h] = (point_list2[h][0]-360,point_list2[h][1])
                        poly_list[k] = Polygon(point_list1)
                        poly_list.append(Polygon(point_list2))
                gdf1.loc[i,'geometry'] = MultiPolygon(poly_list)
    # Degradeted geometries
    if name == r"na\FloatingFoundation.shp":
        prob_index =[176,180]
        for i in prob_index :
            gdf1.drop(index=i, inplace=True)
                    
    # Index object to facilitate iterations
    idx = index.Index()
    for i, row in gdf1.iterrows():
        bbox = row.geometry.bounds
        idx.insert(i, bbox)
    # Iterate to find intersecting islands
    for i,isl in gdf.iterrows():
        ID = isl.ALL_Uniq
        multi = isl.geometry
        bbox_isl = multi.bounds
        potential_zones = list(idx.intersection(bbox_isl))
        for h in potential_zones:
            shape = gdf1.loc[h]
            # To avoid invalid geometries
            geom_shape = shape.geometry.buffer(0)
            if multi.intersects(geom_shape):
                a = False
                # Associate island and shape only if there is a common nation
                for country in islands_nation[ID]:
                    # Translation if necessary
                    if country in translate:
                        country = translate[country]
                    # Different notations for two files
                    if name == r"na\FloatingFoundation.shp" or name == "sa\FloatingFoundation.shp":
                        if country == shape.TERRITORY1 or country == shape.SOVEREIGN1:
                            a = True
                        if shape.TERRITORY1==None or shape.SOVEREIGN1==None:
                            a = True
                    else:
                        if country == shape.Territory1 or country == shape.Sovereign1:
                            a = True
                        if shape.Territory1==None or shape.Sovereign1==None:
                            a = True
                if a:
                    # ASSOCIATION
                    gdf1.loc[h,'associated_islands'].append(i)
    
    # Delete shapes with no association
    gdf1 = gdf1[gdf1['associated_islands'].apply(lambda x: len(x) > 0)]
    # Iterate for shapes
    print(f'Shapes to analyze: {len(gdf1)}')
    for cont,(j,shape) in enumerate(gdf1.iterrows(),1):
        if cont%1000 == 0 or cont == len(gdf1):
            print(f'Shapes analyzed: {cont}')
        isl_indexes = shape.associated_islands
        # Shape area
        shape_ripro,crs = reproject(shape.geometry)
        shape_ripro = shape_ripro.buffer(0)
        shape_area = compute_area(shape_ripro)
        # Union of reprojected geometries of intersecting islands
        isl_union = reproject(gdf.loc[isl_indexes[0],'geometry'],crs)[0]
        if len(isl_indexes) > 1:
            for h in range(1,len(isl_indexes)):
                isl_union = isl_union.union(reproject(gdf.loc[isl_indexes[h],'geometry'],crs)[0])
        isl_union = isl_union.buffer(0)
        # Intersection with offshore shape
        isl_union = isl_union.intersection(shape_ripro)
        union_area = compute_area(isl_union)
        # If too small, ignore
        if union_area < 1000:
            continue
        # Power installable proposrtional to intersecting area
        tot_pow = shape.InstallCap*(union_area/shape_area)
        # Power repartition
        if len(isl_indexes) == 1:
            ID = gdf.loc[isl_indexes[0],'ALL_Uniq']
            offshore[ID] += tot_pow
        elif len(isl_indexes) == 2:
            isl1 = reproject(gdf.loc[isl_indexes[0],'geometry'])[0].intersection(shape_ripro)
            isl2 = reproject(gdf.loc[isl_indexes[1],'geometry'])[0].intersection(shape_ripro)
            inte = isl1.intersection(isl2)
            ID1 = gdf.loc[isl_indexes[0],'ALL_Uniq']
            ID2 = gdf.loc[isl_indexes[1],'ALL_Uniq']
            ratio1 = (compute_area(isl1)-(compute_area(inte)/2))/union_area
            ratio2 = (compute_area(isl2)-(compute_area(inte)/2))/union_area
            offshore[ID1] += tot_pow*ratio1
            offshore[ID2] += tot_pow*ratio2
        else:
            # Raster to count shared pixels
            minx, miny, maxx, maxy = isl_union.bounds
            resolution = 50
            width = max(int((maxx - minx) / resolution),1)
            height = max(int((maxy - miny) / resolution),1)
            transform = Affine.translation(minx, miny) * Affine.scale(resolution, resolution)
            # Initialize mask
            counts = np.zeros((height, width), dtype=np.uint8)
            # Iterate for intersecting islands
            for ind in range(len(isl_indexes)):
                island = reproject(gdf.loc[isl_indexes[ind],'geometry'], crs)[0].intersection(shape_ripro)
                if (compute_area(island)) > 0:
                    mask = rasterize(
                        [(island, 1)],
                        out_shape = (height, width),
                        transform = transform,
                        fill = 0,
                        all_touched = True,
                        dtype = np.uint8
                    )
                    counts += mask
            # New raster, inverse of the other one
            result = np.zeros_like(counts, dtype=np.float32)
            mask = counts > 0
            result[mask] = 1.0 / counts[mask]
            total_pixels = np.count_nonzero(result)
            if total_pixels > 0:
                for ind in range(len(isl_indexes)):
                    island = reproject(gdf.loc[isl_indexes[ind],'geometry'],crs)[0]
                    ID = gdf.loc[isl_indexes[ind],'ALL_Uniq']
                    # Island mask sum
                    island_mask = rasterize(
                        [(island, 1)],
                        out_shape = (height, width),
                        transform = transform,
                        fill = 0,
                        all_touched = True,
                        dtype = np.uint8
                    )
                    island_values = result[island_mask > 0]
                    isl_pixels = np.sum(island_values)
                    ratio = isl_pixels/total_pixels
                    offshore[ID] += tot_pow*ratio

shape_files=["eap\FixedFoundation.shp",
            "eap\FloatingFoundation.shp",          
            "eca\FixedFoundation.shp",
            "eca\FloatingFoundation.shp",
            "lac\FixedFoundation.shp",
            "lac\FloatingFoundation.shp",
            "mena\FixedFoundation.shp",
            "mena\FloatingFoundation.shp",
            r"na\FixedFoundation.shp",
            r"na\FloatingFoundation.shp",
            "sa\FixedFoundation.shp",
            "sa\FloatingFoundation.shp",
            "ssa\FixedFoundation.shp",
            "ssa\FloatingFoundation.shp"
            ]
for str in shape_files:
    function(str)

# Expo
folder_out = os.path.join(project_folder, "data/final_data")
os.makedirs(folder_out, exist_ok=True)
percorso_file=os.path.join(folder_out, "offshore_wind.pkl")
with open(percorso_file, "wb") as f:
    pickle.dump(offshore, f)