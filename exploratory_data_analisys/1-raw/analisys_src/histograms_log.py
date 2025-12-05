import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

current_folder = os.path.dirname(os.path.abspath(__file__))
df_folder = os.path.join(current_folder, "..", "..")
csv_path = os.path.join(df_folder, 'df_raw.csv')
df = pd.read_csv(csv_path)
skewed_col = ['IslandArea', 'population', 'density_pop', 'wind_power', 'offshore_wind', 'gdp_2019', 'consumption', 'geothermal_potential', 'hydro', 'urban_area', 'urban_area_rel', 'ele_max']

out_folder = os.path.join(current_folder, "..", "results/histograms/logarithm")
os.makedirs(out_folder, exist_ok = True)
for col in df[skewed_col].select_dtypes(include = 'number').columns:
    out_path = os.path.join(out_folder, f"{col}_histogram.png")
    plt.figure(figsize = (10, 15))
    data = np.log(df[df[col] != 0][col])
    data.hist(bins = 60, color = 'skyblue', edgecolor = 'black')
    plt.title(f"{col} log histogram")
    plt.xlabel(col)
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

# Coloured histogram for variable consumption
labels = {'XS': 'red', 'S': 'green', 'M':'yellow', 'L': 'blue'}
out_path = os.path.join(out_folder, f"consumption_colour_histogram.png")
plt.figure(figsize = (10, 15))
df_log = df[['consumption', 'consumption_label']]
df_log = df_log[df_log['consumption'] != 0]
df_log['consumption'] = np.log(df_log['consumption'])
bin_width = (df_log['consumption'].max() - df_log['consumption'].min())/60
min_val = df_log['consumption'].min()
max_val = df_log['consumption'].max()
start_bin = np.floor(min_val / bin_width) * bin_width
end_bin = np.ceil(max_val / bin_width) * bin_width + bin_width
common_bins = np.arange(start_bin, end_bin, bin_width)
for label in labels:
    data = df_log[df_log['consumption_label'] == label]['consumption']
    if len(data) > 0:
        plt.hist(data, bins = common_bins, color = labels[label], label = label, edgecolor = 'black')
plt.title(f'Histogram of consumptions logarithm')
plt.xlabel('consumption')
plt.ylabel('Frequency')
plt.tight_layout()
plt.savefig(out_path)
plt.close()