from __future__ import annotations

import math
from pathlib import Path
from textwrap import TextWrapper

import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle
from shapely.geometry import box
from shapely.ops import transform


ROOT = Path(__file__).resolve().parents[3]
REVISION = ROOT / "output" / "lrhwp_revision"
TABLES = REVISION / "tables_sci"
TABLES_ALT = REVISION / "tables"
OUTDIR = REVISION / "figures" / "graphical_abstract"
NE_SHP = ROOT / "meta" / "geospatial" / "ne_50m_admin_0_countries" / "ne_50m_admin_0_countries.shp"


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


CONTEXT_MAP_NAMES = {
    "Australia",
    "Bangladesh",
    "Bhutan",
    "Brunei",
    "India",
    "Japan",
    "Mongolia",
    "Nepal",
    "New Zealand",
    "Singapore",
    "South Korea",
}


COLORS = {
    "blue": "#0072B2",
    "sky": "#56B4E9",
    "orange": "#E69F00",
    "vermillion": "#D55E00",
    "green": "#009E73",
    "yellow": "#F0E442",
    "purple": "#CC79A7",
    "ink": "#1F2933",
    "muted": "#5F6B77",
    "light": "#EEF2F5",
    "line": "#D7DEE5",
    "dark_gray": "#4B5563",
    "mid_gray": "#9AA5B1",
}


def get_table_path(name: str) -> Path:
    primary = TABLES / name
    if primary.exists():
        return primary
    fallback = TABLES_ALT / name
    if fallback.exists():
        return fallback
    raise FileNotFoundError(name)


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


def iter_polygons(geom):
    if geom.is_empty:
        return
    if geom.geom_type == "Polygon":
        yield geom
    elif geom.geom_type == "MultiPolygon":
        yield from geom.geoms
    elif geom.geom_type == "GeometryCollection":
        for part in geom.geoms:
            yield from iter_polygons(part)


def load_study_map():
    table_path = TABLES_ALT / "Table1_counterfactual_2023_country.csv"
    if not table_path.exists():
        table_path = ROOT / "output" / "final" / "tables" / "Table1_counterfactual_2023_country.csv"
    table1 = pd.read_csv(table_path)

    world = gpd.read_file(NE_SHP).to_crs("EPSG:4326")
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
    world["geometry_shifted"] = world.geometry.map(shift_geometry)
    return world, table1


def add_geometry(ax, geom, x_project, y_project, facecolor, edgecolor, lw, alpha=1.0, zorder=1):
    for poly in iter_polygons(geom):
        coords = np.asarray(poly.exterior.coords)
        if len(coords) < 3:
            continue
        xy = np.column_stack([x_project(coords[:, 0]), y_project(coords[:, 1])])
        ax.add_patch(
            Polygon(
                xy,
                closed=True,
                facecolor=facecolor,
                edgecolor=edgecolor,
                lw=lw,
                alpha=alpha,
                zorder=zorder,
            )
        )


def safe_clip(geom, clip_box):
    try:
        if not geom.is_valid:
            geom = geom.buffer(0)
        return geom.intersection(clip_box)
    except Exception:
        return geom.buffer(0).intersection(clip_box)


def draw_real_study_map(
    ax,
    map_x0=3.0,
    map_y0=10.6,
    map_w=30.0,
    map_h=16.3,
    chip_x=26.6,
    chip_y=25.1,
    source_x=31.9,
    source_y=11.1,
    point_scale=1.0,
):
    world, table1 = load_study_map()
    xmin, xmax = 55.0, 202.0
    ymin, ymax = -25.0, 55.0
    bbox = box(xmin, ymin, xmax, ymax)
    map_x0, map_y0 = 3.0, 10.6
    map_w, map_h = 30.0, 16.3

    def xp(x):
        return map_x0 + (np.asarray(x) - xmin) / (xmax - xmin) * map_w

    def yp(y):
        return map_y0 + (np.asarray(y) - ymin) / (ymax - ymin) * map_h

    # Light ocean frame keeps the true map readable at graphical-abstract scale.
    ax.add_patch(
        FancyBboxPatch(
            (map_x0 - 0.25, map_y0 - 0.25),
            map_w + 0.5,
            map_h + 0.5,
            boxstyle="round,pad=0.02,rounding_size=0.8",
            facecolor="#FBFCFD",
            edgecolor=COLORS["line"],
            lw=0.55,
            zorder=0,
        )
    )

    for _, row in world.iterrows():
        geom = row["geometry_shifted"]
        is_study = pd.notna(row["study_location_name"])
        if not is_study and row.get("ADMIN") not in CONTEXT_MAP_NAMES:
            continue
        if geom.is_empty or not geom.intersects(bbox):
            continue
        clipped = safe_clip(geom, bbox).simplify(0.10, preserve_topology=True)
        add_geometry(
            ax,
            clipped,
            xp,
            yp,
            facecolor="#D8ECF7" if is_study else "#EFF3F6",
            edgecolor=COLORS["blue"] if is_study else "#C8D1DA",
            lw=0.35 if is_study else 0.18,
            alpha=1.0,
            zorder=2 if is_study else 1,
        )

    points = table1[["location_name", "avoidable_number_main_dalys"]].copy()
    max_size = math.sqrt(float(points["avoidable_number_main_dalys"].max()))
    for _, row in points.iterrows():
        lon, lat = POINT_COORDS[row["location_name"]]
        px = float(xp(shift_lon_value(lon)))
        py = float(yp(lat))
        radius = point_scale * (
            0.09 + 0.23 * math.sqrt(max(float(row["avoidable_number_main_dalys"]), 0.0)) / max_size
        )
        ax.add_patch(
            Circle(
                (px, py),
                radius,
                facecolor=COLORS["blue"],
                edgecolor="#FFFFFF",
                lw=0.35,
                alpha=0.92,
                zorder=4,
            )
        )

    chip(ax, chip_x, chip_y, 5.1, 1.7, "34 locations", fc="#FFFFFF", ec=COLORS["blue"], color=COLORS["blue"], size=5.8)
    ax.text(source_x, source_y, "Natural Earth", fontsize=4.8, color=COLORS["mid_gray"], ha="right", va="bottom")


def load_results() -> dict[str, float | int | str]:
    table1 = pd.read_csv(get_table_path("Manuscript_Table_1_key_results_three_line.csv"))
    projection_raw = TABLES_ALT / "Table3A_projection_2050_summary.csv"
    if projection_raw.exists():
        proj = pd.read_csv(projection_raw)
    else:
        proj = pd.read_csv(get_table_path("Supplementary_Table_S3A_projection_2050.csv"))

    def estimate(endpoint: str) -> float:
        hit = table1.loc[table1["Endpoint or comparison"].eq(endpoint), "Estimate"]
        if hit.empty:
            raise KeyError(endpoint)
        return float(str(hit.iloc[0]).replace(",", ""))

    def projection(measure: str, scenario_contains: str, column: str) -> float:
        measure_col = "measure_name" if "measure_name" in proj.columns else "Measure"
        scenario_col = "scenario" if "scenario" in proj.columns else "Scenario"
        col = column
        if col not in proj.columns:
            display_names = {
                "rate_mean": "Rate mean",
                "percent_reduction_vs_observed": "Percent reduction vs baseline",
            }
            col = display_names[column]
        mask = proj[measure_col].str.contains(measure, case=False, regex=False)
        mask &= proj[scenario_col].str.contains(scenario_contains, case=False, regex=False)
        hit = proj.loc[mask, col]
        if hit.empty:
            raise KeyError((measure, scenario_contains, column))
        return float(hit.iloc[0])

    return {
        "avoidable_deaths": estimate("Scenario A potentially avoidable deaths"),
        "avoidable_dalys": estimate("Scenario A potentially avoidable DALYs"),
        "deaths_share_total_pct": estimate("Scenario A deaths as share of total burden"),
        "dalys_share_total_pct": estimate("Scenario A DALYs as share of total burden"),
        "dalys_share_high_bmi_pct": estimate(
            "Scenario A DALYs as share of observed high-BMI-attributable burden"
        ),
        "tmrel_dalys": estimate("Scenario B potentially avoidable DALYs"),
        "tmrel_deaths": estimate("Scenario B potentially avoidable deaths"),
        "high_fpg_locations": int(
            estimate("Locations where high FPG had the highest 30+ internal standardized DALY rate")
        ),
        "high_bmi_locations": int(
            estimate("Locations where high BMI had the highest 30+ internal standardized DALY rate")
        ),
        "smoking_locations": int(
            estimate("Locations where smoking had the highest 30+ internal standardized DALY rate")
        ),
        "dalys_2050_baseline": projection(
            "DALYs", "Baseline projection", "rate_mean"
        ),
        "dalys_2050_scenario_a": projection(
            "DALYs", "Scenario A", "rate_mean"
        ),
        "dalys_2050_scenario_b": projection(
            "DALYs", "Scenario B", "rate_mean"
        ),
        "dalys_2050_scenario_a_reduction_pct": projection(
            "DALYs", "Scenario A", "percent_reduction_vs_observed"
        ),
        "dalys_2050_scenario_b_reduction_pct": projection(
            "DALYs", "Scenario B", "percent_reduction_vs_observed"
        ),
    }


def text_block(ax, x, y, text, width=32, size=7.5, color=None, weight="normal", ha="left",
               va="top", linespacing=1.2, **kwargs):
    color = color or COLORS["ink"]
    if "\n" in text:
        rendered = text
    else:
        wrapper = TextWrapper(width=width, break_long_words=False, break_on_hyphens=False)
        rendered = "\n".join(wrapper.wrap(text))
    return ax.text(
        x,
        y,
        rendered,
        fontsize=size,
        color=color,
        fontweight=weight,
        ha=ha,
        va=va,
        linespacing=linespacing,
        **kwargs,
    )


def chip(ax, x, y, w, h, label, fc="#FFFFFF", ec=None, color=None, size=6.3):
    ec = ec or COLORS["line"]
    color = color or COLORS["ink"]
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.16,rounding_size=0.8",
        linewidth=0.65,
        facecolor=fc,
        edgecolor=ec,
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=size, color=color)


def icon_person(ax, x, y, scale, color, label=None):
    ax.add_patch(Circle((x, y + 2.05 * scale), 0.72 * scale, facecolor=color, edgecolor="white", lw=0.6))
    body = FancyBboxPatch(
        (x - 0.86 * scale, y - 0.4 * scale),
        1.72 * scale,
        2.0 * scale,
        boxstyle=f"round,pad=0.02,rounding_size={0.35 * scale}",
        facecolor=color,
        edgecolor="white",
        lw=0.6,
    )
    ax.add_patch(body)
    if label:
        ax.text(x, y - 0.9 * scale, label, ha="center", va="top", fontsize=5.8, color=COLORS["muted"])


def normal_curve(x, mu, sigma, amp):
    return amp * np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def draw_panel_header(ax, x, y, step, title):
    ax.text(
        x,
        y,
        step,
        fontsize=6.5,
        color="#FFFFFF",
        fontweight="bold",
        ha="center",
        va="center",
        bbox=dict(boxstyle="circle,pad=0.24", facecolor=COLORS["ink"], edgecolor=COLORS["ink"], linewidth=0),
    )
    ax.text(x + 2.0, y + 0.02, title, fontsize=8.8, fontweight="bold", color=COLORS["ink"], ha="left", va="center")


def draw_region_panel(ax):
    draw_panel_header(ax, 3.0, 33.5, "1", "Evidence base")
    text_block(
        ax,
        3.0,
        31.0,
        "GBD 2023 estimates for MASLD/NAFLD-related\ncirrhosis and liver cancer burden.",
        width=39,
        size=6.8,
        color=COLORS["muted"],
    )

    draw_real_study_map(ax)

    chip(ax, 4.0, 7.0, 7.4, 2.2, "Adults 20+", fc="#FFFFFF")
    chip(ax, 13.6, 7.0, 7.8, 2.2, "1990-2023", fc="#FFFFFF")
    chip(ax, 23.6, 7.0, 6.8, 2.2, "WPP 2024", fc="#FFFFFF")

    ax.text(
        3.2,
        4.9,
        "High-BMI exposure, attributable burden, SDI context, and future person-years.",
        fontsize=5.45,
        color=COLORS["muted"],
        ha="left",
        va="top",
    )


def draw_counterfactual_panel(ax):
    draw_panel_header(ax, 36.4, 33.5, "2", "Counterfactual")
    text_block(
        ax,
        36.4,
        31.1,
        "Higher-BMI sex assigned the\nlower-BMI sex exposure distribution\nwithin each location-year-age cell.",
        width=31,
        size=6.8,
        color=COLORS["muted"],
    )

    icon_person(ax, 39.3, 22.2, 1.05, COLORS["orange"], "Higher-BMI sex")
    icon_person(ax, 52.4, 22.2, 1.05, COLORS["blue"], "Lower-BMI sex")

    arrow = FancyArrowPatch(
        (41.2, 24.2),
        (50.5, 24.2),
        arrowstyle="-|>",
        mutation_scale=15,
        lw=1.5,
        color=COLORS["ink"],
    )
    ax.add_patch(arrow)
    ax.text(45.8, 25.5, "exposure scaling", ha="center", va="bottom", fontsize=6.2, color=COLORS["muted"])

    xs = np.linspace(37.0, 54.4, 200)
    y1 = 14.0 + normal_curve(xs, 42.9, 2.15, 4.2)
    y2 = 14.0 + normal_curve(xs, 47.2, 2.15, 4.2)
    ax.plot(xs, y1, color=COLORS["blue"], lw=1.5)
    ax.plot(xs, y2, color=COLORS["orange"], lw=1.5)
    ax.fill_between(xs, 14.0, y1, color=COLORS["blue"], alpha=0.12)
    ax.fill_between(xs, 14.0, y2, color=COLORS["orange"], alpha=0.12)
    ax.plot([37.0, 54.4], [14.0, 14.0], color=COLORS["line"], lw=0.9)
    ax.text(42.8, 18.6, "lower\nexposure", fontsize=5.8, color=COLORS["blue"], ha="center", va="bottom")
    ax.text(48.3, 18.6, "higher\nexposure", fontsize=5.8, color=COLORS["orange"], ha="center", va="bottom")

    chip(ax, 37.0, 9.4, 17.3, 2.7, "Scenario A: sex-equalized high BMI", fc="#E8F4FA", ec=COLORS["blue"], color=COLORS["blue"])
    chip(ax, 37.0, 6.2, 17.3, 2.7, "Scenario B: TMREL upper bound", fc="#FFF8E6", ec=COLORS["orange"], color=COLORS["orange"])
    ax.text(45.7, 5.0, "Nested deterministic layers; not additive", fontsize=5.6, color=COLORS["muted"], ha="center")


def draw_burden_panel(ax, results):
    draw_panel_header(ax, 58.0, 33.5, "3", "2023 burden")
    text_block(
        ax,
        58.0,
        31.1,
        "Potentially avoidable MASLD/NAFLD-related\nliver burden under Scenario A.",
        width=31,
        size=6.8,
        color=COLORS["muted"],
    )

    dalys = f"{results['avoidable_dalys']:,.0f}"
    deaths = f"{results['avoidable_deaths']:,.0f}"
    total_share = f"{results['dalys_share_total_pct']:.2f}%"
    high_bmi_share = f"{results['dalys_share_high_bmi_pct']:.1f}%"

    ax.text(58.4, 24.6, dalys, fontsize=20, fontweight="bold", color=COLORS["blue"], ha="left", va="baseline")
    ax.text(58.4, 22.2, "potentially avoidable DALYs", fontsize=6.7, color=COLORS["ink"], ha="left")
    ax.text(58.4, 18.8, deaths, fontsize=15.5, fontweight="bold", color=COLORS["blue"], ha="left", va="baseline")
    ax.text(63.8, 18.8, "deaths", fontsize=7.0, color=COLORS["ink"], ha="left", va="baseline")

    # Two bars: one for total burden share and one for the high-BMI component share.
    x0, y0, w, h = 58.5, 13.8, 15.8, 1.25
    ax.add_patch(Rectangle((x0, y0), w, h, facecolor=COLORS["light"], edgecolor=COLORS["line"], lw=0.5))
    ax.add_patch(Rectangle((x0, y0), max(w * results["dalys_share_total_pct"] / 5.0, 0.22), h, facecolor=COLORS["blue"], edgecolor="none"))
    ax.text(x0, y0 + 2.0, total_share, fontsize=9.5, fontweight="bold", color=COLORS["blue"], ha="left")
    ax.text(x0 + 5.7, y0 + 2.0, "of total DALY burden", fontsize=6.2, color=COLORS["muted"], ha="left")

    y1 = 9.7
    ax.add_patch(Rectangle((x0, y1), w, h, facecolor=COLORS["light"], edgecolor=COLORS["line"], lw=0.5))
    ax.add_patch(Rectangle((x0, y1), w * results["dalys_share_high_bmi_pct"] / 100.0, h, facecolor=COLORS["blue"], edgecolor="none"))
    ax.text(x0, y1 + 2.0, high_bmi_share, fontsize=9.5, fontweight="bold", color=COLORS["blue"], ha="left")
    ax.text(x0 + 5.8, y1 + 2.0, "of observed high-BMI DALYs", fontsize=6.2, color=COLORS["muted"], ha="left")

    chip(ax, 58.3, 5.5, 16.3, 2.4, "Effect is small but measurable", fc="#FFFFFF", ec=COLORS["line"], color=COLORS["ink"], size=6.0)


def draw_priority_panel(ax, results):
    draw_panel_header(ax, 78.2, 33.5, "4", "Risk priority")
    text_block(
        ax,
        78.2,
        31.1,
        "High BMI was not the dominant regional\nMASLD/NAFLD-related risk signal.",
        width=31,
        size=6.8,
        color=COLORS["muted"],
    )

    labels = ["High FPG", "High BMI", "Smoking"]
    counts = [
        results["high_fpg_locations"],
        results["high_bmi_locations"],
        results["smoking_locations"],
    ]
    colors = [COLORS["vermillion"], COLORS["blue"], COLORS["dark_gray"]]
    yvals = [25.5, 22.2, 18.9]
    for label, count, color, y in zip(labels, counts, colors, yvals):
        ax.text(78.4, y + 0.45, label, fontsize=6.4, color=COLORS["ink"], ha="left", va="center")
        ax.add_patch(Rectangle((85.1, y), 9.2, 0.9, facecolor=COLORS["light"], edgecolor="none"))
        ax.add_patch(Rectangle((85.1, y), 9.2 * count / 34.0, 0.9, facecolor=color, edgecolor="none"))
        ax.text(94.9, y + 0.45, f"{count}/34", fontsize=7.0, fontweight="bold", color=color, ha="left", va="center")

    ax.plot([78.4, 97.4], [15.2, 15.2], color=COLORS["line"], lw=0.8)
    ax.text(78.4, 13.6, "2050 internal DALY-rate scenario", fontsize=6.5, fontweight="bold", color=COLORS["ink"])
    base = results["dalys_2050_baseline"]
    vals = [
        ("Baseline", results["dalys_2050_baseline"], COLORS["mid_gray"]),
        ("Scenario A", results["dalys_2050_scenario_a"], COLORS["blue"]),
        ("Scenario B", results["dalys_2050_scenario_b"], COLORS["orange"]),
    ]
    maxv = base * 1.08
    for i, (label, value, color) in enumerate(vals):
        y = 11.6 - i * 2.0
        ax.text(78.4, y + 0.36, label, fontsize=5.7, color=COLORS["muted"], ha="left", va="center")
        ax.add_patch(Rectangle((85.0, y), 9.4, 0.72, facecolor=COLORS["light"], edgecolor="none"))
        ax.add_patch(Rectangle((85.0, y), 9.4 * value / maxv, 0.72, facecolor=color, edgecolor="none"))
        ax.text(94.9, y + 0.36, f"{value:.1f}", fontsize=5.7, color=color, ha="left", va="center")

    ax.text(
        78.4,
        4.4,
        f"Scenario A: -{results['dalys_2050_scenario_a_reduction_pct']:.1f}% | "
        f"TMREL upper bound: -{results['dalys_2050_scenario_b_reduction_pct']:.1f}%",
        fontsize=5.8,
        color=COLORS["muted"],
        ha="left",
    )
    chip(ax, 78.3, 1.8, 19.2, 2.0, "Glycaemic-risk prevention remains central", fc="#FFF1EC", ec=COLORS["vermillion"], color=COLORS["vermillion"], size=5.8)


def draw_panel_header_16x9(ax, x, y, step, title):
    ax.text(
        x,
        y,
        step,
        fontsize=7.2,
        color="#FFFFFF",
        fontweight="bold",
        ha="center",
        va="center",
        bbox=dict(boxstyle="circle,pad=0.25", facecolor=COLORS["ink"], edgecolor=COLORS["ink"], linewidth=0),
    )
    ax.text(x + 2.5, y + 0.02, title, fontsize=10.2, fontweight="bold", color=COLORS["ink"], ha="left", va="center")


def draw_region_panel_16x9(ax):
    draw_panel_header_16x9(ax, 5.2, 73.2, "1", "Evidence base")
    text_block(
        ax,
        5.2,
        69.4,
        "GBD 2023 estimates for MASLD/NAFLD-related\ncirrhosis and liver cancer burden.",
        width=52,
        size=7.6,
        color=COLORS["muted"],
    )
    draw_real_study_map(
        ax,
        map_x0=3.8,
        map_y0=40.0,
        map_w=62.0,
        map_h=33.7,
        chip_x=56.0,
        chip_y=68.5,
        source_x=64.2,
        source_y=40.8,
        point_scale=1.35,
    )
    chip(ax, 6.0, 21.0, 11.5, 3.2, "Adults 20+", fc="#FFFFFF", size=7.2)
    chip(ax, 23.7, 21.0, 12.2, 3.2, "1990-2023", fc="#FFFFFF", size=7.2)
    chip(ax, 42.1, 21.0, 10.8, 3.2, "WPP 2024", fc="#FFFFFF", size=7.2)
    ax.text(
        5.6,
        17.0,
        "High-BMI exposure, attributable burden, SDI context, and future person-years.",
        fontsize=6.5,
        color=COLORS["muted"],
        ha="left",
        va="top",
    )


def draw_burden_panel_16x9(ax, results):
    draw_panel_header_16x9(ax, 73.0, 73.2, "2", "2023 burden")
    text_block(
        ax,
        73.0,
        69.2,
        "Potentially avoidable MASLD/NAFLD-related\nliver burden under Scenario A.",
        width=48,
        size=7.6,
        color=COLORS["muted"],
    )
    dalys = f"{results['avoidable_dalys']:,.0f}"
    deaths = f"{results['avoidable_deaths']:,.0f}"
    total_share = f"{results['dalys_share_total_pct']:.2f}%"
    high_bmi_share = f"{results['dalys_share_high_bmi_pct']:.1f}%"

    ax.text(73.2, 58.3, dalys, fontsize=28, fontweight="bold", color=COLORS["blue"], ha="left", va="baseline")
    ax.text(73.4, 54.4, "potentially avoidable DALYs", fontsize=8.2, color=COLORS["ink"], ha="left")
    ax.text(73.4, 48.7, deaths, fontsize=20, fontweight="bold", color=COLORS["blue"], ha="left", va="baseline")
    ax.text(82.0, 48.8, "deaths", fontsize=8.1, color=COLORS["ink"], ha="left", va="baseline")

    x0, y0, w, h = 73.6, 42.5, 31.2, 1.55
    ax.add_patch(Rectangle((x0, y0), w, h, facecolor=COLORS["light"], edgecolor=COLORS["line"], lw=0.5))
    ax.add_patch(Rectangle((x0, y0), max(w * results["dalys_share_total_pct"] / 5.0, 0.32), h, facecolor=COLORS["blue"], edgecolor="none"))
    ax.text(x0, y0 + 2.9, total_share, fontsize=11.0, fontweight="bold", color=COLORS["blue"], ha="left")
    ax.text(x0 + 10.0, y0 + 2.9, "of total DALY burden", fontsize=7.3, color=COLORS["muted"], ha="left")

    y1 = 36.4
    ax.add_patch(Rectangle((x0, y1), w, h, facecolor=COLORS["light"], edgecolor=COLORS["line"], lw=0.5))
    ax.add_patch(Rectangle((x0, y1), w * results["dalys_share_high_bmi_pct"] / 100.0, h, facecolor=COLORS["blue"], edgecolor="none"))
    ax.text(x0, y1 + 2.9, high_bmi_share, fontsize=11.0, fontweight="bold", color=COLORS["blue"], ha="left")
    ax.text(x0 + 10.0, y1 + 2.9, "of observed high-BMI DALYs", fontsize=7.3, color=COLORS["muted"], ha="left")

    chip(ax, 73.4, 30.5, 31.8, 3.5, "Effect is small but measurable", fc="#FFFFFF", ec=COLORS["line"], color=COLORS["ink"], size=7.0)


def draw_priority_panel_16x9(ax, results):
    draw_panel_header_16x9(ax, 114.8, 73.2, "3", "Risk priority")
    text_block(
        ax,
        114.8,
        69.2,
        "High BMI was not the dominant regional\nMASLD/NAFLD-related risk signal.",
        width=43,
        size=7.6,
        color=COLORS["muted"],
    )
    labels = ["High FPG", "High BMI", "Smoking"]
    counts = [
        results["high_fpg_locations"],
        results["high_bmi_locations"],
        results["smoking_locations"],
    ]
    colors = [COLORS["vermillion"], COLORS["blue"], COLORS["dark_gray"]]
    yvals = [58.4, 52.6, 46.8]
    for label, count, color, y in zip(labels, counts, colors, yvals):
        ax.text(115.0, y + 0.6, label, fontsize=7.7, color=COLORS["ink"], ha="left", va="center")
        ax.add_patch(Rectangle((126.7, y), 17.8, 1.3, facecolor=COLORS["light"], edgecolor="none"))
        ax.add_patch(Rectangle((126.7, y), 17.8 * count / 34.0, 1.3, facecolor=color, edgecolor="none"))
        ax.text(146.0, y + 0.62, f"{count}/34", fontsize=8.2, fontweight="bold", color=color, ha="left", va="center")

    ax.plot([115.0, 153.4], [40.5, 40.5], color=COLORS["line"], lw=0.8)
    ax.text(115.0, 37.9, "2050 internal DALY-rate scenario", fontsize=7.6, fontweight="bold", color=COLORS["ink"])
    base = results["dalys_2050_baseline"]
    vals = [
        ("Baseline", results["dalys_2050_baseline"], COLORS["mid_gray"]),
        ("Scenario A", results["dalys_2050_scenario_a"], COLORS["blue"]),
        ("Scenario B", results["dalys_2050_scenario_b"], COLORS["orange"]),
    ]
    maxv = base * 1.08
    for i, (label, value, color) in enumerate(vals):
        y = 35.2 - i * 3.8
        ax.text(115.0, y + 0.52, label, fontsize=6.7, color=COLORS["muted"], ha="left", va="center")
        ax.add_patch(Rectangle((126.7, y), 17.8, 1.05, facecolor=COLORS["light"], edgecolor="none"))
        ax.add_patch(Rectangle((126.7, y), 17.8 * value / maxv, 1.05, facecolor=color, edgecolor="none"))
        ax.text(146.0, y + 0.52, f"{value:.1f}", fontsize=6.7, color=color, ha="left", va="center")

    chip(ax, 115.0, 41.4, 38.0, 3.4, "Glycaemic-risk prevention remains central", fc="#FFF1EC", ec=COLORS["vermillion"], color=COLORS["vermillion"], size=6.9)


def draw_counterfactual_panel_16x9(ax):
    draw_panel_header_16x9(ax, 73.0, 23.8, "4", "Counterfactual")
    text_block(
        ax,
        73.0,
        20.5,
        "Higher-BMI sex assigned the lower-BMI sex exposure distribution within each location-year-age cell.",
        width=72,
        size=7.1,
        color=COLORS["muted"],
    )

    icon_person(ax, 82.5, 8.8, 1.25, COLORS["orange"], "Higher-BMI sex")
    icon_person(ax, 128.4, 8.8, 1.25, COLORS["blue"], "Lower-BMI sex")
    ax.add_patch(
        FancyArrowPatch(
            (86.0, 12.0),
            (124.8, 12.0),
            arrowstyle="-|>",
            mutation_scale=18,
            lw=1.7,
            color=COLORS["ink"],
        )
    )
    ax.text(105.3, 13.8, "exposure scaling", ha="center", va="bottom", fontsize=7.1, color=COLORS["muted"])

    xs = np.linspace(90.0, 121.0, 220)
    y1 = 5.0 + normal_curve(xs, 100.1, 3.6, 6.5)
    y2 = 5.0 + normal_curve(xs, 110.0, 3.6, 6.5)
    ax.plot(xs, y1, color=COLORS["blue"], lw=1.7)
    ax.plot(xs, y2, color=COLORS["orange"], lw=1.7)
    ax.fill_between(xs, 5.0, y1, color=COLORS["blue"], alpha=0.12)
    ax.fill_between(xs, 5.0, y2, color=COLORS["orange"], alpha=0.12)
    ax.plot([90.0, 121.0], [5.0, 5.0], color=COLORS["line"], lw=0.9)
    ax.text(100.2, 11.8, "lower\nexposure", fontsize=6.3, color=COLORS["blue"], ha="center", va="bottom")
    ax.text(111.0, 11.8, "higher\nexposure", fontsize=6.3, color=COLORS["orange"], ha="center", va="bottom")

    chip(ax, 134.0, 11.5, 19.5, 3.3, "Scenario A", fc="#E8F4FA", ec=COLORS["blue"], color=COLORS["blue"], size=7.0)
    chip(ax, 134.0, 6.9, 19.5, 3.3, "Scenario B: TMREL", fc="#FFF8E6", ec=COLORS["orange"], color=COLORS["orange"], size=7.0)
    ax.text(143.8, 5.3, "Nested; not additive", fontsize=6.3, color=COLORS["muted"], ha="center")


def build_figure(results):
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.unicode_minus": False,
        }
    )
    fig, ax = plt.subplots(figsize=(13.28, 5.31), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 40)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")
    ax.add_patch(Rectangle((0, 0), 100, 40, facecolor="#FFFFFF", edgecolor="none"))

    ax.text(
        2.6,
        38.3,
        "Sex-equalized high-BMI exposure and potentially avoidable MASLD/NAFLD liver burden",
        fontsize=12.5,
        fontweight="bold",
        color=COLORS["ink"],
        ha="left",
        va="center",
    )
    ax.text(
        2.7,
        36.35,
        "GBD 2023 counterfactual analysis across Southeast Asia, East Asia, and Oceania",
        fontsize=6.8,
        color=COLORS["muted"],
        ha="left",
        va="center",
    )

    for x in [34.8, 56.0, 76.6]:
        ax.plot([x, x], [4.7, 34.5], color=COLORS["line"], lw=0.8)

    draw_region_panel(ax)
    draw_counterfactual_panel(ax)
    draw_burden_panel(ax, results)
    draw_priority_panel(ax, results)

    footnote = (
        "Scenario A assigns the higher-BMI sex the lower-BMI sex exposure distribution within each location-year-age cell.\n"
        "Scenario B is a high-BMI-at-TMREL upper-bound comparator; the scenarios are nested and not additive.\n"
        "Projection rates are internal scenarios, not IHME official forecasts."
    )
    text_block(ax, 2.7, 0.85, footnote, width=190, size=4.85, color=COLORS["muted"], va="bottom", linespacing=1.08)
    return fig


def build_figure_16x9(results):
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.unicode_minus": False,
        }
    )
    fig = plt.figure(figsize=(13.333333, 7.5), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 90)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")
    ax.add_patch(Rectangle((0, 0), 160, 90, facecolor="#FFFFFF", edgecolor="none"))

    ax.text(
        5.0,
        85.0,
        "Sex-equalized high-BMI exposure and potentially avoidable MASLD/NAFLD liver burden",
        fontsize=15.0,
        fontweight="bold",
        color=COLORS["ink"],
        ha="left",
        va="center",
    )
    ax.text(
        5.2,
        80.8,
        "GBD 2023 counterfactual analysis across Southeast Asia, East Asia, and Oceania",
        fontsize=8.4,
        color=COLORS["muted"],
        ha="left",
        va="center",
    )

    ax.plot([68.0, 68.0], [11.0, 76.0], color=COLORS["line"], lw=0.85)
    ax.plot([110.0, 110.0], [27.0, 76.0], color=COLORS["line"], lw=0.85)
    ax.plot([70.0, 156.0], [26.0, 26.0], color=COLORS["line"], lw=0.85)

    draw_region_panel_16x9(ax)
    draw_burden_panel_16x9(ax, results)
    draw_priority_panel_16x9(ax, results)
    draw_counterfactual_panel_16x9(ax)

    footnote = (
        "Scenario A assigns the higher-BMI sex the lower-BMI sex exposure distribution within each location-year-age cell.\n"
        "Scenario B is a high-BMI-at-TMREL upper-bound comparator; the scenarios are nested and not additive.\n"
        "Projection rates are internal scenarios, not IHME official forecasts."
    )
    text_block(ax, 5.0, 2.8, footnote, width=210, size=5.6, color=COLORS["muted"], va="bottom", linespacing=1.08)
    return fig


def save_outputs(fig, stem, tight=True):
    save_kwargs = {"bbox_inches": "tight", "pad_inches": 0.05} if tight else {}
    fig.savefig(stem.with_suffix(".svg"), **save_kwargs)
    fig.savefig(stem.with_suffix(".pdf"), **save_kwargs)
    fig.savefig(stem.with_suffix(".png"), dpi=300, **save_kwargs)
    fig.savefig(stem.with_suffix(".tiff"), dpi=300, pil_kwargs={"compression": "tiff_lzw"}, **save_kwargs)
    plt.close(fig)

    for suffix in [".png", ".tiff"]:
        image_path = stem.with_suffix(suffix)
        image = Image.open(image_path)
        if image.mode == "RGBA":
            background = Image.new("RGB", image.size, "white")
            background.paste(image, mask=image.split()[-1])
            save_kwargs = {"compression": "tiff_lzw"} if suffix == ".tiff" else {}
            background.save(image_path, **save_kwargs)


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    results = load_results()
    fig = build_figure(results)
    stem = OUTDIR / "Graphical_Abstract_LRHWP"
    save_outputs(fig, stem, tight=True)

    fig16 = build_figure_16x9(results)
    stem16 = OUTDIR / "Graphical_Abstract_LRHWP_16x9"
    save_outputs(fig16, stem16, tight=False)

    source = pd.DataFrame([results])
    source.to_csv(OUTDIR / "Graphical_Abstract_LRHWP_source_values.csv", index=False)
    print(f"Saved graphical abstract outputs to {OUTDIR}")


if __name__ == "__main__":
    main()
