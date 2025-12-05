import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

current_folder = os.path.dirname(os.path.abspath(__file__))

df_folder = os.path.join(current_folder, "..", "..")
csv_path = os.path.join(df_folder, 'df_norm.csv')
df = pd.read_csv(csv_path)
relevant_col = [col for col in df.columns if col != 'ALL_Uniq']

output_folder = os.path.join(current_folder, "..", "results")
os.makedirs(output_folder, exist_ok = True)
output_folder = os.path.join(output_folder, "correlations")
os.makedirs(output_folder, exist_ok = True)
correlation_matrix = df[relevant_col].select_dtypes(include='number').corr(numeric_only = True)
output_path = os.path.join(output_folder, "correlation_matrix.xlsx")
correlation_matrix.to_excel(output_path)
plt.figure(figsize = (12, 10))
sns.heatmap(correlation_matrix, annot = True, cmap = 'coolwarm', fmt = ".2f", square = True)
plt.title("Correlation Heatmap")
plt.tight_layout()
output_path = os.path.join(output_folder, "correlation_heatmap.png")
plt.savefig(output_path)
plt.close()

# Scatter plots for some relevant features
scatter_col = ['res_area', 'density_pop', 'wind_power', 'temp', 'solar_pow', 'gdp_cons_pop_urban_merged']
plt.figure(figsize = (30, 30))
sns.pairplot(df[scatter_col].select_dtypes(include = 'number'))
output_path = os.path.join(output_folder,'scatter_plot.png')
plt.savefig(output_path)
plt.close()