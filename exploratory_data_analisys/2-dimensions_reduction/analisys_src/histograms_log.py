import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

current_folder = os.path.dirname(os.path.abspath(__file__))
df_folder = os.path.join(current_folder, "..", "..")
csv_path = os.path.join(df_folder, 'df_dim_reduction.csv')
df = pd.read_csv(csv_path)
skewed_col = ['density_pop', 'res_area', 'offshore_wind', 'geothermal_potential', 'gdp_cons_pop_urban_merged', 'hydro', 'wind_power']

out_folder = os.path.join(current_folder, "..", "results/histograms/logarithm")
os.makedirs(out_folder, exist_ok = True)
for col in df[skewed_col].select_dtypes(include = 'number').columns:
    out_path = os.path.join(out_folder, f"{col}_histogram.png")
    plt.figure(figsize = (10, 15))
    min = df[col].min()
    data = np.log1p(df[col]-min)
    # Variables with many zeros
    if col == 'geothermal_potential' or col == 'offshore_wind' or col == 'hydro':
        data=np.log1p(df[df[col] > 0][col])
    data.hist(bins = 60, color = 'skyblue', edgecolor = 'black')
    plt.title(f"{col} log histogram")
    plt.xlabel(col)
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()