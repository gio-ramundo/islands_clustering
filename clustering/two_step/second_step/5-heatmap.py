import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import gridspec

current_folder = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_folder, 'results/dataframes/df_norm_final.csv')
df = pd.read_csv(csv_path)
columns = ['density_pop', 'solar_pow', 'wind_power', 'temp', 'res_area', 'solar_seas_ind', 'wind_std', 'offshore_wind', 'evi', 'hydro', 'geothermal_potential']

# Heatmaps of features' mean values in different cluster 
means = df.groupby(['consumption_label', 'final_cluster'])[columns].mean().reset_index()
means_norm = means.copy()
means_norm[columns] = means[columns].apply(
    lambda x: (x - x.min()) / (x.max() - x.min()), axis = 0
)
# Iterate for first level cluster
for label in ['XS', 'S', 'M', 'L']:
    subset = means_norm[means_norm['consumption_label'] == label]
    subset = subset.set_index('final_cluster')[columns]
    plt.figure(figsize = (10, 6))
    sns.heatmap(subset, vmin = 0, vmax = 1, cmap = "viridis", cbar = True)
    plt.tight_layout()
    # Expo
    output_path = os.path.join(current_folder, 'results/heatmap')
    os.makedirs(output_path, exist_ok = True)
    heatmap_path = os.path.join(output_path, f'heatmap_cluster_{label}.png')
    plt.savefig(heatmap_path)
    plt.close()

# Overall heatmap
grouped = df[['gdp_cons_pop_urban_merged'] + columns + ['consumption_label', 'final_cluster']].groupby(["consumption_label", "final_cluster"]).mean()
ordered = grouped.sort_index(level = [0,1])
ordered_norm = ordered.copy()
ordered_norm[['gdp_cons_pop_urban_merged'] + columns] = ordered[['gdp_cons_pop_urban_merged'] + columns].apply(
    lambda x: (x - x.min()) / (x.max() - x.min()), axis = 0
)
fig = plt.figure(figsize=(20, 28))
# Two levels dendrogram
gs = gridspec.GridSpec(1, 2, width_ratios = [1, 4], wspace = 0.05)
ax_tree = plt.subplot(gs[0])
ax_tree.set_xlim(0, 1)
ax_tree.set_ylim(0, len(ordered))
y_ticks = []
labels = []
y_pos = 0
# Iterate for first level cluster
for lvl1, subdf in ordered.groupby(level = 0):
    n_sub = len(subdf)
    mid = y_pos + n_sub/2
    # First level branch
    ax_tree.plot([0.7, 0.4], [mid, mid], color = "black")
    ax_tree.text(0.2, mid, f"{lvl1}", va = "center", ha = "right", fontsize = 24)
    # Iterate for subcluster
    for lvl2 in subdf.index.get_level_values(1):
        leaf_y = y_pos + 0.5
        # Second level branch
        ax_tree.plot([0.7, 0.7], [mid, leaf_y], color = "black")
        ax_tree.plot([0.7, 1], [leaf_y, leaf_y], color = "black")
        labels.append(f"{lvl1}.{lvl2}")
        y_ticks.append(leaf_y)
        y_pos += 1
ax_tree.set_xticks([])
ax_tree.set_yticks([])
ax_tree.invert_yaxis()
ax_tree.set_yticklabels(ax_tree.get_yticklabels(), fontsize=30)
ax_tree.text(
    -0.2,
    len(ordered_norm)/2,
    "Cluster",
    va="center", ha="center", 
    rotation=90,
    fontsize=30
)
# Heatmap
ax_heat = plt.subplot(gs[1])
sns.heatmap(
    ordered_norm,
    cmap = "viridis",
    cbar = True,
    ax = ax_heat,
    yticklabels = [f"{i[0]}.{i[1]}" for i in ordered.index]
)
ax_heat.set_ylabel("")
ax_heat.set_xlabel("Features", fontsize=30)
ax_heat.set_xticklabels(ax_heat.get_xticklabels(), fontsize=18, rotation=35, ha="right")
ax_heat.set_yticklabels(ax_heat.get_yticklabels(), fontsize=18)

# Expo
output_path = os.path.join(current_folder, 'results/heatmap')
heatmap_path = os.path.join(output_path, f'overall_heatmap_with_dendogram.png')
plt.savefig(heatmap_path)
plt.close()