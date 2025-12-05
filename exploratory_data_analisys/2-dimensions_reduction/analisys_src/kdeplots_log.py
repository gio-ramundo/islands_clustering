import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

current_folder = os.path.dirname(os.path.abspath(__file__))

df_folder = os.path.join(current_folder, "..", "..")
csv_path = os.path.join(df_folder, 'df_dim_reduction.csv')
df = pd.read_csv(csv_path)
skewed_col = ['res_area', 'density_pop', 'wind_power', 'offshore_wind', 'geothermal_potential', 'gdp_cons_pop_urban_merged', 'hydro']

out_folder = os.path.join(current_folder, "..", "results/kde_plots/logarithm")
os.makedirs(out_folder, exist_ok = True)
for col in df[skewed_col].select_dtypes(include = 'number').columns:
    output_path = os.path.join(out_folder, f"{col}_kdeplot.png")
    plt.figure(figsize = (10, 15))
    min = df[col].min()
    data = np.log1p(df[col]-min)
    # Variables with many zeros
    if col == 'geothermal_potential' or col == 'offshore_wind' or col == 'hydro':
        data = np.log1p(df[df[col] > 0][col])
    sns.kdeplot(data, shade = True, color = "skyblue", fill = True)
    plt.title(f"KDE Plot di {col}")
    plt.xlabel(col)
    plt.ylabel("Density")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()