import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

current_folder = os.path.dirname(os.path.abspath(__file__))

df_folder = os.path.join(current_folder, "..", "..")
csv_path = os.path.join(df_folder, 'df_raw.csv')
df = pd.read_csv(csv_path)
skewed_col = ['IslandArea', 'population', 'density_pop', 'wind_power', 'offshore_wind', 'gdp_2019', 'consumption', 'geothermal_potential', 'hydro', 'urban_area', 'urban_area_rel', 'ele_max']

out_folder = os.path.join(current_folder, "..", "results/kde_plots/logarithm")
os.makedirs(out_folder, exist_ok = True)
for col in df[skewed_col].select_dtypes(include = 'number').columns:
    output_path = os.path.join(out_folder, f"{col}_kdeplot.png")
    plt.figure(figsize = (10, 15))
    data=np.log(df[df[col] != 0][col])
    sns.kdeplot(data, shade = True, color = "skyblue",fill = True)
    plt.title(f"{col} KDE Plot")
    plt.xlabel(col)
    plt.ylabel("Density")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()