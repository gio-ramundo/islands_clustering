import geopandas as gp
import numpy as np
import pickle
import os

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..")

# Islands dataframe load, geometry column elimination
isl_path=os.path.join(project_folder, "data/filtered/final", "islands_4.gpkg")
gdf = gp.read_file(isl_path)
df = gdf.drop(columns = ['geometry'])
del gdf

# Dictionaries load function
pkl_folder = os.path.join(project_folder, "data/final_data")
def data_load(name):
    df[name] = float(0)
    file = name+'.pkl'
    pkl_path = os.path.join(pkl_folder, file)
    with open(pkl_path, 'rb') as file:
        return pickle.load(file)

# Function application    
evi = data_load('evi')
evi_nodata = data_load("evi_nodata")

wind_power = data_load("wind_power")
wind_nodata = data_load("wind_nodata")
wind_std = data_load("wind_std")
offshore_wind = data_load("offshore_wind")

gdp_2019 = data_load("gdp_2019")
gdp_2019_nodata = data_load("gdp_2019_nodata")
consumption = data_load("consumption")
cons_nodata = data_load("cons_nodata")

geothermal_potential = data_load("geothermal_potential")

hydro = data_load("hydro")

temp = data_load("temp")
temp_nodata = data_load("temp_nodata")
prec = data_load("prec")
prec_nodata = data_load("prec_nodata")
hdd = data_load("hdd")
hdd_nodata = data_load("hdd_nodata")
cdd = data_load("cdd")
cdd_nodata = data_load("cdd_nodata")

solar_pow = data_load("solar_pow")
solar_seas_ind = data_load("solar_seas_ind")
solar_nodata = data_load("solar_nodata")

urban_area = data_load("urban_area")
urban_area_rel = data_load("urban_area_rel")

res_area = data_load("res_area")
ele_max = data_load("ele_max")

# Dictionary to check nodata and NaN values
dict_check = {}
dict_check['evi'] = [0,0]
dict_check['wind'] = [0,0]
dict_check['gdp_2019'] = [0,0]
dict_check['consumption'] = [0,0]
dict_check['temp'] = [0,0]
dict_check['prec'] = [0,0]
dict_check['hdd'] = [0,0]
dict_check['cdd'] = [0,0]
dict_check['solar'] = [0,0]

#riempio le nuove colonne del dataframe
for i,isl in df.iterrows():
    ID = isl.ALL_Uniq
    df.loc[i,'evi'] = evi[ID]
    df.loc[i,'evi_nodata'] = evi_nodata[ID]
    if np.isnan(evi[ID]) and evi_nodata[ID] == 0:
        dict_check['evi'][0] += 1
    if (not np.isnan(evi[ID])) and evi_nodata[ID] == 1:
        dict_check['evi'][1] += 1
    df.loc[i,'wind_power'] = wind_power[ID]
    df.loc[i,'wind_nodata'] = wind_nodata[ID]
    if np.isnan(wind_power[ID]) and wind_nodata[ID] == 0:
        dict_check['wind'][0] += 1
    if (not np.isnan(wind_power[ID])) and wind_nodata[ID] == 1:
        dict_check['wind'][1] += 1
    df.loc[i,'wind_std'] = wind_std[ID]
    df.loc[i,'offshore_wind'] = offshore_wind[ID]
    df.loc[i,'gdp_2019'] = gdp_2019[ID]
    df.loc[i,'gdp_2019_nodata'] = gdp_2019_nodata[ID]
    if np.isnan(gdp_2019[ID]) and gdp_2019_nodata[ID] == 0:
        dict_check['gdp_2019'][0] += 1
    if (not np.isnan(gdp_2019[ID])) and gdp_2019_nodata[ID] == 1:
        dict_check['gdp_2019'][1] += 1
    df.loc[i,'consumption'] = consumption[ID]
    df.loc[i,'cons_nodata'] = cons_nodata[ID]
    if np.isnan(consumption[ID]) and cons_nodata[ID] == 0:
        dict_check['consumption'][0] += 1
    if (not np.isnan(consumption[ID])) and cons_nodata[ID] == 1:
        dict_check['consumption'][1] += 1
    df.loc[i,'geothermal_potential'] = geothermal_potential[ID]
    df.loc[i,'hydro'] = hydro[ID]
    df.loc[i,'temp'] = temp[ID]
    df.loc[i,'temp_nodata'] = temp_nodata[ID]
    if np.isnan(temp[ID]) and temp_nodata[ID] == 0:
        dict_check['temp'][0] += 1
    if (not np.isnan(temp[ID])) and temp_nodata[ID] == 1:
        dict_check['temp'][1] += 1
    df.loc[i,'prec'] = prec[ID]
    df.loc[i,'prec_nodata'] = prec_nodata[ID]
    if np.isnan(prec[ID]) and prec_nodata[ID] == 0:
        dict_check['prec'][0] += 1
    if (not np.isnan(prec[ID])) and prec_nodata[ID] == 1:
        dict_check['prec'][1] += 1
    df.loc[i,'hdd'] = hdd[ID]
    df.loc[i,'hdd_nodata'] = hdd_nodata[ID]
    if np.isnan(hdd[ID]) and hdd_nodata[ID] == 0:
        dict_check['hdd'][0] += 1
    if (not np.isnan(hdd[ID])) and hdd_nodata[ID] == 1:
        dict_check['hdd'][1] += 1
    df.loc[i,'cdd'] = cdd[ID]
    df.loc[i,'cdd_nodata'] = cdd_nodata[ID]
    if np.isnan(cdd[ID]) and cdd_nodata[ID] == 0:
        dict_check['cdd'][0] += 1
    if (not np.isnan(cdd[ID])) and cdd_nodata[ID] == 1:
        dict_check['cdd'][1] += 1
    df.loc[i,'solar_pow'] = solar_pow[ID]
    df.loc[i,'solar_seas_ind'] = solar_seas_ind[ID]
    df.loc[i,'solar_nodata'] = solar_nodata[ID]
    if np.isnan(solar_pow[ID]) and solar_nodata[ID] == 0:
        dict_check['solar'] += 1
    if (not np.isnan(solar_pow[ID])) and solar_nodata[ID] == 1:
        dict_check['solar'] += 1
    df.loc[i,'urban_area'] = urban_area[ID]
    df.loc[i,'urban_area_rel'] = urban_area_rel[ID]
    df.loc[i,'res_area'] = res_area[ID]
    df.loc[i,'ele_max'] = ele_max[ID]
print(dict_check)

# Create a copy for exportation and drop nodata columns
df1 = df.drop(columns = ['evi_nodata', 'eolico_nodata',  'cons_nodata', 'gdp_2019_nodata', 'temp_nodata', 'prec_nodata', 'hdd_nodata', 'cdd_nodata', 'solar_nodata'])

# Dataframe with NaN values exportation 
output_folder = os.path.join(current_folder, '..')
output_path = os.path.join(output_folder, 'df_raw_toal.csv')
df1.to_csv(output_path, index=False, encoding='utf-8')

# Drop not useful to clustering column
df=df.drop(columns = ['Shape_Leng'])

# Delete not complete rows
print(f"Total islands: {len(df)}")
df=df.dropna()
df = df.reset_index(drop=True)
print(f"Complete data islands: {len(df)}")
print(' ')

# 2 islands with gdp and consumption value not nan but nodata value 1, check if not already deleted
indexes = df[df['gdp_2019_nodata'] == 1].index
df = df.drop(indexes)
indexes = df[df['consumption'] == 1].index
df = df.drop(indexes)
print(f"Complete data islands: {len(df)}")
print(' ')
# Drop nodata columns, not useful anymore
df = df.drop(columns = ['evi_nodata', 'eolico_nodata',  'cons_nodata', 'gdp_2019_nodata', 'temp_nodata', 'prec_nodata', 'hdd_nodata', 'cdd_nodata', 'solar_nodata'])

# Fuction to create class labels
def labelling(value, thresholds, labels):
    if value < thresholds[0]:
        return labels[0]
    for i in range(len(thresholds) - 1):
        if thresholds[i] <= value < thresholds[i+1]:
            return labels[i+1]
    if value >= thresholds[-1]:
        return labels[-1]

# Electric consumption label
consumption_thresholds =[2, 15, 100]
consumption_thresholds  = [x * 10**6 for x in consumption_thresholds ] # kWh to GWh
consumption_labels =['XS','S','M','L']
df['consumption_label'] = df['consumption'].apply(labelling, args=(consumption_thresholds, consumption_labels ))
for label in consumption_labels :
    length = len(df[(df['consumption_label'] == label)])
    print(f'There are {length} islands with consumption label {label}')

# Expo
output_folder = os.path.join(current_folder, '..')
output_path = os.path.join(output_folder, 'df_raw.csv')
df.to_csv(output_path, index=False, encoding='utf-8')