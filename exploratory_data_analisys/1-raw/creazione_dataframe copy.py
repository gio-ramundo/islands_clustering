import pandas as pd
import os
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

current_folder = os.path.dirname(os.path.abspath(__file__))

# Dataframe load
folder_path = os.path.join(current_folder, "..")
csv_path = os.path.join(folder_path, "df_raw.csv")
df = pd.read_csv(csv_path)

print(df.columns)
df.drop(columns=['Densità_pop_etichetta', 'Solar_etichetta','Wind_class','NO_res'],inplace=True)
print(df.columns)

nuovi_nomi = {
    'Popolazione': 'population',
    'Densità_pop': 'density_pop',
    'eolico' : 'wind_power',
    'eolico_std' : 'wind_std',
    'offshore' : 'offshore_wind',
    'superficie_res' : 'res_area',
    'consumption_etichetta' : 'consumption_label'
}

df = df.rename(columns=nuovi_nomi)

#esportazione
output_folder = os.path.join(current_folder, '..')
output_path = os.path.join(output_folder, 'df_raw1.csv')
df.to_csv(output_path, index=False, encoding='utf-8')