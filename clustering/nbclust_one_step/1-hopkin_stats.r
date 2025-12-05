if (!require("clustertend")) {
  install.packages("clustertend")
  library(clustertend)
} else {
  library(clustertend)
}

if (!require("here")) {
  install.packages("here")
  library(here)
} else {
  library(here)
}

if (!require("hopkins")) {
  install.packages("hopkins")
  library(hopkins)
} else {
  library(hopkins)
}

file_path <- here("exploratory_data_analisys/df_norm.csv")
data <- read.csv(file_path, header = TRUE, sep = ",")
results_folder <- here("clustering/nbclust_one_step/results")
if (!dir.exists(results_folder)) {
  dir.create(results_folder, recursive = TRUE)
}

columns <- list(
  c('gdp_cons_pop_urban_merged', 'density_pop', 'solar_pow', 'wind_power', 'res_area', 'solar_seas_ind', 'wind_std', 'offshore_wind', 'evi', 'temp'),
  c('gdp_cons_pop_urban_merged', 'density_pop', 'solar_pow', 'wind_power', 'res_area', 'solar_seas_ind', 'wind_std', 'offshore_wind', 'evi', 'temp', 'hydro'),
  c('gdp_cons_pop_urban_merged', 'density_pop', 'solar_pow', 'wind_power', 'res_area', 'solar_seas_ind', 'wind_std', 'offshore_wind', 'evi', 'temp', 'hydro', 'geothermal_potential')
)
names <- c('base', 'hydro', 'geothermal_potential')

txt_path <- file.path(results_folder, paste0("hopkins_stats_cluster.txt"))
if (file.exists(txt_path)) {
  file.remove(txt_path)
}
m <- min(max(30, floor(0.10 * nrow(data))), nrow(data)-1)
print(m)
write(paste("m value utilized:", m), file = txt_path, append = TRUE)
num_iterations <- 10
for (j in 1:length(columns)) {
  cols_to_select <- columns[[j]]
  selected_data <- data[cols_to_select]
  if (j != 1) {
    n <- sum(data$hydro > 0)
    n1 <- sum(data$hydro == 0)
    write(paste("Islands with hydro potential", n, ", islands without hydro potential", n1), file = txt_path, append = TRUE)
  }
  if (j == 3) {
    n <- sum(data$geothermal_potential > 0)
    n1 <- sum(data$geothermal_potential == 0)
    write(paste("Islands with geothermal potential", n, ", islands without geothermal potential", n1), file = txt_path, append = TRUE)
  }
  cluster_hopkins_results <- numeric(num_iterations)
  clustertend_hopkins_results <- numeric(num_iterations)
  for (h in 1:num_iterations) {
    cluster_hopkins_results[h] <- hopkins(selected_data, m = m)
    set.seed(264+h)
    clustertend_hopkins_results[h] <- clustertend::hopkins(selected_data, n = m)$H
  }
  cluster_average_hopkins <- mean(cluster_hopkins_results)
  clustertend_average_hopkins <- mean(clustertend_hopkins_results)
  write(paste("Mean Hopkins value ('cluster' library):", round(cluster_average_hopkins, 6)), file = txt_path, append = TRUE)
  write(paste("Mean Hopkins value ('clustertend' library):", round(clustertend_average_hopkins, 6)), file = txt_path, append = TRUE)
  cat("\n", file = txt_path, append = TRUE)
}