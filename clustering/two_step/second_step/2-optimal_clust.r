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
txt_folder <- here("clustering/two_step/second_step/results/optimal_clust")
if (!dir.exists(txt_folder)) {
  dir.create(txt_folder, recursive = TRUE)
}

columns <- list(
  c('density_pop', 'solar_pow', 'wind_power', 'res_area', 'solar_seas_ind', 'wind_std', 'offshore_wind', 'evi', 'temp'),
  c('density_pop', 'solar_pow', 'wind_power', 'res_area', 'solar_seas_ind', 'wind_std', 'offshore_wind', 'evi', 'temp', 'hydro'),
  c('density_pop', 'solar_pow', 'wind_power', 'res_area', 'solar_seas_ind', 'wind_std', 'offshore_wind', 'evi', 'temp', 'hydro', 'geothermal_potential')
)
names <- c('base', 'hydro', 'geothermal_potential')

label_list <- list("XS", "S", "M", "L")

for (label in label_list) {
  filtered_data <- subset(data, data$consumption_label == label)
  txt_path <- file.path(txt_folder, paste0("optimal_number_cluster_", label, ".txt"))
  if (file.exists(txt_path)) {
    file.remove(txt_path)
  }
  for (j in 1:length(columns)) {
    write(paste("Columns group", names[j], ":"), file = txt_path, append = TRUE)
    cols_to_select <- columns[[j]]
    selected_data <- filtered_data[cols_to_select]
    set.seed(123) # For reproducibility
    if (nrow(selected_data) < 50) {
      max = 10
    } else{
      max = 20
    }
    res <- NbClust(
      data = selected_data,
      distance = "euclidean",
      min.nc = 2,
      max.nc = max,
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
}