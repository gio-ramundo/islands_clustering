import numpy as np
import os
import pandas as pd
import json

current_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.join(current_folder, "..", "..")

# Results import
pkl_path = os.path.join(current_folder, "results/first_trials_results.pkl")
df = pd.read_pickle(pkl_path)

df_clean = df.copy()
# String containing every option except random state
df_clean['options_str'] = df_clean['options'].apply(lambda x: json.dumps(x, sort_keys=True))
df_clean['config_key'] = df_clean.apply(lambda row: (
    row['algorithm'],
    row['n_cluster'],
    row['options_str']
), axis=1)

# From elements with same 'config_key' (differ for random state only) I save those with best performance only
best_silhouette = df_clean.loc[df_clean.groupby('config_key')['silhouette_score'].idxmax()]
best_calinski = df_clean.loc[df_clean.groupby('config_key')['calinski_harabasz_score'].idxmax()]
best_davies = df_clean.loc[df_clean.groupby('config_key')['davies_bouldin_score'].idxmin()]

# Best combinations
# Referred to all three metrics
common_keys=set()
#Reffered to evaluations couples that can be formed
common_keys1=set()
common_keys2=set()
common_keys3=set()

# First a element of every dataframe are considered in every iteration to find a common one
a = 1
while True:
    top_silhouette = best_silhouette.sort_values(by='silhouette_score', ascending=False).head(a)
    top_calinski = best_calinski.sort_values(by='calinski_harabasz_score', ascending=False).head(a)
    top_davies = best_davies.sort_values(by='davies_bouldin_score', ascending=True).head(a)
    if len(common_keys) == 0:
        common_keys = set(top_silhouette['config_key']) & \
                      set(top_calinski['config_key']) & \
                      set(top_davies['config_key'])
        if len(common_keys) > 0:
            print(f"Found {len(common_keys)} common configurations with top scores at a={a}:")
            print(common_keys)
    if len(common_keys1) == 0:
        common_keys1 = set(top_silhouette['config_key']) & \
                      set(top_calinski['config_key'])
        if len(common_keys1) > 0:
            print(f"Found {len(common_keys1)} common configurations in sil and cal with top scores at a={a}:")
            print(common_keys1)
    if len(common_keys2) == 0:
        common_keys2 = set(top_silhouette['config_key']) & \
                      set(top_davies['config_key'])
        if len(common_keys2) > 0:
            print(f"Found {len(common_keys2)} common configurations in sil and dav with top scores at a={a}:")
            print(common_keys2)
    if len(common_keys3) == 0:
        common_keys3 = set(top_calinski['config_key']) & \
                      set(top_davies['config_key'])
        if len(common_keys3) > 0:
            print(f"Found {len(common_keys3)} common configurations in cal and dav with top scores at a={a}:")
            print(common_keys3)
    if common_keys and common_keys1 and common_keys2 and common_keys3:
        break
    a += 1

# Expo
df_common = df_clean[df_clean['config_key'].isin(common_keys)]
df_common1 = df_clean[df_clean['config_key'].isin(common_keys1)]
df_common2 = df_clean[df_clean['config_key'].isin(common_keys2)]
df_common3 = df_clean[df_clean['config_key'].isin(common_keys3)]

# Repetitive combination check
if len(df_common) > 1:
    df_common = df_common.loc[df['silhouette_score'].idxmax()]
if len(df_common1) > 1:
    df_common1 = df_common1[df_common1['silhouette_score'] == df_common1['silhouette_score'].max()]
if len(df_common2) > 1:
    df_common2 = df_common2[df_common2['silhouette_score'] == df_common2['silhouette_score'].max()]
if len(df_common3) > 1:
    df_common3 = df_common3[df_common3['calinski_harabasz_score'] == df_common3['silhouette_score'].max()]
df_common.to_pickle(os.path.join(current_folder, "results/best_configs.pkl"))
if df_common1.iloc[0]['config_key'] != df_common.iloc[0]['config_key']:
    df_common1.to_pickle(os.path.join(current_folder, "results/best_configs1.pkl"))
if df_common2.iloc[0]['config_key'] != df_common.iloc[0]['config_key']:
    if df_common2.iloc[0]['config_key'] != df_common1.iloc[0]['config_key']:
        df_common2.to_pickle(os.path.join(current_folder, "results/best_configs2.pkl"))
if df_common3.iloc[0]['config_key'] != df_common.iloc[0]['config_key']:
    if df_common3.iloc[0]['config_key'] != df_common1.iloc[0]['config_key']:
        if df_common3.iloc[0]['config_key'] != df_common2.iloc[0]['config_key']:
            df_common3.to_pickle(os.path.join(current_folder, "results/best_configs3.pkl"))