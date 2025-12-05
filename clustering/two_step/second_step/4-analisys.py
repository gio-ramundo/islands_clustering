import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from matplotlib.colors import ListedColormap

current_folder = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_folder, 'results/dataframes/df_norm_final.csv')
df = pd.read_csv(csv_path)
columns = ['density_pop', 'solar_pow', 'wind_power', 'temp', 'res_area', 'solar_seas_ind', 'wind_std', 'offshore_wind', 'evi', 'hydro', 'geothermal_potential', 'gdp_cons_pop_urban_merged']
output_folder = os.path.join(current_folder, f'results')
os.makedirs(output_folder, exist_ok = True)

# Iterate for first step cluster and create a .txt file with descriptive stats
txt_folder = os.path.join(output_folder, 'txt_folder')
os.makedirs(txt_folder, exist_ok = True)
for label in ['XS', 'S', 'M', 'L']:
    df1 = df[df['consumption_label'] == label].copy()
    clust_second = df1['final_cluster'].max() + 1
    txt_path = os.path.join(txt_folder, f'cluster_{label}.txt')
    with open(txt_path, 'w') as file:
        l = len(df1)
        file.write(f'Islands in the cluster: {l}\n')
        l = len(df1[df1['hydro'] > 0])
        file.write(f'Islands with hydro potential: {l}\n')
        l = len(df1[df1['geothermal_potential'] > 0])
        file.write(f'Islands with geothermal potential: {l}\n')
        l = len(df1[df1['offshore_wind'] > 0])
        file.write(f'Islands with offshore wind potential: {l}\n')
        file.write('\n')
        for j in range(clust_second):
            df2 = df1[df1['final_cluster'] == j].copy()
            l = len(df2)
            file.write(f'Islands in the subcluster {j}: {l}\n')
            l = len(df2[df2['hydro'] > 0])
            file.write(f'Islands in the subcluster with hydro potential: {l}\n')
            l = len(df2[df2['geothermal_potential'] > 0])
            file.write(f'Islands in the subcluster with geothermal potential: {l}\n')
            l = len(df2[df2['offshore_wind'] > 0])
            file.write(f'Islands in the subcluster with offshore wind potential: {l}\n')
            file.write('\n')
        # Compute variance explained by clustering process
        X = df1[columns]
        grand_mean = X.mean()
        SST = ((X - grand_mean) ** 2).to_numpy().sum()
        SSB = 0
        for cluster, group in df1[columns + ['final_cluster']].groupby('final_cluster'):
            n_k = len(group)
            cluster_mean = group.drop(columns=['final_cluster']).mean()
            SSB += n_k * ((cluster_mean - grand_mean) ** 2).to_numpy().sum()
        R2 = SSB / SST
        file.write(f'Cluster variance ratio explained by subclusters: {R2}')

# Boxplots
boxplot_folder = os.path.join(output_folder, 'boxplot')
os.makedirs(boxplot_folder, exist_ok = True)
# Function to create and export boxplots
def box(dataframe, folder_name): # Folder name to differentiate raw and normalized data
    boxplot_folder1 = os.path.join(boxplot_folder, folder_name)
    os.makedirs(boxplot_folder1, exist_ok = True)
    # Iterate for first step clusters
    for label in ['XS', 'S', 'M', 'L']:
        df1 = dataframe[dataframe['consumption_label'] == label].copy()
        clust_second = df1['final_cluster'].max() + 1
        boxplot_folder2 = os.path.join(boxplot_folder1, f'cluster_{label}')
        os.makedirs(boxplot_folder2, exist_ok = True)
        # Feature iterations
        for feature in columns:
            plt.figure(figsize=(8, 6))
            data = [df1[df1['final_cluster'] == cluster_label][feature] for cluster_label in range(clust_second)]
            plt.boxplot(data, vert = True, patch_artist = True)
            plt.xticks(ticks = range(1, clust_second + 1), labels = [f'Cluster {cluster_label}' for cluster_label in range(clust_second)])
            plt.tight_layout()
            boxplot_path = os.path.join(boxplot_folder2, f'{feature}_boxplot.png')
            plt.savefig(boxplot_path)
            plt.close()
box(df, 'normalized')

# Descriptove stats
stat_folder = os.path.join(output_folder, 'descriptive_stat')
os.makedirs(stat_folder, exist_ok = True)
def stat(dataframe, folder_name):
    stat_folder1 = os.path.join(stat_folder, folder_name)
    os.makedirs(stat_folder1, exist_ok = True)
    for label in ['XS', 'S', 'M', 'L']:
        df1 = dataframe[dataframe['consumption_label']==label].copy()
        # .xlsx file with descriptove stats, every sheet is referred to a feature
        output_xlsx = os.path.join(stat_folder1, f'statistics_cluster_{label}.xlsx')
        with pd.ExcelWriter(output_xlsx, engine='xlsxwriter') as writer:
            for feature in columns:
                stats = []
                clust_second = df1['final_cluster'].max() + 1
                for cluster_label in range(clust_second):
                    df_feature= df1[df1['final_cluster'] == cluster_label][feature]
                    stats.append([
                        len(df_feature),
                        df_feature.mean(),
                        df_feature.min(),
                        df_feature.quantile(0.2),
                        df_feature.quantile(0.4),
                        df_feature.quantile(0.6),
                        df_feature.quantile(0.8),
                        df_feature.max(),
                        df_feature.std(),
                    ])
                stats_df = pd.DataFrame(
                    np.array(stats).T,
                    index=['len', 'mean', 'min', '20%', '40%', '60%', '80%', 'max', 'std'],
                    columns=[f'Cluster_{label}' for label in range(clust_second)]
                )
                stats_df.to_excel(writer, sheet_name=feature)
stat(df, 'normalized')

# PCA projection
pca_folder = os.path.join(output_folder, 'PCA')
os.makedirs(pca_folder, exist_ok = True)
def pca(dataframe, folder_name):
    pca_folder1 = os.path.join(pca_folder, folder_name)
    os.makedirs(pca_folder1, exist_ok = True)
    pca = PCA(n_components = 2)
    for label in ['XS', 'S', 'M', 'L']:
        df1 = dataframe[dataframe['consumption_label'] == label].copy()
        X_pca = pca.fit_transform(df1[columns].values)
        df1['PCA1'] = X_pca[:, 0]
        df1['PCA2'] = X_pca[:, 1]
        plt.figure(figsize=(8, 6))
        clust_second = df1['final_cluster'].max() + 1
        cmap = ListedColormap(plt.get_cmap('tab10').colors[:clust_second])
        scatter = plt.scatter(df1['PCA1'], df1['PCA2'], c = df1['final_cluster'], cmap=cmap, alpha=0.7)
        plt.xlabel('PCA1')
        plt.ylabel('PCA2')
        cbar_ticks = np.linspace((clust_second - 1) / (2 * clust_second), (clust_second - 1) - ((clust_second - 1) / (2 * clust_second)), clust_second)
        cbar = plt.colorbar(scatter, label = 'Cluster')
        cbar.set_ticks(cbar_ticks)
        cbar.set_ticklabels(range(clust_second))
        plt.tight_layout()
        output_path = os.path.join(pca_folder1, f'plot_cluster_{label}.png')
        plt.savefig(output_path)
        plt.close()
pca(df, 'normalized')

# Repeat all processes for raw data
csv_path = os.path.join(current_folder, 'results/dataframes/df_raw_final.csv')
df = pd.read_csv(csv_path)
columns = ['density_pop', 'evi', 'wind_power', 'wind_std', 'offshore_wind', 'geothermal_potential', 'hydro', 'temp', 'hdd', 'cdd', 'solar_pow', 'solar_seas_ind', 'res_area']
box(df, 'raw')
stat(df, 'raw')
pca(df, 'raw')