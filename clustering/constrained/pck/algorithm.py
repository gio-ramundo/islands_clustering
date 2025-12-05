import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle
from sklearn.metrics import silhouette_score
import sys

# Clustering algorithm
from active_semi_clustering.semi_supervised.pairwise_constraints import PCKMeans
sys.setrecursionlimit(2000)

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..", "..")

csv_path = os.path.join(project_folder, "exploratory_data_analisys/df_norm.csv")
df = pd.read_csv(csv_path)
not_relevant_col = ['ALL_Uniq', 'Name_USGSO', 'consumption_label']
relevant_col = [col for col in df.columns if col not in not_relevant_col]
# Constraints
pkl_path = os.path.join(current_folder, '..', 'cannot_link.pkl')
cl = pickle.load(open(pkl_path, 'rb'))

# Different violations weights
weights = [0.5, 1, 2, 3]
# Violations counter list
violations = []

# Function to count constraints violations
def violations_counter(labels):
    cont = 0
    for constraint in cl:
        if labels[constraint[0]] == labels[constraint[1]]:
            cont += 1
    return cont/len(cl)

# Iterate for weight-cluster number combination and export silhouette plots
for w in weights:
    shilouette = []
    for n_clust in range(5,26):
        print(f"Trial with {n_clust} cluster and weight {w}")
        pck = PCKMeans(n_clusters = n_clust, w = w)
        pck.fit(df[relevant_col].values, cl = cl)
        score_pck = silhouette_score(df[relevant_col], pck.labels_)
        shilouette.append(score_pck)
        df[f'cluster_label_pck_{n_clust}_{w}'] = pck.labels_
        # Violations list update
        violation = violations_counter(pck.labels_)
        if w == 0.5:
            violations.append([violation])
        else:
            violations[n_clust-5].append(violation)
    
    # Silouhette plot
    plt.figure(figsize = (12,10))
    plt.plot(range(5,26), shilouette, marker = 'o')
    plt.title(f'Elbow Method for Optimal K, w={w}')
    plt.xlabel('Number of clusters (k)')
    plt.ylabel(f'Shilouette score PCKMeans')
    plt.grid(True)
    out_folder = os.path.join(current_folder, 'silhouette')
    os.makedirs(out_folder, exist_ok = True)
    out_path=os.path.join(out_folder, f'elbow_method_w_{w}.png')
    plt.savefig(out_path)
    plt.close()

# Violations plots
for n in range(len(violations)):
    plt.figure(figsize = (12, 10))
    plt.plot(weights, violations[n], marker = 'o')
    plt.title(f'Constraints violations for {n+5} cluster')
    plt.xlabel('Violations weight (w)')
    plt.ylabel(f'Violations share of total constraints')
    plt.grid(True)
    out_folder = os.path.join(current_folder, 'violations')
    os.makedirs(out_folder, exist_ok = True)
    out_path=os.path.join(out_folder, f'violations_n_{n+5}.png')
    plt.savefig(out_path)
    plt.close()

# DF exportation
output_path = os.path.join(current_folder, 'df_labels.csv')
df.to_csv(output_path)