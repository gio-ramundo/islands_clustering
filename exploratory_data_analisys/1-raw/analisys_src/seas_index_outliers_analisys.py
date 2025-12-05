# Analisys to prove that huge values of the index are related to islands with low mean PVOUT
import pandas as pd
import os

current_folder = os.path.dirname(os.path.abspath(__file__))

df_folder = os.path.join(current_folder, "..", "..")
csv_path = os.path.join(df_folder, 'df_raw.csv')
df = pd.read_csv(csv_path)
mean = df['solar_pow'].mean()
print(f"Mean PVOUT for all islands: {mean}")
for i in range(4,11):
    df1 = df[(df['solar_seas_ind'] > i)]
    mean = df1['solar_pow'].mean()
    print(f'Mean PVOUT for islands with index greater than {i}: {mean}')
for i in range(10,35,5):
    df1 = df[(df['solar_seas_ind'] > i)]
    mean = df1['solar_pow'].mean()
    print(f'Mean PVOUT for islands with index greater than {i}: {mean}')
for i in range(30,200,10):
    df1 = df[(df['solar_seas_ind'] > i)]
    mean = df1['solar_pow'].mean()
    print(f'Mean PVOUT for islands with index greater than {i}: {mean}')