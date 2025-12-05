import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import gridspec

current_folder = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_folder, 'results/dataframes/df_norm_cluster_label.csv')
df = pd.read_csv(csv_path)
columns = ['gdp_cons_pop_urban_merged', 'density_pop', 'solar_pow', 'wind_power', 'res_area', 'solar_seas_ind', 'wind_std', 'offshore_wind', 'evi', 'hydro', 'geothermal_potential', 'temp']

# Features' mean values heatmap in different cluster 
means = df.groupby(['cluster'])[columns].mean().reset_index()
means_norm = means.copy()
means_norm[columns] = means[columns].apply(
    lambda x: (x - x.min()) / (x.max() - x.min()), axis = 0
)
plt.figure(figsize=(10, 6))
sns.heatmap(means_norm[columns], cmap = "viridis", cbar = True)
plt.title("Heatmap mean values (normalized for features)")
plt.ylabel("Cluster")
plt.xlabel("Features")
plt.tight_layout()
# Expo
heatmap_path = os.path.join(current_folder, f'results/heatmap.png')
plt.savefig(heatmap_path)
plt.close()