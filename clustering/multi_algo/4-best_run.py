import numpy as np
import os
import pandas as pd
from sklearn.cluster import KMeans, BisectingKMeans, Birch, AgglomerativeClustering, SpectralClustering
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import xlsxwriter

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..")
csv_path = os.path.join(project_folder, "exploratory_data_analisys/df_norm.csv")
df = pd.read_csv(csv_path)
relevant_columns = [col for col in df.columns if col not in ['ALL_Uniq', 'Name_USGSO', 'consumption_label']]

# Hyperparameter combinations
pkl_path = os.path.join(current_folder, 'results/best_configs.pkl')
method1 = pd.read_pickle(pkl_path)[['algorithm', 'options', 'n_cluster', 'random_state']].iloc[0]
pkl_path = os.path.join(current_folder, 'results/best_configs1.pkl')
method2 = pd.read_pickle(pkl_path)[['algorithm', 'options', 'n_cluster', 'random_state']].iloc[0]
pkl_path = os.path.join(current_folder, 'results/best_configs2.pkl')
method3 = pd.read_pickle(pkl_path)[['algorithm', 'options', 'n_cluster', 'random_state']].iloc[0]

methods = [method1, method2, method3]
X = df[relevant_columns].values

results = []

# Algorithm run
for method in methods:
    n = method['n_cluster']
    options = method['options']
    if method['algorithm'] in ['KMeans','BisectingKMeans']:
        algo = options['algorithm']
        init = options['init']
        state = int(method['random_state'])
        if method['algorithm'] == 'KMeans':
            kmeans = KMeans(n_clusters = n, init = init, random_state = state, algorithm = algo)
            labels = kmeans.fit_predict(X)
            if 'Kmeans' not in df.columns:
                df['Kmeans'] = labels
            else:
                df['Kmeans2'] = labels
        if method['algorithm'] == 'BisectingKMeans':
            bis_kmeans = BisectingKMeans(n_clusters = n, init = init, random_state = state, algorithm = algo)
            labels = bis_kmeans.fit_predict(X)
            if 'BisectingKmeans' not in df.columns:
                df['BisectingKmeans'] = labels
            else:
                df['BisectingKmeans2'] = labels
    if method['algorithm'] == 'Birch':
        threshold = options['threshold']
        branching_factor = options['branching_factor']
        birch = Birch(n_clusters = n, threshold = threshold, branching_factor = branching_factor)
        labels = birch.fit_predict(X)
        if 'Birch' not in df.columns:
            df['Birch'] = labels
        else:
            df['Birch2'] = labels
    if method['algorithm'] == 'AgglomerativeClustering':
        linkage = options['linkage']
        metric = options['metric']
        agglo = AgglomerativeClustering(n_clusters = n, linkage = linkage, metric = metric)
        labels = agglo.fit_predict(X)
        if 'Agglomerative' not in df.columns:
            df['Agglomerative'] = labels
        else:
            df['Agglomerative2'] = labels
    if method['algorithm'] == 'SpectralClustering':
        affinity = options['affinity']
        n_neighbors = options['n_neighbors'] if affinity == 'nearest_neighbors' else None
        assign_label = options['assign_labels']
        state = options['random_state']
        spectral_kwargs = dict(
            n_clusters = n,
            affinity = affinity,
            assign_labels = assign_label,
            random_state = state
        )
        if n_neighbors is not None:
            spectral_kwargs['n_neighbors'] = n_neighbors
        spectral = SpectralClustering(**spectral_kwargs)
        labels = spectral.fit_predict(X)
        if 'SpectralClustering' not in df.columns:
            df['SpectralClustering'] = labels
        else:
            df['SpectralClustering2'] = labels

clustering_columns = [col for col in df.columns if col not in relevant_columns + ['ALL_Uniq', 'Name_USGSO', 'consumption_label']]
not_valid_methods = []

# Validity check
for col in clustering_columns:
    n_clusters = max(df[col])+1
    for i in range(n_clusters):
        if len(df[df[col] == i]) > 2000 or len(df[df[col] == i]) == 1:
            not_valid_methods.append(col)
            break

# Results analisys
clustering_columns = [col for col in clustering_columns if col not in not_valid_methods]

# Function to export clustering results in different formats
def export(dataframe, method, name, columns):
    # PCA projection
    pca = PCA(n_components = 2)
    X_pca = pca.fit_transform(dataframe[columns].values)
    dataframe['PCA1'] = X_pca[:, 0]
    dataframe['PCA2'] = X_pca[:, 1]
    plt.figure(figsize = (8, 6))
    n_clusters = dataframe[method].nunique()
    cmap = ListedColormap(plt.get_cmap('tab10').colors[:n_clusters])
    scatter = plt.scatter(dataframe['PCA1'], dataframe['PCA2'], c = dataframe[method], cmap = cmap, alpha = 0.7)
    plt.xlabel('PCA1')
    plt.ylabel('PCA2')
    plt.title(f'Clusters by {method} on PCA projection')
    plt.colorbar(scatter, label = 'Cluster')
    plt.tight_layout()
    output_folder = os.path.join(current_folder, 'results/best', method, name)
    os.makedirs(output_folder, exist_ok = True)
    output_path = os.path.join(output_folder, f'plot_{method}.png')
    plt.savefig(output_path)
    plt.close()

    # .xlsx file, every sheet is referred to a feature
    output_xlsx = os.path.join(output_folder, f'statistics_{method}.xlsx')
    with pd.ExcelWriter(output_xlsx, engine = 'xlsxwriter') as writer:
        for feature in columns:
            stats = []
            cluster_labels = sorted(dataframe[method].unique())
            for cluster_label in cluster_labels:
                cluster_df= dataframe[dataframe[method] == cluster_label][feature]
                stats.append([
                    len(cluster_df),
                    cluster_df.mean(),
                    cluster_df.min(),
                    cluster_df.quantile(0.2),
                    cluster_df.quantile(0.4),
                    cluster_df.quantile(0.6),
                    cluster_df.quantile(0.8),
                    cluster_df.max(),
                    cluster_df.std(),
                ])
            stats_df = pd.DataFrame(
                np.array(stats).T,
                index = ['len','mean', 'min', '20%', '40%', '60%', '80%', 'max', 'std'],
                columns = [f'Cluster_{label}' for label in cluster_labels]
            )
            stats_df.to_excel(writer, sheet_name = feature)

            # Boxplots for different features
            plt.figure(figsize = (8, 6))
            data = [dataframe[dataframe[method] == cluster_label][feature] for cluster_label in cluster_labels]
            plt.boxplot(data, vert = True, patch_artist = True)
            plt.title(f"{feature} Boxplot")
            plt.xlabel('')
            plt.ylabel('Values')
            plt.xticks(ticks = range(1, len(cluster_labels) + 1), labels = [f'Cluster {label}' for label in cluster_labels])
            plt.tight_layout()
            boxplot_folder = os.path.join(output_folder, 'boxplot')
            os.makedirs(boxplot_folder, exist_ok = True)
            boxplot_path = os.path.join(boxplot_folder, f'{feature}_boxplot.png')
            plt.savefig(boxplot_path)
            plt.close()
    # .xlsx file, every sheet is referred to a feature
    output_xlsx = os.path.join(output_folder, f'islands_conusmption_class_cluster.xlsx')
    with pd.ExcelWriter(output_xlsx, engine = 'xlsxwriter') as writer:
        stats = []
        cluster_labels = sorted(dataframe[method].unique())
        for cluster_label in cluster_labels:
            cluster_df= dataframe[dataframe[method] == cluster_label]
            stats.append([
                len(cluster_df),
                len(cluster_df[cluster_df['consumption_label']=='XS']),
                len(cluster_df[cluster_df['consumption_label']=='S']),
                len(cluster_df[cluster_df['consumption_label']=='M']),
                len(cluster_df[cluster_df['consumption_label']=='L'])
                ])
        stats_df = pd.DataFrame(
            np.array(stats).T,
            index = ['Total','XS','S', 'M', 'L'],
            columns = [f'Cluster_{label}' for label in cluster_labels]
        )
        stats_df.to_excel(writer)

# Function application to various methods
for method in clustering_columns:
    output_folder = os.path.join(current_folder, 'results/best', method)
    os.makedirs(output_folder, exist_ok = True)
    export(df, method, 'normalized', relevant_columns)
    csv_out_path = os.path.join(output_folder, 'normalized', 'df.csv')
    df[relevant_columns + ['ALL_Uniq', 'Name_USGSO', 'consumption_label'] + [method]].to_csv(csv_out_path, index = False, encoding = 'utf-8')
    # Repeat for different data format
    csv_path = os.path.join(project_folder, "exploratory_data_analisys/df_raw.csv")
    df1 = pd.read_csv(csv_path)
    columns = [col for col in df1.columns if col not in ['ALL_Uniq', 'Name_USGSO', 'consumption_label']]
    df1[method] = df[method]
    export(df1, method, 'raw', columns)
    csv_out_path = os.path.join(output_folder, 'raw', 'df.csv')
    df1[columns + ['ALL_Uniq', 'Name_USGSO', 'consumption_label'] + [method]].to_csv(csv_out_path, index = False, encoding = 'utf-8')
    csv_path = os.path.join(project_folder, "exploratory_data_analisys/df_dim_reduction.csv")
    df2 = pd.read_csv(csv_path)
    columns = [col for col in df2.columns if col not in ['ALL_Uniq', 'Name_USGSO', 'consumption_label']]
    df2[method] = df[method]
    export(df2, method, 'dimensions_reduction', columns)
    csv_out_path = os.path.join(output_folder, 'dimensions_reduction', 'df.csv')
    df2[columns + ['ALL_Uniq', 'Name_USGSO', 'consumption_label'] +[method]].to_csv(csv_out_path, index = False, encoding = 'utf-8')