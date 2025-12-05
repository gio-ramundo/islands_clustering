import pandas as pd
import pickle
import os
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

current_folder = os.path.dirname(os.path.abspath(__file__))
csv_folder = os.path.join(current_folder, "..")
csv_path = os.path.join(csv_folder, "df_raw.csv")
df = pd.read_csv(csv_path)

# Correlated variables
X=df[['gdp_2019', 'population', 'urban_area', 'consumption']]
X_scaled = StandardScaler().fit_transform(X)
pca = PCA(n_components=1)
X_pca = pca.fit_transform(X_scaled)
print(f'Variance explained by the first component {pca.explained_variance_ratio_}')
df['gdp_cons_pop_urban_merged']=X_pca
# Variance explained by the first component [0.79485721]

# Variable merging
df['res_area']=(df['res_area']/100)*df['IslandArea']

# Not relevant variables
df=df.drop(columns=['hdd', 'cdd', 'prec', 'ele_max', 'gdp_2019', 'consumption', 'population', 'urban_area', 'urban_area_rel', 'IslandArea'])

# Expo
out_folder = os.path.join(current_folder, '..')
os.makedirs(out_folder, exist_ok=True)
output_path = os.path.join(out_folder, 'df_dim_reduction.csv')
df.to_csv(output_path, index=False, encoding='utf-8')