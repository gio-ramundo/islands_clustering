import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import PowerTransformer
from sklearn.preprocessing import StandardScaler, RobustScaler, FunctionTransformer
from sklearn.pipeline import Pipeline

current_folder = os.path.dirname(os.path.abspath(__file__))
df_folder = os.path.join(current_folder, "..")
csv_path = os.path.join(df_folder, "df_dim_reduction.csv")
df = pd.read_csv(csv_path)

robust_features = ['solar_pow','temp', 'wind_std', 'evi']
robscaler = RobustScaler()
for col in robust_features:
    df[col] = robscaler.fit_transform(df[[col]])

yeo_features = ['gdp_cons_pop_urban_merged', 'wind_power']
yeo_pipeline = Pipeline([
        ('yeojohnson', PowerTransformer(method='yeo-johnson', standardize= False)),
        ('robust_scaler', robscaler)
    ])
for col in yeo_features:
    df[col] = yeo_pipeline.fit_transform(df[[col]])

log_robust_features = ['res_area', 'density_pop', 'solar_seas_ind']
log_pipeline = Pipeline([
        ('log_transformer', FunctionTransformer(np.log1p, validate=True)),
        ('robust_scaler', robscaler)
    ])
for col in log_robust_features:
    df[col] = log_pipeline.fit_transform(df[[col]])

zeros_log=['offshore_wind', 'hydro']
standscaler = StandardScaler(with_mean=False)
for col in zeros_log:
    zero_mask = df[col] <= 0
    df.loc[zero_mask, col] = np.nan
    df[col] = np.log1p(df[col])
    df[col] = standscaler.fit_transform(df[[col]])
    df.loc[zero_mask, col] = 0
    
yeo_pipeline = Pipeline([
        ('yeojohnson', PowerTransformer(method='yeo-johnson', standardize= False)),
        ('standard_scaler', standscaler)
    ])
zero_mask = df['geothermal_potential'] <= 0
df.loc[zero_mask, 'geothermal_potential'] = np.nan
df['geothermal_potential'] = yeo_pipeline.fit_transform(df[['geothermal_potential']])
df.loc[zero_mask, 'geothermal_potential'] = 0
df['geothermal_potential'] = df['geothermal_potential']

# Expo
output_folder = os.path.join(current_folder, '..')
output_path = os.path.join(output_folder, 'df_norm.csv')
df.to_csv(output_path, index=False, encoding='utf-8')