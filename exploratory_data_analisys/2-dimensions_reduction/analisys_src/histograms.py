import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

current_folder = os.path.dirname(os.path.abspath(__file__))
df_folder = os.path.join(current_folder, "..", "..")
csv_path = os.path.join(df_folder, 'df_dim_reduction.csv')
df = pd.read_csv(csv_path)
relevant_col = [col for col in df.columns if col != 'ALL_Uniq']

out_folder = os.path.join(current_folder, "..", "results")
os.makedirs(out_folder, exist_ok = True)
out_folder = os.path.join(out_folder, "histograms")
os.makedirs(out_folder, exist_ok = True)
for col in df[relevant_col].select_dtypes(include = 'number').columns:
    out_folder1 = os.path.join(out_folder, "normal")
    os.makedirs(out_folder1, exist_ok = True)
    out_path = os.path.join(out_folder1, f"{col}_histogram.png")
    plt.figure(figsize = (10, 15))
    df[col].hist(bins = 60, color = 'skyblue', edgecolor = 'black')
    plt.title(f"{col} Histogram")
    plt.xlabel(col)
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    # Variables with many zeros
    zero_count = (df[col] == 0).sum()
    zero_ratio = zero_count / len(df)
    if zero_ratio>0.5:
        df_no_zeros = df[df[col] != 0]
        plt.figure(figsize = (10, 15))
        plt.hist(df_no_zeros[col], bins = 60, color = 'green', edgecolor = 'black')
        plt.title(f'{col} Histogram (no zeros)')
        plt.xlabel(col)
        plt.ylabel('Frequency')
        plt.tight_layout()
        out_folder1 = os.path.join(out_folder, "no_zeros")
        os.makedirs(out_folder1, exist_ok = True)
        out_path = os.path.join(out_folder1, f"{col}_histogram.png")
        plt.savefig(out_path)
        plt.close()