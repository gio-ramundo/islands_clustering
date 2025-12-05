import os
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats

current_folder = os.path.dirname(os.path.abspath(__file__))

df_folder = os.path.join(current_folder, "..", "..")
csv_path=os.path.join(df_folder, 'df_dim_reduction.csv')
df = pd.read_csv(csv_path)

out_folder = os.path.join(current_folder, "..", "results/qq_plot_skewed")
os.makedirs(out_folder, exist_ok = True)

# Skewed variables
sk_col = ['res_area', 'density_pop', 'wind_power', 'offshore_wind', 'geothermal_potential',  'gdp_cons_pop_urban_merged', 'hydro', 'solar_seas_ind']

# Standard comparison distributions
distributions = {
    'Expo': stats.expon,
    'Gamma': stats.gamma,
    'Weibull': stats.weibull_min,
    'Lognormal': stats.lognorm
}

# Iterate for skewed distributions
for col in sk_col:
    x = df[(df[col] > 0)][col]
    plt.figure(figsize = (20, 16))
    for i, (name, dist) in enumerate(distributions.items(), 1):
        plt.subplot(2, 2, i)
        params = dist.fit(x)
        stats.probplot(x, dist=dist, sparams=params[:-2], plot=plt)
        plt.title(f'Q-Q Plot: {name}')
        plt.xlabel('Teoretical Quantiles')
        plt.ylabel('Sample Quantiles')
    plt.tight_layout()
    output_path=os.path.join(out_folder, f"qq_{col}.png")
    plt.savefig(output_path)
    plt.close()