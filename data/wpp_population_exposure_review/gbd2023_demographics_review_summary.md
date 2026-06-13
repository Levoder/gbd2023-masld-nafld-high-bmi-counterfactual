# GBD 2023 Demographics Local Review

Generated: 2026-06-12

## Local Package

- Local source folder: `<local_GBD2023_demographics_cache>`
- Top-level files copied: 7
- Zip entries indexed: 24

## Key Finding

The local GBD 2023 Demographics 1950-2023 package is not a direct GBD Results Tool population export. Its information sheet describes mortality input data, stillbirth input/estimate data, TMRLT, and selected appendix tables. The mortality CSV contains `sample_size`, defined as the sample population to which each mortality-rate input value applies. This can support source triangulation, but it should not be treated as the official final GBD population/person-years denominator for all study locations.

## 2023 Mortality-Input Sample-Size Coverage

- Study locations: 34
- Locations with 2023 20+ mortality-input sample-size rows: 12
- Locations without 2023 20+ mortality-input sample-size rows: 22
- Aggregate sample size among available locations: 183160324
- WPP 2024 20+ exposure for the same locations: 188661291
- Relative difference: -2.92%

Missing locations:

Cambodia, China, Cook Islands, Democratic People's Republic of Korea, Fiji, Indonesia, Kiribati, Lao People's Democratic Republic, Maldives, Marshall Islands, Micronesia (Federated States of), Myanmar, Nauru, Niue, Papua New Guinea, Samoa, Solomon Islands, Timor-Leste, Tokelau, Tonga, Vanuatu, Viet Nam

## Files Written

- `gbd2023_demographics_local_file_inventory.csv`
- `gbd2023_demographics_zip_inventory.csv`
- `gbd2023_demographics_mortality_input_2023_20plus_rows.csv`
- `gbd2023_demographics_mortality_input_2023_20plus_sample_size_vs_wpp_internal.csv`
- `gbd2023_demographics_mortality_input_2023_20plus_coverage_summary.csv`

## Largest Available-Location Differences vs WPP Exposure

| project_location_name | gbd_mortality_input_sample_size_20plus_2023 | wpp_exposure_20plus | relative_difference_mortality_input_sample_size_vs_wpp_exposure_pct |
| --- | --- | --- | --- |
| Seychelles | 76150.28 | 93574.00 | -18.62 |
| Tuvalu | 6614.43 | 5882.00 | 12.45 |
| Thailand | 52665202.77 | 56523784.00 | -6.83 |
| Northern Mariana Islands | 33102.23 | 31598.00 | 4.76 |
| Malaysia | 23773606.99 | 24374170.00 | -2.46 |
