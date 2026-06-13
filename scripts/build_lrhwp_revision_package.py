# -*- coding: utf-8 -*-
"""
Build an LRH-WP-oriented revision package without modifying the first-version
outputs under output/final.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import math
import os
import shutil
from pathlib import Path

import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import polars as pl
import statsmodels.api as sm
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D
from shapely.geometry import Point
from shapely.ops import transform


ROOT = Path(os.environ.get("GBD_PROJECT_ROOT", "<PROJECT_ROOT>"))
FINAL = ROOT / "output" / "final"
REV = ROOT / "output" / "lrhwp_revision"
REV_FIG = REV / "figures"
REV_TAB = REV / "tables"
REV_DOC = REV / "documents"
REV_POP = REV / "population_review"
ARCHIVE = REV / "source_archive" / "final_v1_snapshot"


spec = importlib.util.spec_from_file_location("cfg", ROOT / "code" / "00_config.py")
cfg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cfg)
cfg.reconfig_utf8()


POINT_COORDS = {
    "China": (104.0, 35.0),
    "Democratic People's Republic of Korea": (127.3, 40.1),
    "Taiwan": (121.0, 23.7),
    "Cambodia": (104.9, 12.6),
    "Indonesia": (118.0, -2.5),
    "Lao People's Democratic Republic": (103.8, 18.2),
    "Malaysia": (102.3, 4.2),
    "Maldives": (73.2, 3.2),
    "Myanmar": (96.0, 21.0),
    "Philippines": (122.0, 12.9),
    "Sri Lanka": (80.7, 7.9),
    "Thailand": (100.9, 15.8),
    "Timor-Leste": (125.7, -8.9),
    "Viet Nam": (108.3, 14.1),
    "Fiji": (178.1, -17.8),
    "Kiribati": (173.0, 1.8),
    "Marshall Islands": (171.2, 7.1),
    "Micronesia (Federated States of)": (158.2, 6.9),
    "Papua New Guinea": (143.9, -6.3),
    "Samoa": (-172.1, -13.8),
    "Solomon Islands": (160.2, -9.6),
    "Tonga": (-175.2, -21.2),
    "Vanuatu": (167.7, -15.4),
    "Mauritius": (57.6, -20.2),
    "Seychelles": (55.5, -4.7),
    "American Samoa": (-170.7, -14.3),
    "Cook Islands": (-159.8, -21.2),
    "Guam": (144.8, 13.4),
    "Nauru": (166.9, -0.5),
    "Niue": (-169.9, -19.1),
    "Northern Mariana Islands": (145.7, 15.1),
    "Palau": (134.6, 7.5),
    "Tokelau": (-171.9, -9.2),
    "Tuvalu": (179.2, -8.5),
}

NAME_ALIASES = {
    "China": ["China"],
    "Democratic People's Republic of Korea": ["North Korea", "Dem. Rep. Korea", "Korea, North"],
    "Taiwan": ["Taiwan"],
    "Cambodia": ["Cambodia"],
    "Indonesia": ["Indonesia"],
    "Lao People's Democratic Republic": ["Laos", "Lao PDR"],
    "Malaysia": ["Malaysia"],
    "Maldives": ["Maldives"],
    "Myanmar": ["Myanmar", "Burma"],
    "Philippines": ["Philippines"],
    "Sri Lanka": ["Sri Lanka"],
    "Thailand": ["Thailand"],
    "Timor-Leste": ["Timor-Leste", "East Timor"],
    "Viet Nam": ["Vietnam", "Viet Nam"],
    "Fiji": ["Fiji"],
    "Kiribati": ["Kiribati"],
    "Marshall Islands": ["Marshall Islands"],
    "Micronesia (Federated States of)": ["Federated States of Micronesia", "Micronesia"],
    "Papua New Guinea": ["Papua New Guinea"],
    "Samoa": ["Samoa"],
    "Solomon Islands": ["Solomon Islands"],
    "Tonga": ["Tonga"],
    "Vanuatu": ["Vanuatu"],
    "Mauritius": ["Mauritius"],
    "Seychelles": ["Seychelles"],
    "American Samoa": ["American Samoa"],
    "Cook Islands": ["Cook Islands"],
    "Guam": ["Guam"],
    "Nauru": ["Nauru"],
    "Niue": ["Niue"],
    "Northern Mariana Islands": ["Northern Mariana Islands"],
    "Palau": ["Palau"],
    "Tokelau": ["Tokelau"],
    "Tuvalu": ["Tuvalu"],
}

PALETTE_2 = [
    "#A6CEE3",
    "#1F78B4",
    "#B2DF8A",
    "#33A02C",
    "#FB9A99",
    "#E31A1C",
    "#FDBF6F",
    "#FF7F00",
    "#CAB2D6",
    "#6A3D9A",
    "#FFFF99",
    "#B15928",
]
MAP_CMAP = LinearSegmentedColormap.from_list(
    "lrhwp_map",
    ["#F2F2F2", "#A6CEE3", "#1F78B4", "#6A3D9A"],
)
FACTOR_COLORS = {
    "high_bmi": "#1F78B4",
    "high_fpg": "#FF7F00",
    "smoking": "#6A3D9A",
}


def ensure_dirs() -> None:
    for path in [REV_FIG, REV_TAB, REV_DOC, REV_POP, ARCHIVE]:
        path.mkdir(parents=True, exist_ok=True)
    if not any(ARCHIVE.rglob("*")):
        shutil.copytree(FINAL, ARCHIVE, dirs_exist_ok=True)


def set_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "font.size": 7,
            "axes.titlesize": 8.2,
            "axes.labelsize": 7.4,
            "xtick.labelsize": 6.8,
            "ytick.labelsize": 6.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.45,
            "xtick.major.width": 0.4,
            "ytick.major.width": 0.4,
            "legend.frameon": False,
            "figure.dpi": 150,
            "savefig.dpi": 600,
        }
    )


def save_figure(fig: plt.Figure, stem: str, tiff: bool = True) -> None:
    for ext in ["png", "svg", "pdf"]:
        fig.savefig(REV_FIG / f"{stem}.{ext}", bbox_inches="tight", dpi=600 if ext == "png" else None)
    if tiff:
        fig.savefig(
            REV_FIG / f"{stem}.tiff",
            bbox_inches="tight",
            dpi=600,
            pil_kwargs={"compression": "tiff_lzw"},
        )


def norm_name(value: object) -> str:
    return str(value).strip().lower().replace("&", "and")


def shift_lon_value(x: float) -> float:
    return x + 360.0 if x < 40.0 else x


def shift_geometry(geom):
    def _shift(x, y, z=None):
        x_arr = np.asarray(x)
        shifted = np.where(x_arr < 40.0, x_arr + 360.0, x_arr)
        if z is None:
            return shifted, y
        return shifted, y, z

    return transform(_shift, geom)


def load_shifted_world(table1: pd.DataFrame) -> gpd.GeoDataFrame:
    shp = ROOT / "meta" / "geospatial" / "ne_50m_admin_0_countries" / "ne_50m_admin_0_countries.shp"
    if not shp.exists():
        raise FileNotFoundError(f"Natural Earth shapefile not found: {shp}")
    world = gpd.read_file(shp).to_crs("EPSG:4326")
    lookup: dict[str, str] = {}
    for loc_name in table1["location_name"]:
        lookup[norm_name(loc_name)] = loc_name
        for alias in NAME_ALIASES.get(loc_name, []):
            lookup[norm_name(alias)] = loc_name
    name_cols = [c for c in ["ADMIN", "NAME", "NAME_LONG", "SOVEREIGNT", "BRK_NAME", "NAME_EN"] if c in world.columns]
    matches = []
    for _, row in world.iterrows():
        matched = None
        for col in name_cols:
            key = norm_name(row.get(col, ""))
            if key in lookup:
                matched = lookup[key]
                break
        matches.append(matched)
    world["study_location_name"] = matches
    return world


def figure1() -> None:
    table1 = pd.read_csv(FINAL / "tables" / "Table1_counterfactual_2023_country.csv")
    world = load_shifted_world(table1)
    points = table1.copy()
    points["longitude"] = points["location_name"].map(lambda x: POINT_COORDS[x][0])
    points["latitude"] = points["location_name"].map(lambda x: POINT_COORDS[x][1])
    points["longitude_shifted"] = points["longitude"].map(shift_lon_value)
    points["geometry"] = [Point(xy) for xy in zip(points["longitude_shifted"], points["latitude"])]
    gpoints = gpd.GeoDataFrame(points, geometry="geometry", crs="EPSG:4326")

    # Compact Pacific-centered extent selected after visual review: keeps all
    # manual study points while reducing unused non-study land/ocean background.
    xmin, xmax = 54, 202
    ymin, ymax = -23.5, 55
    region = world.cx[xmin:180, ymin:ymax].copy()
    region = region.merge(
        table1[["location_name", "avoidable_daly_rate_per_100k_20plus", "avoidable_number_main_dalys"]],
        left_on="study_location_name",
        right_on="location_name",
        how="left",
    )

    vmax = float(np.nanpercentile(table1["avoidable_daly_rate_per_100k_20plus"], 92))
    norm = Normalize(vmin=0, vmax=vmax)
    top10 = table1.nlargest(10, "avoidable_number_main_dalys").sort_values("avoidable_number_main_dalys")

    fig = plt.figure(figsize=(10.8, 6.05), constrained_layout=False)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.48, 0.92], wspace=0.18)
    ax_map = fig.add_subplot(gs[0, 0])
    ax_bar = fig.add_subplot(gs[0, 1])

    region.plot(ax=ax_map, color="#FAFAFA", edgecolor="#E2E7EC", linewidth=0.28)
    highlighted = region[region["avoidable_daly_rate_per_100k_20plus"].notna()]
    highlighted.plot(
        ax=ax_map,
        column="avoidable_daly_rate_per_100k_20plus",
        cmap=MAP_CMAP,
        norm=norm,
        edgecolor="#5F6B76",
        linewidth=0.42,
    )

    size = np.sqrt(gpoints["avoidable_number_main_dalys"].clip(lower=0))
    size = 18 + (size / size.max()) * 170
    gpoints.plot(
        ax=ax_map,
        markersize=size,
        column="avoidable_daly_rate_per_100k_20plus",
        cmap=MAP_CMAP,
        norm=norm,
        edgecolor="#1F2933",
        linewidth=0.42,
        alpha=0.88,
        zorder=5,
    )

    label_df = gpoints.nlargest(6, "avoidable_number_main_dalys")
    offsets = {
        "China": (2.2, 2.2),
        "Indonesia": (2.0, -1.8),
        "Thailand": (2.0, 1.4),
        "Malaysia": (2.0, -1.4),
        "Philippines": (2.0, 1.8),
        "Myanmar": (2.0, 1.2),
    }
    for _, row in label_df.iterrows():
        dx, dy = offsets.get(row["location_name"], (1.6, 1.2))
        ax_map.text(
            row["longitude_shifted"] + dx,
            row["latitude"] + dy,
            row["location_name"],
            fontsize=6.1,
            color="#1F2933",
            ha="left",
            va="center",
        )

    ax_map.set_xlim(xmin, xmax)
    ax_map.set_ylim(ymin, ymax)
    ax_map.set_aspect(1.10)
    ax_map.set_xticks([60, 90, 120, 150, 180])
    ax_map.set_xticklabels(["60E", "90E", "120E", "150E", "180"])
    ax_map.set_yticks([-20, 0, 20, 40])
    ax_map.set_yticklabels(["20S", "0", "20N", "40N"])
    ax_map.grid(color="#E5E7EB", linewidth=0.35, zorder=0)
    ax_map.set_title("A. Rate and absolute burden", loc="left", fontweight="bold")
    ax_map.set_xlabel("")
    ax_map.set_ylabel("")

    sm = mpl.cm.ScalarMappable(norm=norm, cmap=MAP_CMAP)
    cbar = fig.colorbar(sm, ax=ax_map, orientation="horizontal", fraction=0.036, pad=0.055, extend="max")
    cbar.set_label("Rate per 100,000 adults aged 20+")
    cbar.ax.tick_params(labelsize=6.2)

    legend_handles = []
    for value in [50, 500, 1500]:
        s = 18 + (math.sqrt(value) / math.sqrt(points["avoidable_number_main_dalys"].max())) * 170
        legend_handles.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="none",
                markerfacecolor="#A6CEE3",
                markeredgecolor="#1F2933",
                markersize=math.sqrt(s),
                label=f"{value:,}",
            )
        )
    ax_map.legend(
        handles=legend_handles,
        title="Potentially avoidable DALYs",
        loc="lower left",
        bbox_to_anchor=(0.01, 0.02),
        fontsize=5.8,
        title_fontsize=6.2,
        frameon=True,
        facecolor="white",
        edgecolor="#D1D5DB",
    )

    display_name = {
        "Democratic People's Republic of Korea": "DPR Korea",
        "Lao People's Democratic Republic": "Lao PDR",
        "Micronesia (Federated States of)": "Micronesia",
    }
    top10 = top10.assign(display_location=top10["location_name"].map(lambda x: display_name.get(x, x)))
    colors = [MAP_CMAP(norm(v)) for v in top10["avoidable_daly_rate_per_100k_20plus"]]
    ax_bar.barh(top10["display_location"], top10["avoidable_number_main_dalys"], color=colors, edgecolor="#2F3A44", linewidth=0.35)
    ax_bar.set_title("B. Largest potentially avoidable DALYs", loc="left", fontweight="bold")
    ax_bar.set_xlabel("Potentially avoidable DALYs, 2023")
    ax_bar.tick_params(axis="y", labelsize=6.4)
    ax_bar.grid(axis="x", color="#E5E7EB", linewidth=0.45)
    for _, row in top10.iterrows():
        ax_bar.text(
            row["avoidable_number_main_dalys"] + top10["avoidable_number_main_dalys"].max() * 0.02,
            row["display_location"],
            f"{row['avoidable_number_main_dalys']:.0f}",
            va="center",
            fontsize=6.2,
            color="#2F3A44",
        )
    ax_bar.set_xlim(0, top10["avoidable_number_main_dalys"].max() * 1.18)

    fig.suptitle(
        "Potentially avoidable MASLD/NAFLD-related DALYs under sex-equalized high-BMI exposure, 2023",
        fontsize=10.5,
        y=0.985,
    )
    fig.text(
        0.08,
        0.012,
        "Basemap: Natural Earth admin-0 countries. Points use manual coordinates for all 34 study countries/territories; map is Pacific-centered. Color scale is capped at the 92nd percentile with overflow indicated.",
        fontsize=5.9,
        color="#4B5563",
    )
    fig.subplots_adjust(top=0.9, bottom=0.11, left=0.06, right=0.98)
    save_figure(fig, "Figure1_LRHWP_potentially_avoidable_DALYs")
    plt.close(fig)
    table1.to_csv(REV_TAB / "Table1_counterfactual_2023_country_v1_source.csv", index=False, encoding="utf-8-sig")


def figure2() -> None:
    table2 = pd.read_csv(FINAL / "tables" / "Table2_factor_comparison_2023_country.csv")
    grad = pd.read_csv(ROOT / "output" / "tables" / "block4_country_sdi_gradient_2023_model.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 5.5), gridspec_kw={"width_ratios": [0.9, 1.55]})

    ycol = "internal_std_rate_30plus_high_bmi"
    d = table2.sort_values("sdi_mean").copy()
    axes[0].scatter(d["sdi_mean"], d[ycol], color=FACTOR_COLORS["high_bmi"], s=22, alpha=0.9)
    x = sm.add_constant(d["sdi_mean"].astype(float), has_constant="add")
    res = sm.OLS(d[ycol].astype(float), x).fit()
    grid = pd.DataFrame({"sdi_mean": np.linspace(d["sdi_mean"].min(), d["sdi_mean"].max(), 120)})
    pred = res.get_prediction(sm.add_constant(grid["sdi_mean"], has_constant="add")).summary_frame()
    axes[0].plot(grid["sdi_mean"], pred["mean"], color="#263238", lw=1.0)
    axes[0].fill_between(
        grid["sdi_mean"].to_numpy(),
        pred["mean_ci_lower"].to_numpy(),
        pred["mean_ci_upper"].to_numpy(),
        color=FACTOR_COLORS["high_bmi"],
        alpha=0.12,
        lw=0,
    )
    for _, r in d.nlargest(5, ycol).iterrows():
        axes[0].text(r["sdi_mean"], r[ycol], r["location_name"], ha="left", va="bottom", fontsize=5.7)
    g = grad.query("risk_key == 'high_bmi' and measure_id == 2").iloc[0]
    axes[0].text(
        0.03,
        0.96,
        f"Slope per 0.1 SDI: {g['slope_per_0_1_sdi']:.2f}; HC3 p={g['slope_p_hc3']:.3f}",
        transform=axes[0].transAxes,
        ha="left",
        va="top",
        fontsize=5.9,
        color="#374151",
    )
    axes[0].set_xlabel("Official SDI, 2023")
    axes[0].set_ylabel("High-BMI-attributable DALY rate per 100,000")
    axes[0].set_title("A. Descriptive SDI association", loc="left", fontweight="bold")
    axes[0].grid(axis="both", color="#E5E7EB", lw=0.5)

    top = table2.head(16).sort_values("internal_std_rate_30plus_high_bmi").copy()
    y = np.arange(len(top))
    labels = {"high_bmi": "High BMI", "high_fpg": "High FPG", "smoking": "Smoking"}
    for risk in ["high_bmi", "high_fpg", "smoking"]:
        axes[1].scatter(top[f"internal_std_rate_30plus_{risk}"], y, s=24, color=FACTOR_COLORS[risk], label=labels[risk])
    axes[1].set_yticks(y)
    axes[1].set_yticklabels(top["location_name"], fontsize=6.2)
    axes[1].set_xlabel("Internal age-standardized 30+ DALY rate per 100,000")
    axes[1].set_title("B. Non-additive risk-factor comparison", loc="left", fontweight="bold")
    axes[1].grid(axis="x", color="#E5E7EB", lw=0.5)
    axes[1].legend(loc="lower right")
    fig.suptitle("SDI context and non-additive metabolic risk-factor comparison, 2023", fontsize=10.0, y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.965])
    save_figure(fig, "Figure2_LRHWP_SDI_and_risk_factor_comparison", tiff=False)
    plt.close(fig)
    table2.to_csv(REV_TAB / "Table2_factor_comparison_2023_country_v1_source.csv", index=False, encoding="utf-8-sig")


def figure_s1() -> None:
    bmi_path = ROOT / "clean" / "adult_bmi_population_weighted.parquet"
    long_path = ROOT / "clean" / "analysis_long.parquet"
    if not bmi_path.exists() or not long_path.exists():
        for ext in ["png", "svg", "pdf"]:
            src = FINAL / "figures" / f"Figure3_exposure_burden_dumbbell.{ext}"
            if src.exists():
                shutil.copy2(src, REV_FIG / f"Supplementary_FigureS1_BMI_exposure_burden_dumbbell.{ext}")
        return

    exp = pl.read_parquet(bmi_path).to_pandas()
    exp = exp[exp["year"].isin([1990, 2023])].copy()
    exp = exp[["location_name", "year", "sex_name", "mean_bmi_20plus_pop_weighted"]].rename(
        columns={"mean_bmi_20plus_pop_weighted": "value"}
    )

    burden = (
        pl.scan_parquet(long_path)
        .filter(
            pl.col("dataset") == "A_highBMI_attr",
            pl.col("location_tier") == "country",
            pl.col("year").is_in([1990, 2023]),
            pl.col("sex_name").is_in(["Male", "Female"]),
            pl.col("measure_id") == 2,
            pl.col("metric_name") == "Rate",
            pl.col("age_key") == "ASR",
        )
        .select("location_name", "year", "sex_name", "val")
        .collect()
        .rename({"val": "value"})
        .to_pandas()
    )

    sort_ref = (
        exp[exp["year"] == 2023]
        .pivot(index="location_name", columns="sex_name", values="value")
        .assign(abs_gap=lambda d: (d["Female"] - d["Male"]).abs())
        .sort_values("abs_gap", ascending=False)
        .index
        .tolist()
    )
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 8.9), sharey=True)
    year_colors = {1990: "#9CA3AF", 2023: FACTOR_COLORS["high_bmi"]}
    sex_markers = {"Male": "^", "Female": "o"}
    y_positions = {loc: i for i, loc in enumerate(sort_ref)}

    for ax, data, title, xlabel in [
        (axes[0], exp, "A. Adult mean BMI, 20+ population-weighted", "Mean BMI (kg/m^2)"),
        (axes[1], burden, "B. Observed high-BMI-attributable burden", "High-BMI-attributable DALY ASR per 100,000"),
    ]:
        for year, offset in [(1990, -0.16), (2023, 0.16)]:
            subset = data[data["year"] == year]
            wide = subset.pivot(index="location_name", columns="sex_name", values="value")
            for loc in sort_ref:
                if loc not in wide.index or not {"Male", "Female"} <= set(wide.columns):
                    continue
                y = y_positions[loc] + offset
                x_m = wide.loc[loc, "Male"]
                x_f = wide.loc[loc, "Female"]
                ax.plot([x_m, x_f], [y, y], color=year_colors[year], lw=0.8, alpha=0.85)
                ax.scatter(x_m, y, marker=sex_markers["Male"], color=year_colors[year], s=16, zorder=3)
                ax.scatter(x_f, y, marker=sex_markers["Female"], color=year_colors[year], s=16, zorder=3)
        ax.set_title(title, loc="left", fontweight="bold")
        ax.set_xlabel(xlabel)
        ax.grid(axis="x", color="#E5E7EB", lw=0.45)

    axes[0].set_yticks(range(len(sort_ref)))
    axes[0].set_yticklabels(sort_ref, fontsize=5.9)
    axes[0].invert_yaxis()
    axes[0].set_xlabel("Mean BMI (kg/m^2)")
    axes[0].set_title("A. Adult mean BMI, 20+ population-weighted", loc="left", fontweight="bold")
    axes[1].set_xlabel("High-BMI-attributable DALY ASR per 100,000")
    axes[1].set_title("B. Observed high-BMI-attributable burden", loc="left", fontweight="bold")
    for ax in axes:
        ax.grid(axis="x", color="#E5E7EB", lw=0.45)
    handles = [
        Line2D([0], [0], color=year_colors[1990], marker="s", lw=0.7, label="1990"),
        Line2D([0], [0], color=year_colors[2023], marker="s", lw=0.7, label="2023"),
        Line2D([0], [0], color="black", marker="^", linestyle="None", label="Male"),
        Line2D([0], [0], color="black", marker="o", linestyle="None", label="Female"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.005), fontsize=6.2)
    fig.suptitle("Supplementary Figure S1. Sex gap in BMI exposure and observed high-BMI-attributable DALY rate", fontsize=9.4, y=0.995)
    fig.tight_layout(rect=[0, 0.035, 1, 0.965])
    save_figure(fig, "Supplementary_FigureS1_BMI_exposure_burden_dumbbell", tiff=False)
    plt.close(fig)


def figure5() -> None:
    uncertainty = pd.read_csv(FINAL / "tables" / "Table3B_uncertainty_psa_summary.csv")
    sensitivity = pd.read_csv(FINAL / "tables" / "Table3C_sensitivity_tmrel_summary.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.7), gridspec_kw={"width_ratios": [1.15, 0.85]})

    daly = uncertainty.query("measure_id == 2").copy()
    labels = {
        "main_block3_proxy": "Main estimate: proxy interval",
        "summary_ui_lognormal_rho_0.8": "Summary-UI proxy propagation",
        "rr_psa_capped": "RR-PSA, capped primary rule",
        "rr_psa_uncapped_sensitivity": "RR-PSA, uncapped sensitivity",
    }
    order = list(labels.values())
    daly["label"] = pd.Categorical(daly["method"].map(labels), categories=order, ordered=True)
    daly = daly.sort_values("label")
    y = np.arange(len(daly))
    x = daly["median"].fillna(daly["point"]).to_numpy()
    lo = np.maximum(0, x - daly["lower"].to_numpy())
    hi = np.maximum(0, daly["upper"].to_numpy() - x)
    axes[0].errorbar(x, y, xerr=[lo, hi], fmt="o", color="#263238", ecolor="#9CA3AF", elinewidth=0.95, capsize=2.2)
    axes[0].scatter(x, y, s=24, color=[PALETTE_2[1], PALETTE_2[7], PALETTE_2[9], PALETTE_2[5]], zorder=3)
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(daly["label"], fontsize=6.2)
    axes[0].invert_yaxis()
    axes[0].set_xlabel("Potentially avoidable DALYs, 2023")
    axes[0].set_title("A. Proxy uncertainty and RR sensitivity", loc="left", fontweight="bold")
    axes[0].grid(axis="x", color="#E5E7EB", linewidth=0.5)

    lean = sensitivity.query("measure_id == 2 and section == 'lean_denominator_sensitivity'").copy()
    tmrel = sensitivity.query("measure_id == 2 and section == 'tmrel_upper_bound_comparison'").copy()
    rows = []
    for _, r in lean.iterrows():
        rows.append({
            "label": r["scenario"].replace("lean denominator inflation", "Scenario A + denominator"),
            "pct": r["avoidable_pct_total"],
            "group": "Scenario A",
        })
    b = tmrel[tmrel["scenario"].eq("B_TMREL_high_bmi_upper_bound")].iloc[0]
    rows.append({"label": "Scenario B: high BMI at TMREL", "pct": b["avoidable_pct_total"], "group": "Scenario B"})
    pct = pd.DataFrame(rows)
    pct["label"] = pd.Categorical(
        pct["label"],
        categories=[
            "Scenario A + denominator 0%",
            "Scenario A + denominator 10%",
            "Scenario A + denominator 25%",
            "Scenario A + denominator 50%",
            "Scenario B: high BMI at TMREL",
        ],
        ordered=True,
    )
    pct = pct.sort_values("label")
    colors = np.where(pct["group"].eq("Scenario B"), PALETTE_2[7], PALETTE_2[1])
    axes[1].barh(np.arange(len(pct)), pct["pct"], color=colors, alpha=0.9)
    axes[1].set_yticks(np.arange(len(pct)))
    axes[1].set_yticklabels(pct["label"], fontsize=6.2)
    axes[1].invert_yaxis()
    axes[1].set_xlabel("Potentially avoidable DALYs (% of total)")
    axes[1].set_title("B. Lean boundary and TMREL upper bound", loc="left", fontweight="bold")
    axes[1].grid(axis="x", color="#E5E7EB", linewidth=0.5)
    for i, val in enumerate(pct["pct"]):
        axes[1].text(val, i, f" {val:.2f}%", va="center", ha="left", fontsize=6.2)
    fig.suptitle("Supplementary Figure S2. Robustness of the sex-equalized high-BMI counterfactual", fontsize=9.5, y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    save_figure(fig, "Supplementary_FigureS2_uncertainty_sensitivity")
    plt.close(fig)


def figure3_projection() -> None:
    scenario_path = REV_TAB / "block5_projection_scenarios.csv"
    if not scenario_path.exists():
        scenario_path = ROOT / "output" / "tables" / "block5_projection_scenarios.csv"
    scenario = pd.read_csv(scenario_path)
    scenario["year"] = scenario["year"].astype(int)
    scenario["rate_mean"] = pd.to_numeric(scenario["rate_mean"], errors="coerce")
    scenario["rate_lower"] = pd.to_numeric(scenario["rate_lower"], errors="coerce")
    scenario["rate_upper"] = pd.to_numeric(scenario["rate_upper"], errors="coerce")

    scenario_colors = {
        "historical": "#263238",
        "baseline": "#607D8B",
        "Scenario A: sex-equalized high BMI": PALETTE_2[1],
        "Scenario B: high BMI at TMREL": PALETTE_2[7],
    }
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.9), sharex=True)
    measure_titles = {
        1: "A. Deaths",
        2: "B. DALYs",
    }

    for ax, measure_id in zip(axes, [1, 2]):
        sub = scenario[scenario["measure_id"].eq(measure_id)].copy()
        base = sub[sub["scenario"].eq("Observed projection")].sort_values("year")
        hist = base[base["period"].eq("Observed fit")]
        projected = base[base["period"].eq("Projected")]

        ax.plot(
            hist["year"],
            hist["rate_mean"],
            color=scenario_colors["historical"],
            lw=1.15,
            label="Observed fit, 1990-2023",
        )
        ax.plot(
            projected["year"],
            projected["rate_mean"],
            color=scenario_colors["baseline"],
            lw=1.15,
            linestyle="--",
            label="Baseline projection, 2024-2050",
        )
        ax.fill_between(
            projected["year"].to_numpy(),
            projected["rate_lower"].to_numpy(),
            projected["rate_upper"].to_numpy(),
            color=scenario_colors["baseline"],
            alpha=0.13,
            linewidth=0,
        )

        for scen in ["Scenario A: sex-equalized high BMI", "Scenario B: high BMI at TMREL"]:
            s = sub[sub["scenario"].eq(scen) & sub["year"].ge(2023)].sort_values("year")
            ax.plot(
                s["year"],
                s["rate_mean"],
                color=scenario_colors[scen],
                lw=1.25,
                label=scen.replace(": sex-equalized high BMI", "").replace(": high BMI at TMREL", ""),
            )

        ax.axvline(2023, color="#9CA3AF", lw=0.65, linestyle=":")
        ax.text(2023.6, ax.get_ylim()[1] * 0.96, "projection starts", fontsize=5.8, color="#6B7280", va="top")
        ax.set_title(measure_titles[measure_id], loc="left", fontweight="bold")
        ax.set_xlabel("Year")
        ax.set_ylabel("Age-standardized rate per 100,000")
        ax.set_xlim(1990, 2050)
        ax.grid(axis="y", color="#E5E7EB", lw=0.5)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False, fontsize=6.2, bbox_to_anchor=(0.5, 0.005))
    fig.suptitle(
        "Figure 3. BAPC scenario projection of MASLD/NAFLD-related burden rates to 2050",
        fontsize=9.5,
        y=0.995,
    )
    fig.tight_layout(rect=[0, 0.08, 1, 0.94])
    save_figure(fig, "Figure3_LRHWP_BAPC_scenario_projection")
    plt.close(fig)


def copy_tables() -> None:
    for name in [
        "Table1_counterfactual_2023_country.csv",
        "Table2_factor_comparison_2023_country.csv",
        "Table3A_projection_2050_summary.csv",
        "Table3B_uncertainty_psa_summary.csv",
        "Table3C_sensitivity_tmrel_summary.csv",
        "block7_final_tables.xlsx",
    ]:
        src = FINAL / "tables" / name
        if src.exists():
            shutil.copy2(src, REV_TAB / name)

    table3a_path = REV_TAB / "Table3A_projection_2050_summary.csv"
    wpp_block5_summary = REV_TAB / "block5_2050_summary.csv"
    if wpp_block5_summary.exists():
        t3a = pd.read_csv(wpp_block5_summary)
        t3a.to_csv(table3a_path, index=False, encoding="utf-8-sig")

    if table3a_path.exists():
        t3a = pd.read_csv(table3a_path)
        baseline_label = (
            "Baseline projection (WPP 2024 exposure)"
            if wpp_block5_summary.exists()
            else "Baseline projection (internal proxy)"
        )
        t3a["scenario"] = t3a["scenario"].replace({"Observed projection": baseline_label})
        t3a.to_csv(table3a_path, index=False, encoding="utf-8-sig")

    workbook_path = REV_TAB / "block7_final_tables.xlsx"
    if workbook_path.exists():
        sheets = pd.read_excel(workbook_path, sheet_name=None)
        if "Table3A_projection" in sheets:
            if table3a_path.exists():
                sheets["Table3A_projection"] = pd.read_csv(table3a_path)
            else:
                sheets["Table3A_projection"]["scenario"] = sheets["Table3A_projection"]["scenario"].replace(
                    {"Observed projection": "Baseline projection (internal proxy)"}
                )
        with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
            for sheet_name, frame in sheets.items():
                frame.to_excel(writer, sheet_name=sheet_name, index=False)


def write_manifest() -> None:
    rows = [
        {
            "display_order": 1,
            "file_stem": "Figure1_LRHWP_potentially_avoidable_DALYs",
            "role": "main figure",
            "caption_note": "Country-level potentially avoidable MASLD/NAFLD-related DALYs under the sex-equalized high-BMI counterfactual; rates are per 100,000 adults aged 20+.",
        },
        {
            "display_order": 2,
            "file_stem": "Figure2_LRHWP_SDI_and_risk_factor_comparison",
            "role": "main figure",
            "caption_note": "Descriptive SDI association and non-additive 30+ internally standardized risk-factor comparison; rates are not official GBD ASRs.",
        },
        {
            "display_order": 3,
            "file_stem": "Figure3_LRHWP_BAPC_scenario_projection",
            "role": "main or late-results figure",
            "caption_note": "Scenario projection rerun with UN WPP 2024 PopulationExposureByAge5GroupSex_Medium for 2024-2050 person-years; still a model scenario, not an IHME official forecast.",
        },
        {
            "display_order": "S1",
            "file_stem": "Supplementary_FigureS1_BMI_exposure_burden_dumbbell",
            "role": "supplementary figure",
            "caption_note": "Exploratory country-level sex gap plot; use as supplementary material.",
        },
        {
            "display_order": "S2",
            "file_stem": "Supplementary_FigureS2_uncertainty_sensitivity",
            "role": "supplementary figure",
            "caption_note": "Technical robustness figure separating summary-UI proxy propagation, RR-PSA, lean boundary, and TMREL upper bound.",
        },
    ]
    pd.DataFrame(rows).to_csv(REV_TAB / "lrhwp_figure_manifest.csv", index=False, encoding="utf-8-sig")


def write_report() -> None:
    lines = [
        "# LRH-WP revision package report",
        f"Generated: {dt.datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Non-overwrite policy",
        f"- First-version outputs remain under `{FINAL}`.",
        f"- A snapshot was archived under `{ARCHIVE}`.",
        f"- Revised figures, tables, and documents were written only under `{REV}`.",
        "",
        "## Visual decisions",
        "- Figure 1 uses the selected blue-purple continuous map scale with overflow indicated.",
        "- Figure 1 uses the compact Pacific-centered extent selected after visual review to reduce unused background while avoiding map stretching.",
        "- All revised Python-generated figures use Arial-first font settings aligned to Figure 4.",
        "- Figure 3 and Table 3A prefer the WPP-rerun Block 5 outputs under `output/lrhwp_revision/tables` when available.",
        "- Figure 3 from the first package is downgraded to Supplementary Figure S1.",
        "- Figure 5 is downgraded to Supplementary Figure S2 with reader-facing method labels.",
        "",
        "## Files",
        "- `figures/Figure1_LRHWP_potentially_avoidable_DALYs.*`",
        "- `figures/Figure2_LRHWP_SDI_and_risk_factor_comparison.*`",
        "- `figures/Figure3_LRHWP_BAPC_scenario_projection.*`",
        "- `figures/Supplementary_FigureS1_BMI_exposure_burden_dumbbell.*`",
        "- `figures/Supplementary_FigureS2_uncertainty_sensitivity.*`",
        "- `tables/lrhwp_figure_manifest.csv`",
    ]
    (REV_DOC / "LRHWP_revision_package_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    set_style()
    figure1()
    figure2()
    figure_s1()
    figure5()
    figure3_projection()
    copy_tables()
    write_manifest()
    write_report()
    print(f"LRH-WP revision package generated at {REV}")


if __name__ == "__main__":
    main()
