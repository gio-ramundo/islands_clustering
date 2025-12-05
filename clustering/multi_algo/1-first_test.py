import numpy as np
import os
import pandas as pd
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN, HDBSCAN, MeanShift, SpectralClustering, Birch, OPTICS, AffinityPropagation, BisectingKMeans
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..")
csv_path = os.path.join(project_folder, "exploratory_data_analisys/df_norm.csv")
df = pd.read_csv(csv_path)
relevant_columns = [col for col in df.columns if col not in ['ALL_Uniq', 'Name_USGSO', 'consumption_label']]

# Clustering algorithms
algorithms = {
    'KMeans': KMeans,
    'AgglomerativeClustering': AgglomerativeClustering,
    'DBSCAN': DBSCAN,
    'HDBSCAN': HDBSCAN,
    'OPTICS': OPTICS,
    'MeanShift': MeanShift,
    'SpectralClustering': SpectralClustering,
    'Birch': Birch,
    'GaussianMixture': GaussianMixture,
    'AffinityPropagation': AffinityPropagation,
    'BisectingKMeans': BisectingKMeans
}

# Evaluation metrics
evaluation_metrics = {
    'silhouette_score': silhouette_score,
    'calinski_harabasz_score': calinski_harabasz_score,
    'davies_bouldin_score': davies_bouldin_score
}

# Clusters number to try
n_clust = [5, 10, 20, 30, 40]
# DF to store results
results = pd.DataFrame(columns = ["algorithm", "n_clusters", "option", "silhouette_score", "calinski_harabasz_score", "davies_bouldin_score"])

# Function that calculate metrics and stores results
def results_creation(name,n,labels,option = None):
    if n<200:
        scores = []
        for metric_name, metric_func in evaluation_metrics.items():
            try:
                score = metric_func(X, labels)
                scores.append(score)
            except Exception as e:
                scores.append(None)
        results.loc[len(results)] = [name, n, option, scores[0], scores[1], scores[2]]

# Iterate for algorithms
for name, algo in algorithms.items():
    print(f"Running {name}...")
    X = df[relevant_columns].values
    # Hyperparameter setting and iterations
    if name in ['KMeans', 'MiniBatchKMeans', 'AgglomerativeClustering', 'SpectralClustering', 'Birch', 'GaussianMixture', 'BisectingKMeans']:
        for n in n_clust:
            if name == 'KMeans' or name == 'MiniBatchKMeans':
                model = algo(n_clusters = n, random_state = 42)
                labels = model.fit_predict(X)
                results_creation(name, n, labels)
            elif name == 'AgglomerativeClustering':
                linkage = ['ward', 'complete', 'average', 'single']
                for method in linkage:
                    model = algo(n_clusters = n, linkage = method)
                    labels = model.fit_predict(X)
                    results_creation(name, n, labels, method)
            elif name == 'Birch':
                model = algo(n_clusters = n)
                labels = model.fit_predict(X)
                results_creation(name, n, labels)
            elif name == 'SpectralClustering':
                affinity = ['nearest_neighbors', 'rbf']
                for aff in affinity:
                    model = algo(n_clusters = n, assign_labels = 'discretize', random_state = 42, affinity = aff)
                    labels = model.fit_predict(X)
                    results_creation(name, n, labels, aff)
            elif name == 'GaussianMixture':
                model = algo(n_components = n, random_state = 42)
                labels = model.fit_predict(X)
                results_creation(name, n, labels)
            elif name == 'BisectingKMeans':
                bisecting_strategy = ["biggest_inertia", "largest_cluster"]
                for strategy in bisecting_strategy:
                    model = algo(n_clusters = n, random_state = 42, bisecting_strategy = strategy)
                    labels = model.fit_predict(X)
                    results_creation(name, n, labels, strategy)
    else:
        if name == 'DBSCAN':
            eps_range = np.arange(0.2, 1.2, 0.1)
            for eps in eps_range:
                model = algo(eps = eps)
                labels=model.fit_predict(X)
                n = max(labels) + 1
                results_creation(name, n, labels, eps)
        elif name == 'HDBSCAN':
            cluster_selection_method = ['eom', 'leaf']
            for method in cluster_selection_method:
                model = algo(cluster_selection_method = method)
                labels = model.fit_predict(X)
                n = max(labels) + 1
                results_creation(name, n, labels, method)
        elif name == 'AffinityPropagation':
            multipliers = [0.3, 0.5, 1, 2, 3, 5]
            model = algo()
            labels = model.fit_predict(X)
            n = max(labels) + 1
            results_creation(name, n, labels)
            for multi in multipliers:
                preference = - np.median(X) * multi
                model = algo(preference = preference)
                labels = model.fit_predict(X)
                n = max(labels) + 1
                results_creation(name, n, labels, multi)
        else:
            model = algo()
            labels = model.fit_predict(X)
            n = max(labels) + 1
            results_creation(name, n, labels)

# Order results for metrics
for metric in ["silhouette_score", "calinski_harabasz_score"]:
    print(f"\nTop 5 algorithms by {metric}:")
    print(results.sort_values(by = metric, ascending = False)[["algorithm", "n_clusters", "option", metric]].head(5))

print(f"\nTop 5 algorithms by davies_bouldin_score (lower is better):")
print(results.sort_values(by = "davies_bouldin_score", ascending = True)[["algorithm", "n_clusters", "option", "davies_bouldin_score"]].head(5))