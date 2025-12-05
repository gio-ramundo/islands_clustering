import os
import pandas as pd
from sklearn.cluster import KMeans

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..")
csv_path = os.path.join(project_folder, "exploratory_data_analisys/df_norm.csv")
df = pd.read_csv(csv_path)
df['cluster'] = -1

# Possible columns for clustering
columns = ['gdp_cons_pop_urban_merged', 'density_pop', 'solar_pow', 'wind_power', 'res_area', 'solar_seas_ind', 'wind_std', 'offshore_wind', 'evi', 'temp', 'hydro', 'geothermal_potential']
kmeans = KMeans(n_clusters = 3, init = 'k-means++', max_iter = 500, n_init = 10, random_state = 42)
kmeans.fit(df[columns])
df['cluster'] = kmeans.labels_

# DF exportation
output_folder = os.path.join(current_folder, 'results/dataframes')
os.makedirs(output_folder, exist_ok = True)
output_path = os.path.join(output_folder, 'df_norm_cluster_label.csv')
df.to_csv(output_path, index=False, encoding='utf-8')

# Cluster column addiction on raw dataframe
csv_path = os.path.join(project_folder, "exploratory_data_analisys/df_raw.csv")
df1 = pd.read_csv(csv_path)
df1['cluster'] = df['cluster']
output_folder = os.path.join(current_folder, 'results/dataframes')
output_path = os.path.join(output_folder, 'df_raw_cluster_label.csv')
df1.to_csv(output_path, index=False, encoding='utf-8')