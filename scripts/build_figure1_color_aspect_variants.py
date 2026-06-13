# -*- coding: utf-8 -*-
"""
Build compact Figure 1 variants without modifying the original final package.

Outputs two color schemes:
- blue-purple
- light orange to orange-red
"""

from __future__ import annotations

import importlib.util
import math
import os
from pathlib import Path

import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D
from shapely.geometry import Point


ROOT = Path(os.environ.get("GBD_PROJECT_ROOT", "<PROJECT_ROOT>"))
REV = ROOT / "output" / "lrhwp_revision"
VARIANT_DIR = REV / "figures" / "figure1_variants"
VARIANT_DIR.mkdir(parents=True, exist_ok=True)

pkg_path = REV / "scripts" / "build_lrhwp_revision_package.py"
spec = importlib.util.spec_from_file_location("lrhwp_pkg", pkg_path)
pkg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)
pkg.set_style()


SCHEMES = {
    "bluepurple": {
        "cmap": LinearSegmentedColormap.from_list(
            "figure1_bluepurple_compact",
            ["#F2F2F2", "#A6CEE3", "#1F78B4", "#6A3D9A"],
        ),
        "legend_face": "#A6CEE3",
        "bar_edge": "#2F3A44",
    },
    "orangered": {
        "cmap": LinearSegmentedColormap.from_list(
            "figure1_orangered_compact",
            ["#FFF7EC", "#FEE8C8", "#FDBF6F", "#FF7F00", "#E31A1C"],
        ),
        "legend_face": "#FDBF6F",
        "bar_edge": "#4A2D18",
    },
}


def shifted_points(table1: pd.DataFrame) -> gpd.GeoDataFrame:
    points = table1.copy()
    points["longitude"] = points["location_name"].map(lambda x: pkg.POINT_COORDS[x][0])
    points["latitude"] = points["location_name"].map(lambda x: pkg.POINT_COORDS[x][1])
    points["longitude_shifted"] = points["longitude"].map(pkg.shift_lon_value)
    points["geometry"] = [Point(xy) for xy in zip(points["longitude_shifted"], points["latitude"])]
    return gpd.GeoDataFrame(points, geometry="geometry", crs="EPSG:4326")


def save_figure(fig: plt.Figure, stem: str) -> None:
    for ext in ["png", "svg", "pdf"]:
        fig.savefig(VARIANT_DIR / f"{stem}.{ext}", bbox_inches="tight", dpi=600 if ext == "png" else None)
    fig.savefig(
        VARIANT_DIR / f"{stem}.tiff",
        bbox_inches="tight",
        dpi=600,
        pil_kwargs={"compression": "tiff_lzw"},
    )


def draw_variant(scheme_name: str) -> None:
    scheme = SCHEMES[scheme_name]
    cmap = scheme["cmap"]
    table1 = pd.read_csv(ROOT / "output" / "final" / "tables" / "Table1_counterfactual_2023_country.csv")
    world = pkg.load_shifted_world(table1)
    points = shifted_points(table1)

    # Compact Pacific-centered extent: keeps all manual study points while reducing
    # non-study land/ocean background compared with the prior 45-225 extent.
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
        cmap=cmap,
        norm=norm,
        edgecolor="#5F6B76",
        linewidth=0.42,
    )

    size = np.sqrt(points["avoidable_number_main_dalys"].clip(lower=0))
    size = 18 + (size / size.max()) * 170
    points.plot(
        ax=ax_map,
        markersize=size,
        column="avoidable_daly_rate_per_100k_20plus",
        cmap=cmap,
        norm=norm,
        edgecolor="#1F2933",
        linewidth=0.42,
        alpha=0.88,
        zorder=5,
    )

    label_df = points.nlargest(6, "avoidable_number_main_dalys")
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
    ax_map.set_aspect(1.10, adjustable="box")
    ax_map.set_xticks([60, 90, 120, 150, 180])
    ax_map.set_xticklabels(["60E", "90E", "120E", "150E", "180"])
    ax_map.set_yticks([-20, 0, 20, 40])
    ax_map.set_yticklabels(["20S", "0", "20N", "40N"])
    ax_map.grid(color="#E5E7EB", linewidth=0.35, zorder=0)
    ax_map.set_title("A. Rate and absolute burden", loc="left", fontweight="bold")
    ax_map.set_xlabel("")
    ax_map.set_ylabel("")

    sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    cbar = fig.colorbar(sm, ax=ax_map, orientation="horizontal", fraction=0.04, pad=0.06, extend="max")
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
                markerfacecolor=scheme["legend_face"],
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
    colors = [cmap(norm(v)) for v in top10["avoidable_daly_rate_per_100k_20plus"]]
    ax_bar.barh(
        top10["display_location"],
        top10["avoidable_number_main_dalys"],
        color=colors,
        edgecolor=scheme["bar_edge"],
        linewidth=0.35,
    )
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
            fontsize=6.0,
            color="#374151",
        )
    ax_bar.set_xlim(0, top10["avoidable_number_main_dalys"].max() * 1.18)

    fig.suptitle(
        "Potentially avoidable MASLD/NAFLD-related DALYs under sex-equalized high-BMI exposure, 2023",
        fontsize=10.5,
        y=0.97,
    )
    fig.text(
        0.06,
        0.03,
        "Basemap: Natural Earth admin-0 countries. Points use manual coordinates for all 34 study countries/territories; map is Pacific-centered. "
        "Color scale is capped at the 92nd percentile with overflow indicated.",
        fontsize=5.8,
        color="#4B5563",
    )
    fig.subplots_adjust(top=0.89, bottom=0.13, left=0.06, right=0.98)
    save_figure(fig, f"Figure1_variant_{scheme_name}_compact")
    plt.close(fig)


def main() -> None:
    for scheme_name in SCHEMES:
        draw_variant(scheme_name)
    print(f"Figure 1 variants written to {VARIANT_DIR}")


if __name__ == "__main__":
    main()
