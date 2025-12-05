import pandas as pd
import os
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

current_folder = os.path.dirname(os.path.abspath(__file__))

df_folder = os.path.join(current_folder, "..", "..")
csv_path = os.path.join(df_folder, 'df_dim_reduction.csv')
df = pd.read_csv(csv_path)
relevant_col = [col for col in df.columns if col != 'ALL_Uniq']

out_folder = os.path.join(current_folder, "..", "results/PCA")
os.makedirs(out_folder, exist_ok=True)

col=['PC1','PC2','PC3','PC4']
X = df[relevant_col].select_dtypes(include = 'number')
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
for j in range(2,5):
    pca = PCA(n_components = j)
    X_pca = pca.fit_transform(X_scaled)
    df_pca = pd.DataFrame(X_pca, columns = col[:j])
    print(f"Variance explained by model's components: {pca.explained_variance_ratio_}")
    output_path = os.path.join(out_folder, f'PCA_{j}_components.csv')
    df_pca.to_csv(output_path, index = False, encoding = 'utf-8')

# Variance explained by model's components: [0.24510922 0.1776403 ]
# Variance explained by model's components: [0.24510922 0.1776403  0.09704012]
# Variance explained by model's components: [0.24510922 0.1776403  0.09704012 0.08663802]