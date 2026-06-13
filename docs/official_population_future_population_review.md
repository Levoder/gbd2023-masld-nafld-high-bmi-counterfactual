# Official Population And Future Population Review

Generated: 2026-06-12

## Sources Checked

- IHME / GHDx GBD 2023 Demographics 1950-2023: https://ghdx.healthdata.org/record/ihme-data/gbd-2023-demographics-1950-2023
- IHME GBD data page: https://www.healthdata.org/research-analysis/gbd-data
- GBD 2023 Cancer Forecasts 2024-2050: https://ghdx.healthdata.org/record/ihme-data/gbd-2023-global-cancer-forecasts-2024-2050
- UN World Population Prospects 2024: https://population.un.org/wpp/
- UN WPP API documentation: https://population.un.org/dataportalapi/index.html

## Local Source Archive

- GHDx/IHME pages cached under `<active_revision>\population_review`.
- GBD 2023 Demographics local raw package copied to `<local_GBD2023_demographics_cache>`.
- GBD 2023 Demographics manifest: `<local_GBD2023_demographics_cache>\manifest_sha256.csv`.
- GBD 2023 Demographics local review tables:
  - `gbd2023_demographics_local_file_inventory.csv`
  - `gbd2023_demographics_zip_inventory.csv`
  - `gbd2023_demographics_mortality_input_2023_20plus_rows.csv`
  - `gbd2023_demographics_mortality_input_2023_20plus_sample_size_vs_wpp_internal.csv`
  - `gbd2023_demographics_mortality_input_2023_20plus_coverage_summary.csv`
- UN WPP download index: `wpp2024_csv_download_index.csv`.
- UN WPP official files downloaded:
  - `WPP2024_PopulationByAge5GroupSex_Medium.csv.gz`
  - `WPP2024_PopulationExposureByAge5GroupSex_Medium.csv.gz`
- WPP location mapping: `wpp2024_location_name_mapping.csv`.

## Access Findings

- The manually downloaded GBD 2023 Demographics 1950-2023 package was reviewed locally. Its information sheet describes mortality input data, stillbirth input/estimate data, TMRLT, and selected appendix tables. It is not a direct GBD Results Tool export of final `measure_name = Population` estimates.
- The mortality input CSV contains `sample_size`, defined in the information sheet as the sample population to which each mortality-rate value applies. This can be used as a source triangulation check, but it should not be treated as a complete official final GBD population/person-years denominator.
- GBD 2023 Cancer Forecasts 2024-2050 are cancer-specific forecasted values, not a generic future population denominator for this MASLD/NAFLD-related BAPC analysis. They should not be used as a replacement population file.
- UN WPP 2024 provides open official population estimates and projections. The data API `data` endpoint requires Bearer token access, but the WPP download center exposes public compressed CSV files via `assets/downloads.json`.

## GBD 2023 Demographics Local Check

The local package contains these top-level files:

- `IHME_GBD_2023_DEMOGRAPHICS_1950_2023_APPENDIX_2_TABLES.zip`
- `IHME_GBD_2023_DEMOGRAPHICS_1950_2023_INFO_SHEET_Y2025M11D04.pdf`
- `IHME_GBD_2023_DEMOGRAPHICS_1950_2023_MORTALITY.zip`
- `IHME_GBD_2023_DEMOGRAPHICS_1950_2023_TABLE_INDEX_Y2025M11D04.XLSX`
- `IHME_GBD_2023_DEMOGRAPHICS_1950_2023_TMRLT_Y2025M06D09.csv`
- `IHME_GBD_2023_DEMOGRAPHICS_1990_2023_STILLBIRTHS.zip`

For 2023, 20+ mortality-input `sample_size` rows were available for 12 of 34 study locations. The aggregate 20+ sample size in those 12 locations was 183,160,324, compared with 188,661,291 in UN WPP 2024 20+ population exposure for the same locations, a relative difference of -2.92%. Coverage was incomplete, and several rows were flagged as outliers, so this check supports denominator-scale triangulation only.

Locations with 2023 20+ mortality-input sample-size coverage:

American Samoa, Guam, Malaysia, Mauritius, Northern Mariana Islands, Palau, Philippines, Seychelles, Sri Lanka, Taiwan, Thailand, Tuvalu.

Locations without 2023 20+ mortality-input sample-size coverage:

Cambodia, China, Cook Islands, Democratic People's Republic of Korea, Fiji, Indonesia, Kiribati, Lao People's Democratic Republic, Maldives, Marshall Islands, Micronesia (Federated States of), Myanmar, Nauru, Niue, Papua New Guinea, Samoa, Solomon Islands, Timor-Leste, Tokelau, Tonga, Vanuatu, Viet Nam.

## WPP 2024 Files Obtained

- `PopulationByAge5GroupSex_Medium`: de facto population as of 1 July, by 5-year age group and sex, in thousands.
- `PopulationExposureByAge5GroupSex_Medium`: population exposure from 1 January to 31 December, by 5-year age group and sex, in thousands.
- For BAPC person-years, `PopulationExposureByAge5GroupSex_Medium` is the closer candidate denominator.

## Location Mapping

All 34 study locations were matched to WPP locations. Non-identical mappings:

- `Democratic People's Republic of Korea` -> `Dem. People's Republic of Korea`
- `Micronesia (Federated States of)` -> `Micronesia (Fed. States of)`
- `Taiwan` -> `China, Taiwan Province of China`

## Key Numerical Review

Internal 20+ population proxy vs UN WPP 2024 34-location aggregate:

| Year | Internal BAPC proxy 20+ | WPP 20+ population exposure | Relative difference |
|---|---:|---:|---:|
| 2023 | 1.630 billion | 1.631 billion | -0.09% |
| 2050 | 2.998 billion | 1.744 billion | +71.87% |

Interpretation:

- The internal proxy is very close to WPP 2024 in 2023, supporting the historical denominator scale.
- The GBD 2023 Demographics mortality-input `sample_size` check is directionally consistent where available, but it is not complete enough to replace a final GBD population export.
- The internal log-linear extrapolation diverges strongly by 2050 and likely overestimates future 20+ person-years.
- Therefore, Block 5 was rerun for the LRH-WP revision using WPP 2024 `PopulationExposureByAge5GroupSex_Medium` for 2024-2050 person-years.

## Completed Block 5 Rerun

Rerun script:

- `<active_revision>\scripts\07_block5_bapc_projection_wpp.R`

QC script:

- `<active_revision>\scripts\07a_block5_qc_wpp.R`

Main rerun outputs:

- `<active_revision>\tables\block5_population_proxy_projection.csv`
- `<active_revision>\tables\block5_projection_scenarios.csv`
- `<active_revision>\tables\block5_2050_summary.csv`
- `<active_revision>\tables\block5_wpp_population_exposure_age_review.csv`
- `<active_revision>\tables\block5_qc_checks.csv`
- `<active_revision>\logs\block5_bapc_projection_report.md`
- `<active_revision>\logs\block5_qc_report.md`

QC result: PASS. WPP exposure coverage was complete for all 34 matched study locations in 2023 and 2024-2050. The 2050 20+ person-years in the rerun population matrix equal the WPP reference total: 1,744,298,695.

Old vs rerun future person-years:

| Year | Old internal proxy | WPP rerun person-years | Relative change |
|---|---:|---:|---:|
| 2024 | 1.729 billion | 1.642 billion | -5.04% |
| 2050 | 2.998 billion | 1.744 billion | -41.82% |

The 2050 age-standardized rate summary changed negligibly because the current Block 5 reporting target is age-standardized rates rather than projected counts. The rerun nevertheless removes the major denominator criticism by replacing the future person-year matrix with official WPP 2024 population exposure.

## Recommended Handling In Manuscript

- Main manuscript: keep 2050 projection as scenario/sensitivity, not as a headline finding.
- Methods: state that the observed period used GBD-derived internal population proxies inferred from total Number/Rate, while the 2024-2050 BAPC person-years were replaced with UN WPP 2024 `PopulationExposureByAge5GroupSex_Medium` medium-variant exposure, summed across 34 matched locations and 20+ five-year age groups.
- Limitation: note that local GBD Demographics files did not provide complete final population denominators for all study locations; WPP 2024 was therefore used for future person-years, but the projection remains a model scenario rather than an IHME official forecast.
