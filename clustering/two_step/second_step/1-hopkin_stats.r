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
txt_folder <- here("clustering/two_step/second_step/results/hopkins_stats")
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
  txt_path <- file.path(txt_folder, paste0("hopkins_stats_cluster_", label, ".txt"))
  if (file.exists(txt_path)) {
    file.remove(txt_path)
  }
  filtered_data <- subset(data, data$consumption_label == label)
  m <- min(max(30, floor(0.10 * nrow(filtered_data))), nrow(filtered_data) - 1)
  print(m)
  write(paste("m value utilized:", m), file = txt_path, append = TRUE)
  num_iterations <- 10
  for (j in 1:length(columns)) {
    cols_to_select <- columns[[j]]
    selected_data <- filtered_data[cols_to_select]
    if (j != 1) {
      n <- sum(filtered_data$hydro > 0)
      n1 <- sum(filtered_data$hydro == 0)
      write(paste("Cluster", label, ", islands with hydro potential", n, ", islands without hydro potential", n1), file = txt_path, append = TRUE)
    }
    if (j == 3) {
      n <- sum(filtered_data$geothermal_potential > 0)
      n1 <- sum(filtered_data$geothermal_potential == 0)
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
}