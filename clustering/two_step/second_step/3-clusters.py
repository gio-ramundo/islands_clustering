import os
import pandas as pd
from sklearn.cluster import KMeans

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..", "..")
csv_path = os.path.join(project_folder, "exploratory_data_analisys/df_norm.csv")
df = pd.read_csv(csv_path)
df['final_cluster'] = -1

# Possible columns for clustering
columns = [['solar_pow', 'wind_power', 'res_area', 'solar_seas_ind', 'wind_std', 'offshore_wind', 'evi'],
    ['solar_pow', 'wind_power', 'res_area', 'solar_seas_ind', 'wind_std', 'offshore_wind', 'evi', 'hydro'],
    ['solar_pow', 'wind_power', 'res_area', 'solar_seas_ind', 'wind_std', 'offshore_wind', 'evi', 'hydro', 'geothermal_potential']
]

# KMeans hyperparameter for different cluster
hyperparam = {
    'XS' : [3, 2],
    'S' : [2, 0],
    'M' : [3, 0],
    'L' : [3, 1]
}

# Iterate for different first cluster
for clust, hyper in hyperparam.items():
    print(f'cluster {clust}')
    df1 = df[df['consumption_label'] == clust].copy()
    kmeans = KMeans(n_clusters = hyper[0], init = 'k-means++', max_iter = 300, n_init = 10, random_state = 42)
    kmeans.fit(df1[columns[hyper[1]]])
    df1['final_cluster'] = kmeans.labels_
    for i,isl in df1.iterrows():
        df.loc[i, 'final_cluster'] = df1.loc[i, 'final_cluster']

# New column with univocal clsuter code
df["cluster_id"] = df["consumption_label"] + "." + df["final_cluster"].astype(str)

# DF exportation
output_folder = os.path.join(current_folder, 'results/dataframes')
os.makedirs(output_folder, exist_ok = True)
output_path = os.path.join(output_folder, 'df_norm_final.csv')
df.to_csv(output_path, index=False, encoding='utf-8')

# Cluster columns addiction on raw dataframe
csv_path = os.path.join(project_folder, "exploratory_data_analisys/df_raw.csv")
df1 = pd.read_csv(csv_path)
df1['final_cluster'] = df['final_cluster']
output_folder = os.path.join(current_folder, 'results/dataframes')
output_path = os.path.join(output_folder, 'df_raw_final.csv')
df1.to_csv(output_path, index=False, encoding='utf-8')