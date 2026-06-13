# Block 5: BAPC projection and deterministic counterfactual scenarios.
# LRH-WP revision rerun: replace future person-years with UN WPP 2024
# PopulationExposureByAge5GroupSex_Medium, medium variant.

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(tidyr)
  library(stringr)
  library(ggplot2)
  library(patchwork)
  library(scales)
  library(BAPC)
  library(INLA)
})

root <- Sys.getenv("GBD_PROJECT_ROOT", unset = "<PROJECT_ROOT>")
input_tab_dir <- file.path(root, "output", "tables")
tab_dir <- file.path(root, "output", "lrhwp_revision", "tables")
fig_dir <- file.path(root, "output", "lrhwp_revision", "figures")
log_dir <- file.path(root, "output", "lrhwp_revision", "logs")
clean_dir <- file.path(root, "output", "lrhwp_revision", "clean")
population_review_dir <- file.path(root, "output", "lrhwp_revision", "population_review")
dir.create(tab_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(fig_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(log_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(clean_dir, recursive = TRUE, showWarnings = FALSE)

age_levels <- c(paste(seq(20, 90, 5), seq(24, 94, 5), sep = "-"), "95+")
observed_years <- 1990:2023
future_years <- 2024:2050
all_years <- 1990:2050
per_100k <- 100000

age_cells_path <- file.path(input_tab_dir, "block3_counterfactual_age_cells.csv")
country_year_path <- file.path(input_tab_dir, "block3_counterfactual_country_year.csv")
population_path <- file.path(input_tab_dir, "population_weights_20plus.csv")
wpp_exposure_path <- file.path(population_review_dir, "WPP2024_PopulationExposureByAge5GroupSex_Medium.csv.gz")
wpp_mapping_path <- file.path(population_review_dir, "wpp2024_location_name_mapping.csv")

age_cells <- read_csv(age_cells_path, show_col_types = FALSE)
country_year <- read_csv(country_year_path, show_col_types = FALSE)
population <- read_csv(population_path, show_col_types = FALSE)
wpp_mapping <- read_csv(wpp_mapping_path, show_col_types = FALSE)

stopifnot(all(age_levels %in% unique(age_cells$age_key)))
stopifnot(all(observed_years %in% unique(age_cells$year)))

historical_burden <- age_cells %>%
  filter(age_key %in% age_levels, year %in% observed_years) %>%
  mutate(age_key = factor(age_key, levels = age_levels)) %>%
  group_by(year, age_key, measure_id, measure_name) %>%
  summarise(
    total_number = sum(total_number_h + total_number_l, na.rm = TRUE),
    high_bmi_attr_number = sum(attr_obs_number_h + attr_obs_number_l, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  arrange(measure_id, year, age_key)

historical_population <- population %>%
  filter(age_key %in% age_levels, year %in% observed_years) %>%
  mutate(age_key = factor(age_key, levels = age_levels)) %>%
  group_by(year, age_key) %>%
  summarise(population = sum(population, na.rm = TRUE), .groups = "drop") %>%
  arrange(year, age_key)

wpp_future_population <- read_csv(
  wpp_exposure_path,
  col_select = c(Location, Time, AgeGrpStart, AgeGrp, PopTotal),
  show_col_types = FALSE
) %>%
  filter(
    Location %in% wpp_mapping$wpp_location_name,
    Time %in% c(2023, future_years),
    AgeGrpStart >= 20
  ) %>%
  mutate(
    age_key = if_else(AgeGrpStart >= 95, "95+", AgeGrp),
    population = PopTotal * 1000
  ) %>%
  filter(age_key %in% age_levels) %>%
  group_by(year = Time, age_key) %>%
  summarise(population = sum(population, na.rm = TRUE), .groups = "drop") %>%
  mutate(age_key = factor(age_key, levels = age_levels)) %>%
  arrange(year, age_key)

wpp_coverage <- read_csv(
  wpp_exposure_path,
  col_select = c(Location, Time, AgeGrpStart),
  show_col_types = FALSE
) %>%
  filter(
    Location %in% wpp_mapping$wpp_location_name,
    Time %in% c(2023, future_years),
    AgeGrpStart >= 20
  ) %>%
  distinct(Location, Time) %>%
  count(Time, name = "matched_locations") %>%
  mutate(expected_locations = nrow(wpp_mapping))

future_population <- wpp_future_population %>%
  filter(year %in% future_years) %>%
  mutate(population_projection_method = "UN WPP 2024 PopulationExposureByAge5GroupSex_Medium, medium variant, 34 matched locations")

population_all <- bind_rows(
  historical_population %>%
    mutate(population_projection_method = "observed proxy from D_total Number/Rate"),
  future_population
) %>%
  mutate(age_key = factor(age_key, levels = age_levels)) %>%
  arrange(year, age_key)

std_weights <- historical_population %>%
  filter(year == 2023) %>%
  arrange(age_key) %>%
  mutate(weight = population / sum(population)) %>%
  pull(weight)
names(std_weights) <- age_levels

make_matrix <- function(df, value_col, fill_future = NA_real_) {
  grid <- expand_grid(year = all_years, age_key = factor(age_levels, levels = age_levels))
  mat_df <- grid %>%
    left_join(df %>% select(year, age_key, value = all_of(value_col)), by = c("year", "age_key")) %>%
    mutate(value = if_else(year %in% future_years & is.na(value), fill_future, value)) %>%
    arrange(year, age_key)
  mat <- matrix(mat_df$value, nrow = length(all_years), ncol = length(age_levels), byrow = TRUE)
  rownames(mat) <- as.character(all_years)
  colnames(mat) <- age_levels
  mat
}

extract_agestd_rate <- function(result, measure_id, measure_name, burden_type, model_status) {
  qres <- qapc(result, percentiles = c(0.025, 0.5, 0.975))
  rates <- as.data.frame(agestd.rate(qres))
  rates$year <- as.integer(rownames(rates))
  tibble(
    measure_id = measure_id,
    measure_name = measure_name,
    burden_type = burden_type,
    year = rates$year,
    rate_mean = pmax(0, rates$mean * per_100k),
    rate_sd = rates$sd * per_100k,
    rate_lower = pmax(0, rates[["0.025Q"]] * per_100k),
    rate_median = pmax(0, rates[["0.5Q"]] * per_100k),
    rate_upper = pmax(0, rates[["0.975Q"]] * per_100k),
    model_status = model_status
  )
}

run_bapc_model <- function(cases_mat, pyrs_mat, measure_id, measure_name, burden_type) {
  model_status <- "bapc_fractional_counts"
  cases_df <- as.data.frame(cases_mat, check.names = FALSE)
  pyrs_df <- as.data.frame(pyrs_mat, check.names = FALSE)
  fit <- tryCatch({
    apc <- APCList(cases_df, pyrs_df, gf = 5)
    BAPC(
      apc,
      predict = list(npredict = length(future_years), retro = FALSE),
      secondDiff = FALSE,
      stdweight = std_weights,
      verbose = FALSE
    )
  }, error = function(e) {
    message("BAPC fractional-count fit failed for ", burden_type, " ", measure_name, ": ", e$message)
    model_status <<- paste0("bapc_rounded_counts_after_fractional_error: ", e$message)
    rounded <- cases_mat
    rounded[!is.na(rounded)] <- round(pmax(rounded[!is.na(rounded)], 0))
    rounded_df <- as.data.frame(rounded, check.names = FALSE)
    apc <- APCList(rounded_df, pyrs_df, gf = 5)
    BAPC(
      apc,
      predict = list(npredict = length(future_years), retro = FALSE),
      secondDiff = FALSE,
      stdweight = std_weights,
      verbose = FALSE
    )
  })
  extract_agestd_rate(fit, measure_id, measure_name, burden_type, model_status)
}

projection_parts <- list()
model_status_rows <- list()

for (mid in sort(unique(historical_burden$measure_id))) {
  mname <- historical_burden %>% filter(measure_id == mid) %>% pull(measure_name) %>% unique()
  hist_m <- historical_burden %>% filter(measure_id == mid)
  pyrs_mat <- make_matrix(population_all, "population", fill_future = NA_real_)

  for (btype in c("total", "high_bmi_attr")) {
    vcol <- if (btype == "total") "total_number" else "high_bmi_attr_number"
    cases_mat <- make_matrix(hist_m, vcol, fill_future = NA_real_)
    res <- run_bapc_model(cases_mat, pyrs_mat, mid, mname, btype)
    projection_parts[[paste(mid, btype, sep = "_")]] <- res
    model_status_rows[[paste(mid, btype, sep = "_")]] <- tibble(
      measure_id = mid,
      measure_name = mname,
      burden_type = btype,
      model_status = unique(res$model_status),
      min_rate = min(res$rate_mean, na.rm = TRUE),
      max_rate = max(res$rate_mean, na.rm = TRUE)
    )
  }
}

bapc_rates <- bind_rows(projection_parts)
model_status <- bind_rows(model_status_rows)

reduction_fractions <- country_year %>%
  filter(year >= 2019, year <= 2023) %>%
  group_by(measure_id, measure_name) %>%
  summarise(
    years_used = "2019-2023",
    avoidable_sum = sum(avoidable_number_main, na.rm = TRUE),
    high_bmi_attr_sum = sum(observed_attr_20plus_mf, na.rm = TRUE),
    scenario_a_reduction_fraction = avoidable_sum / high_bmi_attr_sum,
    scenario_b_reduction_fraction = 1,
    .groups = "drop"
  )

wide_rates <- bapc_rates %>%
  select(measure_id, measure_name, burden_type, year, rate_mean, rate_lower, rate_median, rate_upper) %>%
  pivot_wider(
    names_from = burden_type,
    values_from = c(rate_mean, rate_lower, rate_median, rate_upper)
  ) %>%
  left_join(reduction_fractions, by = c("measure_id", "measure_name"))

scenario_rows <- bind_rows(
  wide_rates %>%
    transmute(
      measure_id, measure_name, year,
      scenario = "Observed projection",
      rate_mean = rate_mean_total,
      rate_lower = rate_lower_total,
      rate_median = rate_median_total,
      rate_upper = rate_upper_total,
      reduction_fraction = 0,
      scenario_note = "BAPC total-burden continuation"
    ),
  wide_rates %>%
    transmute(
      measure_id, measure_name, year,
      scenario = "Scenario A: sex-equalized high BMI",
      rate_mean = pmax(0, rate_mean_total - scenario_a_reduction_fraction * rate_mean_high_bmi_attr),
      rate_lower = pmax(0, rate_lower_total - scenario_a_reduction_fraction * rate_upper_high_bmi_attr),
      rate_median = pmax(0, rate_median_total - scenario_a_reduction_fraction * rate_median_high_bmi_attr),
      rate_upper = pmax(0, rate_upper_total - scenario_a_reduction_fraction * rate_lower_high_bmi_attr),
      reduction_fraction = scenario_a_reduction_fraction,
      scenario_note = "Total-burden projection minus deterministic sex-equalization fraction of high-BMI-attributable projection"
    ),
  wide_rates %>%
    transmute(
      measure_id, measure_name, year,
      scenario = "Scenario B: high BMI at TMREL",
      rate_mean = pmax(0, rate_mean_total - rate_mean_high_bmi_attr),
      rate_lower = pmax(0, rate_lower_total - rate_upper_high_bmi_attr),
      rate_median = pmax(0, rate_median_total - rate_median_high_bmi_attr),
      rate_upper = pmax(0, rate_upper_total - rate_lower_high_bmi_attr),
      reduction_fraction = 1,
      scenario_note = "Total-burden projection minus full high-BMI-attributable projection; theoretical TMREL upper bound"
    )
) %>%
  mutate(
    scenario = factor(
      scenario,
      levels = c(
        "Observed projection",
        "Scenario A: sex-equalized high BMI",
        "Scenario B: high BMI at TMREL"
      )
    ),
    period = if_else(year <= 2023, "Observed fit", "Projected")
  ) %>%
  arrange(measure_id, scenario, year)

historical_observed <- scenario_rows %>%
  filter(scenario == "Observed projection", year <= 2023)

future_scenarios <- scenario_rows %>%
  filter(year >= 2023)

summary_2050 <- scenario_rows %>%
  filter(year == 2050) %>%
  group_by(measure_id, measure_name) %>%
  mutate(
    observed_rate_2050 = rate_mean[scenario == "Observed projection"][1],
    absolute_reduction_vs_observed = observed_rate_2050 - rate_mean,
    percent_reduction_vs_observed = absolute_reduction_vs_observed / observed_rate_2050 * 100
  ) %>%
  ungroup() %>%
  select(
    measure_id, measure_name, scenario, year,
    rate_mean, rate_lower, rate_upper,
    absolute_reduction_vs_observed,
    percent_reduction_vs_observed,
    reduction_fraction
  )

bapc_input <- historical_burden %>%
  left_join(historical_population, by = c("year", "age_key")) %>%
  mutate(
    total_rate = total_number / population * per_100k,
    high_bmi_attr_rate = high_bmi_attr_number / population * per_100k
  )

population_projection <- population_all
wpp_population_age_review <- wpp_future_population %>%
  left_join(
    historical_population %>% filter(year == 2023) %>% select(age_key, internal_proxy_population_2023 = population),
    by = "age_key"
  ) %>%
  mutate(
    relative_difference_vs_internal_2023_pct = if_else(
      year == 2023,
      (population - internal_proxy_population_2023) / internal_proxy_population_2023 * 100,
      NA_real_
    )
  )

write_csv(bapc_input, file.path(tab_dir, "block5_bapc_input_age_year.csv"))
write_csv(population_projection, file.path(tab_dir, "block5_population_proxy_projection.csv"))
write_csv(wpp_population_age_review, file.path(tab_dir, "block5_wpp_population_exposure_age_review.csv"))
write_csv(wpp_coverage, file.path(tab_dir, "block5_wpp_population_exposure_coverage.csv"))
write_csv(bapc_rates, file.path(tab_dir, "block5_bapc_projected_rates_components.csv"))
write_csv(model_status, file.path(tab_dir, "block5_bapc_model_status.csv"))
write_csv(reduction_fractions, file.path(tab_dir, "block5_reduction_fractions.csv"))
write_csv(scenario_rows, file.path(tab_dir, "block5_projection_scenarios.csv"))
write_csv(summary_2050, file.path(tab_dir, "block5_2050_summary.csv"))

saveRDS(
  list(
    bapc_rates = bapc_rates,
    scenario_rows = scenario_rows,
    reduction_fractions = reduction_fractions,
    model_status = model_status,
    std_weights = std_weights
  ),
  file.path(clean_dir, "block5_bapc_projection_objects.rds")
)

plot_df <- future_scenarios %>%
  mutate(
    measure_label = factor(if_else(measure_id == 1, "Deaths", "DALYs"), levels = c("Deaths", "DALYs")),
    scenario_label = recode(
      as.character(scenario),
      "Observed projection" = "Observed projection",
      "Scenario A: sex-equalized high BMI" = "Scenario A",
      "Scenario B: high BMI at TMREL" = "Scenario B"
    )
  )

hist_df <- historical_observed %>%
  mutate(measure_label = factor(if_else(measure_id == 1, "Deaths", "DALYs"), levels = c("Deaths", "DALYs")))

pal <- c(
  "Observed projection" = "#263238",
  "Scenario A" = "#2A6FBB",
  "Scenario B" = "#B65C00"
)

theme_set(
  theme_classic(base_size = 7, base_family = "Arial") +
    theme(
      axis.line = element_line(linewidth = 0.35, colour = "black"),
      axis.ticks = element_line(linewidth = 0.35, colour = "black"),
      legend.title = element_blank(),
      legend.text = element_text(size = 6.2),
      strip.text = element_text(size = 7, face = "bold"),
      strip.background = element_blank(),
      plot.title = element_text(size = 8.2, face = "bold"),
      panel.grid.major.y = element_line(linewidth = 0.25, colour = "#E5E7EB"),
      panel.grid.major.x = element_blank()
    )
)

fig4 <- ggplot() +
  geom_line(
    data = hist_df,
    aes(x = year, y = rate_mean),
    linewidth = 0.45,
    colour = "#6B7280"
  ) +
  geom_ribbon(
    data = plot_df,
    aes(x = year, ymin = rate_lower, ymax = rate_upper, fill = scenario_label),
    alpha = 0.075,
    colour = NA
  ) +
  geom_line(
    data = plot_df,
    aes(x = year, y = rate_mean, colour = scenario_label),
    linewidth = 0.55
  ) +
  geom_vline(xintercept = 2023, linewidth = 0.3, linetype = "dashed", colour = "#6B7280") +
  facet_wrap(~ measure_label, scales = "free_y", nrow = 1) +
  scale_colour_manual(values = pal) +
  scale_fill_manual(values = pal) +
  scale_x_continuous(breaks = c(1990, 2000, 2010, 2020, 2030, 2040, 2050), limits = c(1990, 2050)) +
  labs(
    title = "Figure 4. BAPC scenario projection of MASLD-related burden to 2050",
    x = NULL,
    y = "Age-standardized 20+ rate per 100,000"
  ) +
  guides(fill = "none", colour = guide_legend(override.aes = list(linewidth = 0.8))) +
  theme(legend.position = "bottom")

fig_base <- file.path(fig_dir, "block5_fig4_bapc_projection_scenarios")
svglite::svglite(paste0(fig_base, ".svg"), width = 183 / 25.4, height = 105 / 25.4)
print(fig4)
dev.off()
grDevices::cairo_pdf(paste0(fig_base, ".pdf"), width = 183 / 25.4, height = 105 / 25.4, family = "Arial")
print(fig4)
dev.off()
ragg::agg_png(paste0(fig_base, ".png"), width = 183 / 25.4, height = 105 / 25.4, units = "in", res = 450)
print(fig4)
dev.off()
ragg::agg_tiff(paste0(fig_base, ".tiff"), width = 183 / 25.4, height = 105 / 25.4, units = "in", res = 600, compression = "lzw")
print(fig4)
dev.off()

fmt <- function(x, digits = 3) format(round(x, digits), nsmall = digits, trim = TRUE)

report_lines <- c(
  "# Block 5 BAPC projection report",
  paste0("Generated: ", format(Sys.time(), "%Y-%m-%dT%H:%M:%S")),
  "",
  "## Quality reminders",
  "- Q23: Rscript is not on PATH; this run used the discovered R 4.5.2 executable. INLA and BAPC were installed and loaded.",
  "- Q24: Future person-years were replaced with UN WPP 2024 PopulationExposureByAge5GroupSex_Medium, medium variant, summed across the 34 matched study locations.",
  "- Q25: BAPC intervals are model-projection intervals from GBD point estimates; they do not include draw-level GBD uncertainty, RR-PSA, or lean-MASLD sensitivity.",
  "- Q26: Scenario A and B are nested deterministic counterfactual layers and must not be added.",
  "- Q27: INLA did not fit fractional GBD expected counts stably; this run documents the failure and uses rounded counts for the BAPC likelihood, with non-negative truncation of rate lower bounds.",
  "",
  "## Model status",
  paste(capture.output(print(model_status, n = Inf, width = Inf)), collapse = "\n"),
  "",
  "## Scenario definitions",
  "- Observed projection: BAPC projection of total MASLD-related burden.",
  "- Scenario A: observed total projection minus the 2019-2023 mean sex-equalization avoidable fraction of the projected high-BMI-attributable component.",
  "- Scenario B: observed total projection minus the full projected high-BMI-attributable component, interpreted as the TMREL theoretical upper bound.",
  "",
  "## Reduction fractions",
  paste(capture.output(print(reduction_fractions, n = Inf, width = Inf)), collapse = "\n"),
  "",
  "## WPP population exposure coverage",
  paste(capture.output(print(wpp_coverage, n = Inf, width = Inf)), collapse = "\n"),
  "",
  "## Population totals",
  paste(capture.output(print(population_projection %>% group_by(year, population_projection_method) %>% summarise(population = sum(population), .groups = "drop") %>% filter(year %in% c(2023, 2024, 2050)), n = Inf, width = Inf)), collapse = "\n"),
  "",
  "## 2050 summary",
  paste(capture.output(print(summary_2050, n = Inf, width = Inf)), collapse = "\n"),
  "",
  "## Outputs",
  paste0("- BAPC input: `", file.path(tab_dir, "block5_bapc_input_age_year.csv"), "`"),
  paste0("- Population projection/person-years: `", file.path(tab_dir, "block5_population_proxy_projection.csv"), "`"),
  paste0("- WPP age review: `", file.path(tab_dir, "block5_wpp_population_exposure_age_review.csv"), "`"),
  paste0("- WPP coverage: `", file.path(tab_dir, "block5_wpp_population_exposure_coverage.csv"), "`"),
  paste0("- Component rates: `", file.path(tab_dir, "block5_bapc_projected_rates_components.csv"), "`"),
  paste0("- Scenario rates: `", file.path(tab_dir, "block5_projection_scenarios.csv"), "`"),
  paste0("- 2050 summary: `", file.path(tab_dir, "block5_2050_summary.csv"), "`"),
  paste0("- Figure 4: `", paste0(fig_base, ".png"), "`"),
  paste0("- Report: `", file.path(log_dir, "block5_bapc_projection_report.md"), "`")
)

writeLines(report_lines, file.path(log_dir, "block5_bapc_projection_report.md"), useBytes = TRUE)

cat("Block 5 complete: ", file.path(log_dir, "block5_bapc_projection_report.md"), "\n", sep = "")
cat("Figure 4: ", paste0(fig_base, ".png"), "\n", sep = "")
