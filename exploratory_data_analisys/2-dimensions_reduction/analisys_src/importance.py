import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

current_folder = os.path.dirname(os.path.abspath(__file__))

df_folder = os.path.join(current_folder, "..", "..")
csv_path = os.path.join(df_folder, 'df_dim_reduction.csv')
df = pd.read_csv(csv_path)
relevant_col = [col for col in df.columns if col != 'ALL_Uniq']

# Relevant features
target_features = ['res_area', 'solar_pow', 'wind_power', 'gdp_cons_pop_urban_merged']

out_folder = os.path.join(current_folder, "..", "results")
os.makedirs(out_folder, exist_ok = True)
output_folder = os.path.join(out_folder, "importance")
os.makedirs(output_folder, exist_ok = True)

for target_feature in target_features:
    X = df[relevant_col].select_dtypes(include='number').drop(columns=target_features)
    y = df[target_feature]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(random_state=42)
    model.fit(X_train, y_train)
    # Calculate importances, create dataframe and plot, export
    importances = model.feature_importances_
    features = X.columns
    feat_importance_df = pd.DataFrame({
        'feature': features,
        'importance': importances
    }).sort_values(by='importance', ascending=False)
    plt.figure(figsize=(12, 10))
    sns.barplot(data=feat_importance_df, x='importance', y='feature', palette='viridis')
    plt.xlabel('')
    plt.ylabel('')
    plt.tight_layout()
    output_path=os.path.join(output_folder, f'{target_feature}_importance.png')
    plt.savefig(output_path)
    plt.close()