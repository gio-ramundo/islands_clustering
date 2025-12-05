if (!require("NbClust")) {
  install.packages("NbClust")
  library(NbClust)
} else {
  library(NbClust)
}

if (!require("here")) {
  install.packages("here")
  library(here)
} else {
  library(here)
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

txt_path <- file.path(results_folder, paste0("optimal_number_cluster.txt"))
if (file.exists(txt_path)) {
  file.remove(txt_path)
}
for (j in 1:length(columns)) {
  write(paste("Columns group", names[j], ":"), file = txt_path, append = TRUE)
  cols_to_select <- columns[[j]]
  selected_data <- data[cols_to_select]
  set.seed(123) # For reproducibility
  res <- NbClust(
    data = selected_data,
    distance = "euclidean",
    min.nc = 2,
    max.nc = 25,
    method = "kmeans"
  )
  recommended_clusters <- res$Best.nc[1, ]
  cluster_counts <- table(recommended_clusters)
  cluster_counts_ordered <- cluster_counts[order(as.numeric(names(cluster_counts)))]
  write(paste("Among all indices:"), file = txt_path, append = TRUE)
  for (num_cluster in names(cluster_counts_ordered)) {
    count <- cluster_counts_ordered[num_cluster]
    write(paste(count, "proposed ", num_cluster, " as the best number of clusters"), file = txt_path, append = TRUE)
  }
  optimal_cluster_num <- as.numeric(names(which.max(cluster_counts)))
  write(paste("According to the majority rule, the best number of clusters is", optimal_cluster_num), file = txt_path, append = TRUE)
  cat("\n", file = txt_path, append = TRUE)
}