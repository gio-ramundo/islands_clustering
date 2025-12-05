import numpy as np
import os
import pandas as pd
from sklearn.cluster import KMeans, BisectingKMeans, Birch, AgglomerativeClustering, SpectralClustering
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..")
csv_path = os.path.join(project_folder, "exploratory_data_analisys/df_norm.csv")
df = pd.read_csv(csv_path)
relevant_columns = [col for col in df.columns if col not in ['ALL_Uniq', 'Name_USGSO', 'consumption_label']]

algorithms = {
    "KMeans": KMeans,
    "BisectingKMeans": BisectingKMeans,
    "Birch": Birch,
    "AgglomerativeClustering": AgglomerativeClustering,
    "SpectralClustering": SpectralClustering
}
evaluation_metrics = {
    "silhouette_score": silhouette_score,
    "calinski_harabasz_score": calinski_harabasz_score,
    "davies_bouldin_score": davies_bouldin_score
}
columns = ['algorithm', 'options', 'n_cluster', 'random_state'] + list(evaluation_metrics.keys())
results = pd.DataFrame(columns = columns)

X = df[relevant_columns].values

# Try all different hyperparameter combination for every algorithm
print('Kmeans...')
for n in range(5, 21):
    print(f'{n} cluster')
    for init in ['k-means++', 'random']:
        for algo in ['lloyd', 'elkan']:
            for state in [42, 123, 456, 789, 1011, 2022, 3033, 4044, 5055, 6066]:
                options = {
                    'init': init,
                    'algorithm': algo
                }
                kmeans = KMeans(n_clusters = n, init = init, random_state = state, algorithm = algo)
                labels = kmeans.fit_predict(X)
                scores = []
                for metric_name, metric_func in evaluation_metrics.items():
                    try:
                        score = metric_func(X, labels)
                    except Exception as e:
                        print(f"Error calculating {metric_name} for options {options}: {e}")
                        score = np.nan
                    scores.append(score)
                results.loc[len(results)] = ['KMeans', options, n, state] + scores

print('BisectingKMeans...')
for n in range(5, 21):
    print(f'{n} cluster')
    for init in ['k-means++', 'random']:
        for algo in ['lloyd', 'elkan']:
            for state in [42, 123, 456, 789, 1011, 2022, 3033, 4044, 5055, 6066]:
                options = {
                    'init': init,
                    'algorithm': algo
                }
                bisect_kmeans = BisectingKMeans(n_clusters = n, init = init, algorithm = algo, random_state = state)
                labels = bisect_kmeans.fit_predict(X)
                scores = []
                for metric_name, metric_func in evaluation_metrics.items():
                    try:
                        score = metric_func(X, labels)
                    except Exception as e:
                        print(f"Error calculating {metric_name} for options {options}: {e}")
                        score = np.nan
                    scores.append(score)
                results.loc[len(results)] = ['BisectingKMeans', options, n, state] + scores

print('Birch...')
for n in range(5, 21):
    print(f'{n} cluster')
    for threshold in [0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0, 1.5, 2, 5, 10]:
        for branching_factor in [10, 20, 30, 40, 50, 75, 100, 150, 200, 500]:
            options = {
                'threshold': threshold,
                'branching_factor': branching_factor
            }
            birch = Birch(n_clusters = n, threshold = threshold, branching_factor = branching_factor)
            labels = birch.fit_predict(X)
            if len(list(set(labels))) >= n-2:
                scores = []
                for metric_name, metric_func in evaluation_metrics.items():
                    try:
                        score = metric_func(X, labels)
                    except Exception as e:
                        print(f"Error calculating {metric_name} for options {options}: {e}")
                        score = np.nan
                    scores.append(score)
                results.loc[len(results)] = ['Birch', options, n, -1] + scores

print('AgglomerativeClustering...')
for n in range(5, 50):
    print(f'{n} cluster')
    for linkage in ['ward', 'complete', 'average', 'single']:
        # 'ward' linkage only supports 'euclidean' affinity
        metric_list = ['euclidean'] if linkage == 'ward' else ['euclidean', 'l1', 'l2', 'manhattan', 'cosine']
        for metric in metric_list:
            options = {
                'linkage': linkage,
                'metric': metric
            }
            try:
                agglo = AgglomerativeClustering(n_clusters = n, linkage = linkage, metric = metric)
                labels = agglo.fit_predict(X)
                scores = []
                for metric_name, metric_func in evaluation_metrics.items():
                    try:
                        score = metric_func(X, labels)
                    except Exception as e:
                        print(f"Error calculating {metric_name} for options {options}: {e}")
                        score = np.nan
                    scores.append(score)
                results.loc[len(results)] = ['AgglomerativeClustering', options, n, -1] + scores
            except Exception as e:
                print(f"Error fitting AgglomerativeClustering for options {options}: {e}")

print('SpectralClustering...')
for n in range(5, 21):
    print(f'{n} cluster')
    for affinity in ['rbf', 'nearest_neighbors', 'cosine', 'linear', 'polynomial', 'poly', 'sigmoid']:
        print(affinity)
        # Set n_neighbors values for 'nearest_neighbors' affinity only
        n_neighbors_list = [5, 10, 15, 20, 50, 100] if affinity == 'nearest_neighbors' else [None]
        for n_neighbors in n_neighbors_list:
            for assign_label in ['kmeans', 'discretize', 'cluster_qr']:
                for state in [42, 123, 456, 789, 1011, 2022, 3033, 4044, 5055, 6066]:
                    options = {
                        'affinity': affinity,
                        'assign_labels': assign_label
                    }
                    if n_neighbors is not None:
                        options['n_neighbors'] = n_neighbors
                    try:
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
                        scores = []
                        for metric_name, metric_func in evaluation_metrics.items():
                            try:
                                score = metric_func(X, labels)
                            except Exception as e:
                                print(f"Error calculating {metric_name} for options {options}: {e}")
                                score = np.nan
                            scores.append(score)
                        results.loc[len(results)] = ['SpectralClustering', options, n, state] + scores
                    except Exception as e:
                        print(f"Error fitting SpectralClustering for options {options}: {e}")

# Expo
output_dir = os.path.join(current_folder, "results")
os.makedirs(output_dir, exist_ok=True)
results.to_pickle(os.path.join(output_dir, "first_trials_results.pkl"))