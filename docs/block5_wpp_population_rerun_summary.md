# Block 5 WPP 2024 Future Person-Years Rerun Summary

Generated: 2026-06-12

## Objective

Replace the 2024-2050 internally extrapolated future person-years in Block 5 with official UN WPP 2024 `PopulationExposureByAge5GroupSex_Medium` and rerun the BAPC scenario projection for the LRH-WP revision package.

## What Changed

- Historical years 1990-2023: unchanged, using the original GBD-derived internal population proxy inferred from total Number/Rate.
- Future years 2024-2050: replaced with UN WPP 2024 medium-variant population exposure, summed across 34 matched study locations and 20+ five-year age groups.
- Age groups: WPP `20-24` to `90-94` mapped directly; WPP `95-99` and `100+` summed into project `95+`.
- Standardization weights: kept as the 2023 historical internal 20+ population structure to preserve the original Block 5 age-standardized-rate definition.

## Files

- Rerun script: `<active_revision>\scripts\07_block5_bapc_projection_wpp.R`
- QC script: `<active_revision>\scripts\07a_block5_qc_wpp.R`
- Rerun population matrix: `<active_revision>\tables\block5_population_proxy_projection.csv`
- Rerun scenarios: `<active_revision>\tables\block5_projection_scenarios.csv`
- Rerun 2050 summary: `<active_revision>\tables\block5_2050_summary.csv`
- QC checks: `<active_revision>\tables\block5_qc_checks.csv`
- Rerun report: `<active_revision>\logs\block5_bapc_projection_report.md`
- QC report: `<active_revision>\logs\block5_qc_report.md`

## QC Result

Overall: PASS.

- Scenario rows: 366/366.
- Component rows: 244/244.
- Future population rows: 432/432.
- WPP age-review rows: 448/448.
- WPP matched locations: 34/34 for 2023 and every year from 2024 to 2050.
- 2050 WPP person-years check: rerun matrix total 1,744,298,695 equals WPP reference total 1,744,298,695.

## Person-Year Difference

| Year | Old internal proxy | WPP rerun person-years | Relative change |
|---|---:|---:|---:|
| 2024 | 1.729 billion | 1.642 billion | -5.04% |
| 2050 | 2.998 billion | 1.744 billion | -41.82% |

## 2050 Rate Summary After Rerun

| Measure | Scenario | 2050 rate mean | Percent reduction vs baseline |
|---|---|---:|---:|
| Deaths | Baseline projection | 1.454 | 0.00% |
| Deaths | Scenario A: sex-equalized high BMI | 1.440 | 0.98% |
| Deaths | Scenario B: high BMI at TMREL | 1.336 | 8.14% |
| DALYs | Baseline projection | 47.131 | 0.00% |
| DALYs | Scenario A: sex-equalized high BMI | 46.245 | 1.88% |
| DALYs | Scenario B: high BMI at TMREL | 39.315 | 16.58% |

## Interpretation

The denominator problem has been corrected for future person-years. The age-standardized rate projections changed negligibly because Block 5 reports age-standardized rates, not projected counts; in this BAPC setup, replacing future person-years mainly corrects the exposure matrix and any count-derived interpretation rather than changing the reported standardized rate trend. The manuscript should state that future person-years were taken from UN WPP 2024 population exposure, while the 2050 estimates remain scenario projections and not official IHME forecasts.
