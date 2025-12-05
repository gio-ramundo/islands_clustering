import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

current_folder = os.path.dirname(os.path.abspath(__file__))

df_folder = os.path.join(current_folder, "..", "..")
csv_path = os.path.join(df_folder, 'df_dim_reduction.csv')
df = pd.read_csv(csv_path)
relevant_col = [col for col in df.columns if col != 'ALL_Uniq']

out_folder = os.path.join(current_folder, "..", "results")
os.makedirs(out_folder, exist_ok = True)
output_folder = os.path.join(out_folder, "boxplots")
os.makedirs(output_folder, exist_ok = True)

# Iterate for columns
for col in df[relevant_col].select_dtypes(include = 'number').columns:
    output_folder1 = os.path.join(output_folder, "normal")
    os.makedirs(output_folder1, exist_ok = True)
    output_path = os.path.join(output_folder1, f"{col}_boxplot.png")
    plt.figure(figsize = (10, 15))
    sns.boxplot(x = df[col], showfliers=True, color='skyblue')
    plt.title(f"{col} Boxplot")
    plt.xlabel("")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    # New plot for variables with many zeros
    zero_count = (df[col] == 0).sum()
    zero_ratio = zero_count / len(df)
    if zero_ratio > 0.5:
        df_no_zero = df[df[col] != 0]
        plt.figure(figsize = (10, 15))
        sns.boxplot(x = df_no_zero[col], showfliers = True, color = 'green')
        plt.title(f"{col} Boxplot")
        plt.xlabel("")
        plt.ylabel("")
        plt.tight_layout()
        output_folder1 = os.path.join(output_folder, "no_zeros")
        os.makedirs(output_folder1, exist_ok = True)
        output_path = os.path.join(output_folder1, f"{col}_boxplot.png")
        plt.savefig(output_path)
        plt.close()