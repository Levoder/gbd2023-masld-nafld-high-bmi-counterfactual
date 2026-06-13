# Independent QC for WPP-rerun block 5 BAPC projection outputs.

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(tidyr)
})

root <- Sys.getenv("GBD_PROJECT_ROOT", unset = "<PROJECT_ROOT>")
tab_dir <- file.path(root, "output", "lrhwp_revision", "tables")
fig_dir <- file.path(root, "output", "lrhwp_revision", "figures")
log_dir <- file.path(root, "output", "lrhwp_revision", "logs")
population_review_dir <- file.path(root, "output", "lrhwp_revision", "population_review")

check_bool <- function(name, ok, detail = "") {
  tibble(check = name, status = ifelse(ok, "PASS", "FAIL"), detail = as.character(detail))
}

scenario <- read_csv(file.path(tab_dir, "block5_projection_scenarios.csv"), show_col_types = FALSE)
summary_2050 <- read_csv(file.path(tab_dir, "block5_2050_summary.csv"), show_col_types = FALSE)
components <- read_csv(file.path(tab_dir, "block5_bapc_projected_rates_components.csv"), show_col_types = FALSE)
model_status <- read_csv(file.path(tab_dir, "block5_bapc_model_status.csv"), show_col_types = FALSE)
reduction <- read_csv(file.path(tab_dir, "block5_reduction_fractions.csv"), show_col_types = FALSE)
population_projection <- read_csv(file.path(tab_dir, "block5_population_proxy_projection.csv"), show_col_types = FALSE)
wpp_reference <- read_csv(file.path(population_review_dir, "wpp2024_population_exposure_20plus_2023_2050_by_location.csv"), show_col_types = FALSE)
wpp_age_review <- read_csv(file.path(tab_dir, "block5_wpp_population_exposure_age_review.csv"), show_col_types = FALSE)

checks <- list()
checks[[length(checks) + 1]] <- check_bool(
  "scenario_row_count",
  nrow(scenario) == 2 * 3 * 61,
  paste(nrow(scenario), "vs", 2 * 3 * 61)
)
checks[[length(checks) + 1]] <- check_bool(
  "component_row_count",
  nrow(components) == 2 * 2 * 61,
  paste(nrow(components), "vs", 2 * 2 * 61)
)
checks[[length(checks) + 1]] <- check_bool(
  "summary_2050_row_count",
  nrow(summary_2050) == 2 * 3,
  paste(nrow(summary_2050), "vs", 2 * 3)
)
checks[[length(checks) + 1]] <- check_bool(
  "model_status_row_count",
  nrow(model_status) == 4,
  paste(nrow(model_status), "vs 4")
)
checks[[length(checks) + 1]] <- check_bool(
  "years_complete",
  setequal(unique(scenario$year), 1990:2050),
  paste(range(scenario$year), collapse = "-")
)
checks[[length(checks) + 1]] <- check_bool(
  "measures_complete",
  setequal(unique(scenario$measure_id), c(1, 2)),
  paste(sort(unique(scenario$measure_id)), collapse = ",")
)
checks[[length(checks) + 1]] <- check_bool(
  "scenarios_complete",
  setequal(unique(scenario$scenario), c(
    "Observed projection",
    "Scenario A: sex-equalized high BMI",
    "Scenario B: high BMI at TMREL"
  )),
  paste(unique(scenario$scenario), collapse = "; ")
)
rate_cols <- c("rate_mean", "rate_lower", "rate_median", "rate_upper")
checks[[length(checks) + 1]] <- check_bool(
  "scenario_rates_non_negative",
  min(as.matrix(scenario[, rate_cols]), na.rm = TRUE) >= 0,
  min(as.matrix(scenario[, rate_cols]), na.rm = TRUE)
)
checks[[length(checks) + 1]] <- check_bool(
  "scenario_intervals_ordered",
  all(scenario$rate_lower <= scenario$rate_mean + 1e-9 & scenario$rate_mean <= scenario$rate_upper + 1e-9),
  sum(!(scenario$rate_lower <= scenario$rate_mean + 1e-9 & scenario$rate_mean <= scenario$rate_upper + 1e-9))
)
future_wide <- scenario %>%
  filter(year >= 2024) %>%
  select(measure_id, year, scenario, rate_mean) %>%
  pivot_wider(names_from = scenario, values_from = rate_mean)
checks[[length(checks) + 1]] <- check_bool(
  "scenario_a_not_above_observed_future",
  all(future_wide[["Scenario A: sex-equalized high BMI"]] <= future_wide[["Observed projection"]] + 1e-9),
  sum(future_wide[["Scenario A: sex-equalized high BMI"]] > future_wide[["Observed projection"]] + 1e-9)
)
checks[[length(checks) + 1]] <- check_bool(
  "scenario_b_not_above_scenario_a_future",
  all(future_wide[["Scenario B: high BMI at TMREL"]] <= future_wide[["Scenario A: sex-equalized high BMI"]] + 1e-9),
  sum(future_wide[["Scenario B: high BMI at TMREL"]] > future_wide[["Scenario A: sex-equalized high BMI"]] + 1e-9)
)
checks[[length(checks) + 1]] <- check_bool(
  "reduction_fractions_in_unit_interval",
  all(reduction$scenario_a_reduction_fraction >= 0 & reduction$scenario_a_reduction_fraction <= 1),
  paste(reduction$scenario_a_reduction_fraction, collapse = ",")
)
checks[[length(checks) + 1]] <- check_bool(
  "model_status_documents_rounded_counts",
  all(grepl("rounded_counts", model_status$model_status)),
  paste(model_status$model_status, collapse = " | ")
)
checks[[length(checks) + 1]] <- check_bool(
  "population_projection_future_complete",
  nrow(population_projection %>% filter(year %in% 2024:2050)) == 27 * 16,
  nrow(population_projection %>% filter(year %in% 2024:2050))
)
checks[[length(checks) + 1]] <- check_bool(
  "population_projection_positive",
  min(population_projection$population, na.rm = TRUE) > 0,
  min(population_projection$population, na.rm = TRUE)
)
checks[[length(checks) + 1]] <- check_bool(
  "future_population_method_is_wpp",
  all(grepl("UN WPP 2024 PopulationExposure", population_projection$population_projection_method[population_projection$year %in% 2024:2050])),
  paste(unique(population_projection$population_projection_method[population_projection$year %in% 2024:2050]), collapse = " | ")
)
pop_2050 <- population_projection %>%
  filter(year == 2050) %>%
  summarise(population = sum(population, na.rm = TRUE)) %>%
  pull(population)
wpp_2050 <- wpp_reference %>%
  filter(year == 2050) %>%
  summarise(population = sum(wpp_exposure_20plus, na.rm = TRUE)) %>%
  pull(population)
checks[[length(checks) + 1]] <- check_bool(
  "population_2050_matches_wpp_reference",
  abs(pop_2050 - wpp_2050) < 1,
  paste(pop_2050, "vs", wpp_2050)
)
checks[[length(checks) + 1]] <- check_bool(
  "wpp_age_review_complete",
  nrow(wpp_age_review %>% filter(year %in% c(2023, 2024:2050))) == 28 * 16,
  nrow(wpp_age_review %>% filter(year %in% c(2023, 2024:2050)))
)

for (ext in c("png", "svg", "pdf", "tiff")) {
  p <- file.path(fig_dir, paste0("block5_fig4_bapc_projection_scenarios.", ext))
  size <- if (file.exists(p)) file.info(p)$size else 0
  checks[[length(checks) + 1]] <- check_bool(
    paste0("figure4_", ext, "_exists_nonempty"),
    size > 5000,
    paste("bytes=", size)
  )
}

qc <- bind_rows(checks)
all_pass <- all(qc$status == "PASS")

write_csv(qc, file.path(tab_dir, "block5_qc_checks.csv"))
write_csv(
  summary_2050,
  file.path(tab_dir, "block5_qc_2050_summary.csv")
)

report_lines <- c(
  "# Block 5 QC report",
  paste0("Generated: ", format(Sys.time(), "%Y-%m-%dT%H:%M:%S")),
  paste0("Overall: ", ifelse(all_pass, "PASS", "FAIL")),
  "",
  "## Checks",
  paste(capture.output(print(qc, n = Inf, width = Inf)), collapse = "\n"),
  "",
  "## 2050 summary",
  paste(capture.output(print(summary_2050, n = Inf, width = Inf)), collapse = "\n"),
  "",
  "## Outputs",
  paste0("- QC checks: `", file.path(tab_dir, "block5_qc_checks.csv"), "`"),
  paste0("- QC 2050 summary: `", file.path(tab_dir, "block5_qc_2050_summary.csv"), "`"),
  paste0("- Report: `", file.path(log_dir, "block5_qc_report.md"), "`")
)

writeLines(report_lines, file.path(log_dir, "block5_qc_report.md"), useBytes = TRUE)

cat("Block 5 QC complete: ", file.path(log_dir, "block5_qc_report.md"), "\n", sep = "")
cat("Overall: ", ifelse(all_pass, "PASS", "FAIL"), "\n", sep = "")
if (!all_pass) {
  print(qc %>% filter(status != "PASS"), n = Inf, width = Inf)
}
