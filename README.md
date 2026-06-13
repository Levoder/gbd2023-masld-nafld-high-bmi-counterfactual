# GBD 2023 MASLD/NAFLD-related liver burden counterfactual analysis

This repository-ready package supports the manuscript:

**Sex-equalized high-BMI exposure and potentially avoidable MASLD/NAFLD-related liver burden in Asia and Oceania: a GBD 2023 counterfactual analysis**

## Scope

The package contains derived tables, figure source files, scripts, WPP population-exposure review files, QC logs, manuscript table files, and final figure outputs from the active revision package `lrhwp_revision`.

This project is a **calibrated exposure-scaling counterfactual anchored to GBD 2023 estimates**. It is not a full IHME PAF recalculation and not a complete continuous RR-integral PAF model. The 2050 results are an internal BAPC scenario projection using WPP 2024 future person-years, not an IHME official forecast.

## Main method boundaries

- Scenario A: sex-equalized high-BMI counterfactual.
- Scenario B: high-BMI-at-TMREL theoretical upper bound.
- Scenario A and Scenario B are nested and non-additive.
- Risk-factor estimates for high BMI, high FPG, and smoking are non-additive and non-mutually exclusive.
- Internal standardized rates are internal 30+ standardized rates, not official GBD ASRs.
- Uncertainty is summary-UI proxy / sensitivity interval uncertainty, not GBD draw-level uncertainty.
- Outcomes are GBD NAFLD/MASLD-related cirrhosis and liver cancer burden, not the full modern MASLD disease spectrum.

## Repository structure

- `data/derived_tables/`: derived analytical tables used in the manuscript and projections.
- `data/manuscript_tables/`: final manuscript and supplementary table files, including three-line table exports.
- `data/figure_source/`: source values and manifest used to map figures to analytical outputs.
- `data/wpp_population_exposure_review/`: WPP 2024 review and population-exposure proxy files used for projection QC.
- `figures/final/`: final main and supplementary figure files.
- `figures/graphical_abstract/`: graphical abstract files and source values.
- `scripts/`: analysis, QC, figure, and package-building scripts.
- `qc/`: QC reports and checks.
- `docs/`: transparency, provenance, and figure/table documentation.
- `FILE_MANIFEST.csv`: file-level checksums.
- `EXTERNAL_PUBLIC_DATA_MANIFEST.csv`: public third-party source records and excluded large raw cache hashes.

## Reproduction notes

Start with `FILE_MANIFEST.csv` and `docs/GATHER_STROBE_transparency_checklist.md`. The core projection and QC scripts are:

1. `scripts/07_block5_bapc_projection_wpp.R`
2. `scripts/07a_block5_qc_wpp.R`
3. `scripts/build_lrhwp_revision_package.py`

The package is intended to support inspection and reuse of derived aggregate outputs. Large third-party raw WPP cache files were not copied into the GitHub-ready folder; they are listed with hashes in `EXTERNAL_PUBLIC_DATA_MANIFEST.csv`.
