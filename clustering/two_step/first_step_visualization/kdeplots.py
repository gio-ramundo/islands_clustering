import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..", "..")
csv_path = os.path.join(project_folder, "exploratory_data_analisys/df_norm.csv")
df = pd.read_csv(csv_path)
relevant_columns = ['solar_pow', 'solar_seas_ind', 'wind_power', 'wind_std', 'offshore_wind', 'evi', 'geothermal_potential', 'hydro', 'res_area', 'density_pop', 'temp', 'gdp_cons_pop_urban_merged']
zero_columns = ['offshore_wind', 'hydro', 'geothermal_potential']

output_folder = os.path.join(current_folder, "kdeplots_cluster")
os.makedirs(output_folder, exist_ok=True)

# Function that generates and export boxplots for different columns
def create_kdeplot(dataframe, label):
    cluster_output_folder = os.path.join(output_folder, f"cluster_{label}")
    os.makedirs(cluster_output_folder, exist_ok=True)
    output_folder1 = os.path.join(cluster_output_folder, "normal")
    os.makedirs(output_folder1, exist_ok=True)
    output_folder2 = os.path.join(cluster_output_folder, "no_zeros")
    os.makedirs(output_folder2, exist_ok=True)
    # Iterate for columns
    for col in relevant_columns:
        df_cluster = dataframe[dataframe['consumption_label'] == label]
        output_path = os.path.join(output_folder1, f"{col}_kdeplot.png")
        plt.figure(figsize=(10, 15))
        sns.kdeplot(df_cluster[col], shade=True, color="skyblue", fill=True)
        plt.title(f"{col} KDE-Plot")
        plt.xlabel('Values')
        plt.ylabel("Density")
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        # Columns with many zeros
        if col in zero_columns:
            df_no_zeros = df_cluster[df_cluster[col] != 0]
            output_path = os.path.join(output_folder2, f"{col}_kdeplot.png")
            plt.figure(figsize=(10, 15))
            sns.kdeplot(df_no_zeros[col], shade=True, color="green", fill=True)
            plt.title(f"{col} KDE-Plot")
            plt.xlabel('Values')
            plt.ylabel("Density")
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()

# Fuction application for different clusters
for i in ['XS', 'S', 'M', 'L']:
    create_kdeplot(df, i)