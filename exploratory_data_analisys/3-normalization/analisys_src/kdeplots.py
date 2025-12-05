import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

current_folder = os.path.dirname(os.path.abspath(__file__))

df_folder = os.path.join(current_folder, "..", "..")
csv_path = os.path.join(df_folder, 'df_norm.csv')
df = pd.read_csv(csv_path)
relevant_col = [col for col in df.columns if col != 'ALL_Uniq']

out_folder = os.path.join(current_folder, "..", "results")
os.makedirs(out_folder, exist_ok = True)
out_folder = os.path.join(out_folder, "kde_plots")
os.makedirs(out_folder, exist_ok = True)
for col in df[relevant_col].select_dtypes(include = 'number').columns:
    out_folder1 = os.path.join(out_folder, "normal")
    os.makedirs(out_folder1, exist_ok = True)
    output_path = os.path.join(out_folder1, f"{col}_kdeplot.png")
    plt.figure(figsize = (10, 15))
    sns.kdeplot(df[col], shade = True, color = "skyblue",fill = True)
    plt.xlabel('')
    plt.ylabel('Density')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    # Variables with many zeros
    if col in ['offshore_wind', 'hydro', 'geothermal_potential']:
        df_no_zeros = df[df[col] != 0]
        out_folder1 = os.path.join(out_folder, "no_zeros")
        os.makedirs(out_folder1, exist_ok = True)
        output_path = os.path.join(out_folder1, f"{col}_kdeplot.png")
        plt.figure(figsize = (10, 15))
        sns.kdeplot(df_no_zeros[col], shade = True, color = "green", fill = True)
        plt.xlabel('')
        plt.ylabel('Density')
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()