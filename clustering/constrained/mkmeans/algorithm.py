import os
import matplotlib.pyplot as plt
import pandas as pd
import pickle
from sklearn.metrics import silhouette_score

# Clustering algorithm
from active_semi_clustering.semi_supervised.pairwise_constraints import MKMeans

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..", "..")

csv_path = os.path.join(project_folder, "exploratory_data_analisys/df_norm.csv")
df = pd.read_csv(csv_path)
not_relevant_col = ['ALL_Uniq', 'Name_USGSO', 'consumption_label']
relevant_col = [col for col in df.columns if col not in not_relevant_col]
# Constraints
pkl_path = os.path.join(current_folder, '..', 'cannot_link.pkl')
cl = pickle.load(open(pkl_path, 'rb'))

# Function to count constraints violations
def violations_counter(labels):
    cont = 0
    for constraint in cl:
        if labels[constraint[0]] == labels[constraint[1]]:
            cont += 1
    return cont/len(cl)

# Repeat the process and store different results
i = 0
while i < 10:
    i +=1
    print(f'Iteration {i} of 10')
    shilouette = []
    violations = []
    # Iterate for different clusters number
    for n_clust in range(5,31):
        mk = MKMeans(n_clusters = n_clust, max_iter = 10000)
        mk.fit(df[relevant_col].values, cl = cl)
        score_mk = silhouette_score(df[relevant_col], mk.labels_)
        shilouette.append(score_mk)
        df[f'cluster_label_mk_{n_clust}'] = mk.labels_
        violation = violations_counter(mk.labels_)
        violations.append(violation)
    
    # Plots exportation
    out_folder = os.path.join(current_folder, 'silhouette')
    os.makedirs(out_folder, exist_ok = True)
    plt.figure(figsize = (12,10))
    plt.plot(range(5,31), shilouette, marker = 'o')
    plt.title(f'Elbow Method for Optimal K')
    plt.xlabel('Number of clusters (k)')
    plt.ylabel(f'Shilouette score MKMeans')
    plt.grid(True)
    output_path = os.path.join(out_folder, f'elbow_method_run_{i}.png')
    plt.savefig(output_path)
    plt.close()

    out_folder = os.path.join(current_folder, 'violations')
    os.makedirs(out_folder, exist_ok = True)
    plt.figure(figsize=(12,10))
    plt.plot(range(5,31), violations, marker = 'o')
    plt.title(f'Violated constrained for cluster number')
    plt.xlabel('Number of clusters (k)')
    plt.ylabel(f'Violations share of total constraints')
    plt.grid(True)
    output_path=os.path.join(out_folder, f'violations_run_{i}.png')
    plt.savefig(output_path)
    plt.close()

    # DF exportation
    out_folder = os.path.join(current_folder, 'dataframes')
    os.makedirs(out_folder, exist_ok = True)
    output_path = os.path.join(out_folder, f'df_labels_run_{i}.csv')
    df.to_csv(output_path)