from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "\u539f\u59cb\u6570\u636e" / "GBD2023_Demographics_1950_2023"
OUT_DIR = ROOT / "output" / "lrhwp_revision" / "population_review"

MORTALITY_ZIP = RAW_DIR / "IHME_GBD_2023_DEMOGRAPHICS_1950_2023_MORTALITY.zip"
MORTALITY_2013_2023_ENTRY = (
    "IHME_GBD_2023_DEMOGRAPHICS_1950_2023_MORTALITY_INPUT_DATA_2013_2023_Y2025M06D09.CSV"
)

AGE_GROUP_IDS_20PLUS = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 30, 31, 32, 235]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_local_file_inventory() -> None:
    rows = []
    for path in sorted(RAW_DIR.glob("*")):
        if not path.is_file():
            continue
        rows.append(
            {
                "file_name": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    pd.DataFrame(rows).to_csv(
        OUT_DIR / "gbd2023_demographics_local_file_inventory.csv", index=False
    )


def write_zip_inventory() -> None:
    rows = []
    for zip_path in sorted(RAW_DIR.glob("*.zip")):
        with zipfile.ZipFile(zip_path) as z:
            for entry in z.infolist():
                rows.append(
                    {
                        "zip_file": zip_path.name,
                        "entry_name": entry.filename,
                        "uncompressed_bytes": entry.file_size,
                        "compressed_bytes": entry.compress_size,
                    }
                )
    pd.DataFrame(rows).to_csv(
        OUT_DIR / "gbd2023_demographics_zip_inventory.csv", index=False
    )


def read_study_locations() -> list[str]:
    mapping = pd.read_csv(OUT_DIR / "wpp2024_location_name_mapping.csv")
    return mapping["project_location_name"].tolist()


def extract_2023_mortality_input_sample_size(study_locations: list[str]) -> pd.DataFrame:
    usecols = [
        "location_id",
        "location_name",
        "sex_name",
        "age_group_id",
        "age_group_name",
        "year_id",
        "sample_size",
        "age_sex_split",
        "outlier",
    ]
    chunks = []
    with zipfile.ZipFile(MORTALITY_ZIP) as z, z.open(MORTALITY_2013_2023_ENTRY) as f:
        for chunk in pd.read_csv(f, usecols=usecols, chunksize=500_000):
            chunk = chunk[
                (chunk["year_id"] == 2023)
                & (chunk["location_name"].isin(study_locations))
                & (chunk["age_group_id"].isin(AGE_GROUP_IDS_20PLUS))
            ]
            if not chunk.empty:
                chunks.append(chunk)
    if not chunks:
        return pd.DataFrame(columns=usecols)
    return pd.concat(chunks, ignore_index=True)


def write_2023_comparison(study_locations: list[str]) -> None:
    df = extract_2023_mortality_input_sample_size(study_locations)
    df.to_csv(
        OUT_DIR / "gbd2023_demographics_mortality_input_2023_20plus_rows.csv",
        index=False,
    )

    if df.empty:
        comparison = pd.DataFrame({"project_location_name": study_locations})
        comparison.to_csv(
            OUT_DIR
            / "gbd2023_demographics_mortality_input_2023_20plus_sample_size_vs_wpp_internal.csv",
            index=False,
        )
        return

    all_rows = (
        df.groupby("location_name", as_index=False)
        .agg(
            gbd_mortality_input_sample_size_20plus_2023=("sample_size", "sum"),
            mortality_input_rows_20plus=("sample_size", "size"),
            mortality_input_outlier_rows_20plus=("outlier", lambda s: (s == "yes").sum()),
            mortality_input_nonoutlier_rows_20plus=(
                "outlier",
                lambda s: (s == "no").sum(),
            ),
        )
        .rename(columns={"location_name": "project_location_name"})
    )

    nonoutlier = (
        df[df["outlier"] == "no"]
        .groupby("location_name", as_index=False)["sample_size"]
        .sum()
        .rename(
            columns={
                "location_name": "project_location_name",
                "sample_size": "gbd_mortality_input_nonoutlier_sample_size_20plus_2023",
            }
        )
    )

    wpp = pd.read_csv(OUT_DIR / "wpp2024_population_exposure_20plus_2023_2050_by_location.csv")
    wpp = wpp[wpp["year"] == 2023][
        ["project_location_name", "wpp_location_name", "wpp_exposure_20plus"]
    ]

    internal = pd.read_csv(OUT_DIR / "wpp2024_vs_internal_proxy_2023_by_location.csv")[
        ["project_location_name", "internal_proxy_population_20plus_2023"]
    ]

    comparison = (
        pd.DataFrame({"project_location_name": study_locations})
        .merge(all_rows, on="project_location_name", how="left")
        .merge(nonoutlier, on="project_location_name", how="left")
        .merge(wpp, on="project_location_name", how="left")
        .merge(internal, on="project_location_name", how="left")
    )
    comparison["gbd_mortality_input_available_2023"] = comparison[
        "gbd_mortality_input_sample_size_20plus_2023"
    ].notna()
    comparison[
        "relative_difference_mortality_input_sample_size_vs_wpp_exposure_pct"
    ] = (
        (
            comparison["gbd_mortality_input_sample_size_20plus_2023"]
            - comparison["wpp_exposure_20plus"]
        )
        / comparison["wpp_exposure_20plus"]
        * 100
    )
    comparison["relative_difference_internal_proxy_vs_wpp_exposure_pct"] = (
        (
            comparison["internal_proxy_population_20plus_2023"]
            - comparison["wpp_exposure_20plus"]
        )
        / comparison["wpp_exposure_20plus"]
        * 100
    )
    comparison.to_csv(
        OUT_DIR
        / "gbd2023_demographics_mortality_input_2023_20plus_sample_size_vs_wpp_internal.csv",
        index=False,
    )

    available = comparison[comparison["gbd_mortality_input_available_2023"]].copy()
    summary = pd.DataFrame(
        [
            {
                "metric": "study_locations",
                "value": len(study_locations),
            },
            {
                "metric": "locations_with_2023_mortality_input_sample_size",
                "value": int(comparison["gbd_mortality_input_available_2023"].sum()),
            },
            {
                "metric": "locations_without_2023_mortality_input_sample_size",
                "value": int((~comparison["gbd_mortality_input_available_2023"]).sum()),
            },
            {
                "metric": "regional_20plus_sample_size_available_locations",
                "value": available[
                    "gbd_mortality_input_sample_size_20plus_2023"
                ].sum(),
            },
            {
                "metric": "wpp_20plus_exposure_same_available_locations",
                "value": available["wpp_exposure_20plus"].sum(),
            },
            {
                "metric": "relative_difference_available_locations_pct",
                "value": (
                    (
                        available[
                            "gbd_mortality_input_sample_size_20plus_2023"
                        ].sum()
                        - available["wpp_exposure_20plus"].sum()
                    )
                    / available["wpp_exposure_20plus"].sum()
                    * 100
                ),
            },
        ]
    )
    summary.to_csv(
        OUT_DIR / "gbd2023_demographics_mortality_input_2023_20plus_coverage_summary.csv",
        index=False,
    )


def write_summary_markdown() -> None:
    inventory = pd.read_csv(OUT_DIR / "gbd2023_demographics_local_file_inventory.csv")
    zip_inventory = pd.read_csv(OUT_DIR / "gbd2023_demographics_zip_inventory.csv")
    coverage = pd.read_csv(
        OUT_DIR / "gbd2023_demographics_mortality_input_2023_20plus_coverage_summary.csv"
    )
    comparison = pd.read_csv(
        OUT_DIR
        / "gbd2023_demographics_mortality_input_2023_20plus_sample_size_vs_wpp_internal.csv"
    )
    available = comparison[comparison["gbd_mortality_input_available_2023"] == True]
    missing = comparison[comparison["gbd_mortality_input_available_2023"] == False][
        "project_location_name"
    ].tolist()

    coverage_dict = dict(zip(coverage["metric"], coverage["value"]))
    lines = [
        "# GBD 2023 Demographics Local Review",
        "",
        "Generated: 2026-06-12",
        "",
        "## Local Package",
        "",
        f"- Local source folder: `{RAW_DIR}`",
        f"- Top-level files copied: {len(inventory)}",
        f"- Zip entries indexed: {len(zip_inventory)}",
        "",
        "## Key Finding",
        "",
        "The local GBD 2023 Demographics 1950-2023 package is not a direct GBD Results Tool population export. Its information sheet describes mortality input data, stillbirth input/estimate data, TMRLT, and selected appendix tables. The mortality CSV contains `sample_size`, defined as the sample population to which each mortality-rate input value applies. This can support source triangulation, but it should not be treated as the official final GBD population/person-years denominator for all study locations.",
        "",
        "## 2023 Mortality-Input Sample-Size Coverage",
        "",
        f"- Study locations: {int(coverage_dict['study_locations'])}",
        f"- Locations with 2023 20+ mortality-input sample-size rows: {int(coverage_dict['locations_with_2023_mortality_input_sample_size'])}",
        f"- Locations without 2023 20+ mortality-input sample-size rows: {int(coverage_dict['locations_without_2023_mortality_input_sample_size'])}",
        f"- Aggregate sample size among available locations: {coverage_dict['regional_20plus_sample_size_available_locations']:.0f}",
        f"- WPP 2024 20+ exposure for the same locations: {coverage_dict['wpp_20plus_exposure_same_available_locations']:.0f}",
        f"- Relative difference: {coverage_dict['relative_difference_available_locations_pct']:.2f}%",
        "",
        "Missing locations:",
        "",
        ", ".join(missing),
        "",
        "## Files Written",
        "",
        "- `gbd2023_demographics_local_file_inventory.csv`",
        "- `gbd2023_demographics_zip_inventory.csv`",
        "- `gbd2023_demographics_mortality_input_2023_20plus_rows.csv`",
        "- `gbd2023_demographics_mortality_input_2023_20plus_sample_size_vs_wpp_internal.csv`",
        "- `gbd2023_demographics_mortality_input_2023_20plus_coverage_summary.csv`",
    ]
    if not available.empty:
        worst = available.assign(
            abs_rel_diff=available[
                "relative_difference_mortality_input_sample_size_vs_wpp_exposure_pct"
            ].abs()
        ).sort_values("abs_rel_diff", ascending=False).head(5)
        lines += [
            "",
            "## Largest Available-Location Differences vs WPP Exposure",
            "",
            simple_markdown_table(
                worst[
                    [
                        "project_location_name",
                        "gbd_mortality_input_sample_size_20plus_2023",
                        "wpp_exposure_20plus",
                        "relative_difference_mortality_input_sample_size_vs_wpp_exposure_pct",
                    ]
                ]
            ),
        ]
    (OUT_DIR / "gbd2023_demographics_review_summary.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def simple_markdown_table(df: pd.DataFrame) -> str:
    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda x: "" if pd.isna(x) else f"{x:.2f}")
    headers = [str(c) for c in display.columns]
    rows = [[str(v) for v in row] for row in display.to_numpy()]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not RAW_DIR.exists():
        raise FileNotFoundError(f"Raw demographics folder not found: {RAW_DIR}")
    write_local_file_inventory()
    write_zip_inventory()
    study_locations = read_study_locations()
    write_2023_comparison(study_locations)
    write_summary_markdown()
    print("GBD demographics review written to", OUT_DIR)


if __name__ == "__main__":
    main()
