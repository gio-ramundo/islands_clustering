import os
import matplotlib.pyplot as plt
import pandas as pd
import pickle
from sklearn.metrics import silhouette_score

# Clustering algorithm
from active_semi_clustering.semi_supervised.pairwise_constraints import COPKMeans

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..", "..")

csv_path = os.path.join(project_folder, "exploratory_data_analisys/df_norm.csv")
df = pd.read_csv(csv_path)
not_relevant_col = ['ALL_Uniq', 'Name_USGSO', 'consumption_label']
relevant_col = [col for col in df.columns if col not in not_relevant_col]
# Constraints
pkl_path = os.path.join(current_folder, '..', 'cannot_link.pkl')
cl = pickle.load(open(pkl_path, 'rb'))

# Evaluation matric list
silhouette = []
clust_list = []

# Iterate for different cluster numbers
for n_clust in range(5,26):
    copk = COPKMeans(n_clusters=n_clust)
    try:
        copk.fit(df[relevant_col].values, cl = cl)
        score_copk = silhouette_score(df[relevant_col], copk.labels_)
        # Lists update
        silhouette.append(score_copk)
        df[f'cluster_label_copk_{n_clust}'] = copk.labels_
        clust_list.append(n_clust)
        print(f'Solution found for {n_clust} cluster')
    except:
        print(f'Solution not found for {n_clust} cluster')
        
# Silhouette plot generation
plt.figure(figsize = (12,10))
plt.plot(clust_list, silhouette, marker = 'o')
plt.title(f'Elbow Method for Optimal K')
plt.xlabel('Number of clusters (k)')
plt.ylabel(f'Silhouette score COPKMeans')
plt.grid(True)
output_path = os.path.join(current_folder, f'elbow_method.png')
plt.savefig(output_path)
plt.close()

# DF exportation
output_path = os.path.join(current_folder, 'df_copkm_labels.csv')
df.to_csv(output_path)