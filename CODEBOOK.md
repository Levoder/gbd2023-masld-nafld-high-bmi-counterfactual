# Codebook

This file lists the tabular files in the package and their column headers. Units and interpretation should be read with the manuscript Methods, table footnotes, and `README.md` method-boundary notes.

## `data/derived_tables/block5_2050_summary.csv`

- `measure_id`
- `measure_name`
- `scenario`
- `year`
- `rate_mean`
- `rate_lower`
- `rate_upper`
- `absolute_reduction_vs_observed`
- `percent_reduction_vs_observed`
- `reduction_fraction`

## `data/derived_tables/block5_bapc_input_age_year.csv`

- `year`
- `age_key`
- `measure_id`
- `measure_name`
- `total_number`
- `high_bmi_attr_number`
- `population`
- `total_rate`
- `high_bmi_attr_rate`

## `data/derived_tables/block5_bapc_model_status.csv`

- `measure_id`
- `measure_name`
- `burden_type`
- `model_status`
- `min_rate`
- `max_rate`

## `data/derived_tables/block5_bapc_projected_rates_components.csv`

- `measure_id`
- `measure_name`
- `burden_type`
- `year`
- `rate_mean`
- `rate_sd`
- `rate_lower`
- `rate_median`
- `rate_upper`
- `model_status`

## `data/derived_tables/block5_population_proxy_projection.csv`

- `year`
- `age_key`
- `population`
- `population_projection_method`

## `data/derived_tables/block5_projection_scenarios.csv`

- `measure_id`
- `measure_name`
- `year`
- `scenario`
- `rate_mean`
- `rate_lower`
- `rate_median`
- `rate_upper`
- `reduction_fraction`
- `scenario_note`
- `period`

## `data/derived_tables/block5_reduction_fractions.csv`

- `measure_id`
- `measure_name`
- `years_used`
- `avoidable_sum`
- `high_bmi_attr_sum`
- `scenario_a_reduction_fraction`
- `scenario_b_reduction_fraction`

## `data/derived_tables/block5_wpp_population_exposure_age_review.csv`

- `year`
- `age_key`
- `population`
- `internal_proxy_population_2023`
- `relative_difference_vs_internal_2023_pct`

## `data/derived_tables/block5_wpp_population_exposure_coverage.csv`

- `Time`
- `matched_locations`
- `expected_locations`

## `data/derived_tables/Table1_counterfactual_2023_country.csv`

- `rank_by_avoidable_dalys`
- `location_id`
- `location_name`
- `population_20plus`
- `dominant_high_exposure_sex_dalys`
- `avoidable_number_main_dalys`
- `avoidable_number_main_lower_dalys`
- `avoidable_number_main_upper_dalys`
- `avoidable_daly_rate_per_100k_20plus`
- `avoidable_pct_of_total_burden_main_dalys`
- `avoidable_pct_of_observed_highbmi_attr_main_dalys`
- `avoidable_number_main_deaths`
- `avoidable_number_main_lower_deaths`
- `avoidable_number_main_upper_deaths`
- `avoidable_death_rate_per_100k_20plus`
- `avoidable_pct_of_total_burden_main_deaths`
- `avoidable_pct_of_observed_highbmi_attr_main_deaths`

## `data/derived_tables/Table2_factor_comparison_2023_country.csv`

- `rank_by_high_bmi_internal_std_daly_rate`
- `location_id`
- `location_name`
- `attr_number_30plus_high_bmi`
- `attr_number_30plus_high_fpg`
- `attr_number_30plus_smoking`
- `internal_std_rate_30plus_high_bmi`
- `internal_std_rate_30plus_high_fpg`
- `internal_std_rate_30plus_smoking`
- `paf_pct_30plus_high_bmi`
- `paf_pct_30plus_high_fpg`
- `paf_pct_30plus_smoking`
- `sdi_mean`
- `sdi_lower`
- `sdi_upper`
- `dominant_factor_by_internal_std_rate`
- `high_bmi_vs_high_fpg_rate_ratio`
- `high_bmi_vs_smoking_rate_ratio`

## `data/derived_tables/Table3A_projection_2050_summary.csv`

- `measure_id`
- `measure_name`
- `scenario`
- `year`
- `rate_mean`
- `rate_lower`
- `rate_upper`
- `absolute_reduction_vs_observed`
- `percent_reduction_vs_observed`
- `reduction_fraction`

## `data/derived_tables/Table3B_uncertainty_psa_summary.csv`

- `measure_id`
- `measure_name`
- `method`
- `n_draws`
- `point`
- `mean`
- `median`
- `lower`
- `upper`
- `prob_gt_zero`
- `mean_negative_cells_per_draw`
- `mean_raw_ratio_gt1_cells_per_draw`

## `data/derived_tables/Table3C_sensitivity_tmrel_summary.csv`

- `section`
- `measure_id`
- `measure_name`
- `scenario`
- `avoidable_number`
- `avoidable_pct_total`
- `avoidable_pct_high_bmi_attr`
- `A_to_B_ratio`

## `data/figure_source/Figure1_source_data.csv`

- `rank_by_avoidable_dalys`
- `location_id`
- `location_name`
- `population_20plus`
- `avoidable_number_main_dalys`
- `avoidable_number_main_lower_dalys`
- `avoidable_number_main_upper_dalys`
- `avoidable_daly_rate_per_100k_20plus`
- `avoidable_pct_of_total_burden_main_dalys`
- `avoidable_pct_of_observed_highbmi_attr_main_dalys`

## `data/figure_source/Graphical_Abstract_LRHWP_source_values.csv`

- `avoidable_deaths`
- `avoidable_dalys`
- `deaths_share_total_pct`
- `dalys_share_total_pct`
- `dalys_share_high_bmi_pct`
- `tmrel_dalys`
- `tmrel_deaths`
- `high_fpg_locations`
- `high_bmi_locations`
- `smoking_locations`
- `dalys_2050_baseline`
- `dalys_2050_scenario_a`
- `dalys_2050_scenario_b`
- `dalys_2050_scenario_a_reduction_pct`
- `dalys_2050_scenario_b_reduction_pct`

## `data/figure_source/lrhwp_figure_manifest.csv`

- `display_order`
- `file_stem`
- `role`
- `caption_note`

## `data/manuscript_tables/Manuscript_Table_1_key_results_three_line.csv`

- `Domain`
- `Endpoint or comparison`
- `Estimate`
- `Unit`
- `Interval or sensitivity range`
- `Interpretation note`

## `data/manuscript_tables/Manuscript_Table_2_country_heterogeneity_three_line.csv`

- `Country or territory`
- `Higher BMI sex`
- `Potentially avoidable DALYs`
- `DALY rate per 100,000 adults aged 20+`
- `Potentially avoidable DALYs, % of total burden`
- `Dominant risk factor`
- `High BMI vs high FPG rate ratio`

## `data/manuscript_tables/Supplementary_Table_S1_country_counterfactual.csv`

- `Rank`
- `Location ID`
- `Country or territory`
- `Population aged 20+`
- `Higher BMI sex`
- `Potentially avoidable DALYs`
- `DALYs lower`
- `DALYs upper`
- `DALY rate per 100,000 adults aged 20+`
- `DALYs, percent of total burden`
- `DALYs, percent of observed high-BMI-attributable burden`
- `Potentially avoidable deaths`
- `Deaths lower`
- `Deaths upper`
- `Death rate per 100,000 adults aged 20+`
- `Deaths, percent of total burden`
- `Deaths, percent of observed high-BMI-attributable burden`

## `data/manuscript_tables/Supplementary_Table_S1_country_counterfactual_three_line.csv`

- `Rank`
- `Location ID`
- `Country or territory`
- `Population aged 20+`
- `Higher BMI sex`
- `Potentially avoidable DALYs`
- `DALYs lower`
- `DALYs upper`
- `DALY rate per 100,000 adults aged 20+`
- `DALYs, % of total burden`
- `DALYs, % of observed high-BMI-attributable burden`
- `Potentially avoidable deaths`
- `Deaths lower`
- `Deaths upper`
- `Death rate per 100,000 adults aged 20+`
- `Deaths, % of total burden`
- `Deaths, % of observed high-BMI-attributable burden`

## `data/manuscript_tables/Supplementary_Table_S2_risk_factor_comparison.csv`

- `Rank`
- `Location ID`
- `Country or territory`
- `SDI, 2023`
- `High BMI DALY number, 30+`
- `High FPG DALY number, 30+`
- `Smoking DALY number, 30+`
- `High BMI internal standardized DALY rate, 30+`
- `High FPG internal standardized DALY rate, 30+`
- `Smoking internal standardized DALY rate, 30+`
- `High BMI PAF, 30+ (%)`
- `High FPG PAF, 30+ (%)`
- `Smoking PAF, 30+ (%)`
- `Dominant factor by rate`
- `High BMI vs high FPG rate ratio`
- `High BMI vs smoking rate ratio`

## `data/manuscript_tables/Supplementary_Table_S2_risk_factor_comparison_three_line.csv`

- `Rank`
- `Location ID`
- `Country or territory`
- `SDI, 2023`
- `High BMI DALY number, 30+`
- `High FPG DALY number, 30+`
- `Smoking DALY number, 30+`
- `High BMI internal standardized DALY rate, 30+`
- `High FPG internal standardized DALY rate, 30+`
- `Smoking internal standardized DALY rate, 30+`
- `High BMI PAF, 30+ (%)`
- `High FPG PAF, 30+ (%)`
- `Smoking PAF, 30+ (%)`
- `Dominant factor by rate`
- `High BMI vs high FPG rate ratio`
- `High BMI vs smoking rate ratio`

## `data/manuscript_tables/Supplementary_Table_S3_projection_uncertainty_sensitivity_three_line.csv`

- `Section`
- `Measure`
- `Scenario or method`
- `Estimate`
- `Lower`
- `Upper`
- `Additional note`

## `data/manuscript_tables/Supplementary_Table_S4_data_sources_reproducibility.csv`

- `Data component`
- `Source or local file`
- `Years`
- `Locations`
- `Measures or variables`
- `Role in manuscript`
- `Key limitation or note`

## `data/manuscript_tables/Supplementary_Table_S4_data_sources_reproducibility_three_line.csv`

- `Data component`
- `Source or local file`
- `Years`
- `Locations`
- `Measures or variables`
- `Role in manuscript`
- `Key limitation or note`

## `data/wpp_population_exposure_review/gbd2023_demographics_local_file_inventory.csv`

- `file_name`
- `bytes`
- `sha256`

## `data/wpp_population_exposure_review/gbd2023_demographics_mortality_input_2023_20plus_coverage_summary.csv`

- `metric`
- `value`

## `data/wpp_population_exposure_review/gbd2023_demographics_mortality_input_2023_20plus_rows.csv`

- `location_id`
- `location_name`
- `sex_name`
- `age_group_id`
- `age_group_name`
- `year_id`
- `sample_size`
- `age_sex_split`
- `outlier`

## `data/wpp_population_exposure_review/gbd2023_demographics_mortality_input_2023_20plus_sample_size_vs_wpp_internal.csv`

- `project_location_name`
- `gbd_mortality_input_sample_size_20plus_2023`
- `mortality_input_rows_20plus`
- `mortality_input_outlier_rows_20plus`
- `mortality_input_nonoutlier_rows_20plus`
- `gbd_mortality_input_nonoutlier_sample_size_20plus_2023`
- `wpp_location_name`
- `wpp_exposure_20plus`
- `internal_proxy_population_20plus_2023`
- `gbd_mortality_input_available_2023`
- `relative_difference_mortality_input_sample_size_vs_wpp_exposure_pct`
- `relative_difference_internal_proxy_vs_wpp_exposure_pct`

## `data/wpp_population_exposure_review/gbd2023_demographics_zip_inventory.csv`

- `zip_file`
- `entry_name`
- `uncompressed_bytes`
- `compressed_bytes`

## `data/wpp_population_exposure_review/wpp2024_csv_download_index.csv`

- `major_group`
- `sub_group`
- `file_name`
- `file_path`
- `url`
- `description`

## `data/wpp_population_exposure_review/wpp2024_location_name_mapping.csv`

- `project_location_name`
- `wpp_location_name`
- `wpp_matched`

## `data/wpp_population_exposure_review/wpp2024_population_20plus_2023_2050_by_location.csv`

- `project_location_name`
- `wpp_location_name`
- `wpp_matched`
- `year`
- `LocID`
- `ISO3_code`
- `wpp_population_20plus`
- `wpp_male_population_20plus`
- `wpp_female_population_20plus`

## `data/wpp_population_exposure_review/wpp2024_population_exposure_20plus_2023_2050_by_location.csv`

- `project_location_name`
- `wpp_location_name`
- `wpp_matched`
- `year`
- `LocID`
- `ISO3_code`
- `wpp_male_exposure_20plus`
- `wpp_female_exposure_20plus`
- `wpp_exposure_20plus`

## `data/wpp_population_exposure_review/wpp2024_vs_internal_bapc_population_exposure_region_2023_2050.csv`

- `year`
- `internal_bapc_population_proxy_20plus`
- `wpp_34_location_exposure_20plus`
- `absolute_difference_internal_minus_wpp_exposure`
- `relative_difference_pct`

## `data/wpp_population_exposure_review/wpp2024_vs_internal_bapc_population_proxy_region_2023_2050.csv`

- `year`
- `internal_bapc_population_proxy_20plus`
- `wpp_34_location_population_20plus`
- `absolute_difference_internal_minus_wpp`
- `relative_difference_pct`

## `data/wpp_population_exposure_review/wpp2024_vs_internal_proxy_2023_by_location.csv`

- `project_location_name`
- `wpp_location_name`
- `wpp_matched`
- `year`
- `LocID`
- `ISO3_code`
- `wpp_population_20plus`
- `wpp_male_population_20plus`
- `wpp_female_population_20plus`
- `internal_proxy_population_20plus_2023`
- `absolute_difference_internal_minus_wpp`
- `relative_difference_pct`

## `qc/block5_qc_2050_summary.csv`

- `measure_id`
- `measure_name`
- `scenario`
- `year`
- `rate_mean`
- `rate_lower`
- `rate_upper`
- `absolute_reduction_vs_observed`
- `percent_reduction_vs_observed`
- `reduction_fraction`

## `qc/block5_qc_checks.csv`

- `check`
- `status`
- `detail`
