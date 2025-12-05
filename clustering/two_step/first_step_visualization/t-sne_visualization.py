import os
import pandas as pd
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..", "..")
csv_path = os.path.join(project_folder, "exploratory_data_analisys/df_norm.csv")
df = pd.read_csv(csv_path)

# Columns to project
columns = ["density_pop", "gdp_cons_pop_urban_merged", "wind_power", "solar_pow", "res_area", "solar_seas_ind", "wind_std", "offshore_wind", "evi", "hydro", "geothermal_potential", "temp"]
# Expo folder
tsne_fold = os.path.join(current_folder, 'tsne_visualizations')
os.makedirs(tsne_fold, exist_ok=True)
# Iterate for different perplexity values
for i in range(20, 41, 10):
    tsne = TSNE(n_components = 2, perplexity = i, random_state = 42)
    data = df[columns].values
    tsne_result = tsne.fit_transform(data)
    plt.figure(figsize=(8, 6))
    sns.scatterplot(
        x=tsne_result[:, 0],
        y=tsne_result[:, 1],
        hue=df['consumption_label'],
        palette='viridis',
        legend='full',
        s=50
    )
    # Expo
    plt.title(f"t-SNE projection (Perplexity: {i})")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(tsne_fold, f'tsne_visualization_perp_{i}.png'))
    plt.close()