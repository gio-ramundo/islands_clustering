import pandas as pd
import os

current_folder = os.path.dirname(os.path.abspath(__file__))

df_folder = os.path.join(current_folder, "..", "..")
csv_path = os.path.join(df_folder, 'df_dim_reduction.csv')
df = pd.read_csv(csv_path)
relevant_col = [col for col in df.columns if col != 'ALL_Uniq']

# Descriptove dataframe
descr = df[relevant_col].select_dtypes(include = 'number').describe()

# Expo
out_folder = os.path.join(current_folder, "..", "results")
os.makedirs(out_folder, exist_ok = True)
output_path = os.path.join(out_folder, 'descriptive_stats.xlsx')
descr.to_excel(output_path)