"""Slide figure 'Same Data, Three Stories' from the lab data (notebook §5.6): 3 maps + 3 histograms."""
from pathlib import Path

import geopandas as gpd
import mapclassify as mc
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

ROOT = Path(__file__).resolve().parents[1]
NAVY, GREY, RED, BAR = "#1F2A5A", "#5F6B7A", "#C0504D", "#C9D6E0"
BLUES = ListedColormap(["#E8F0F8", "#B5D2E3", "#70A9C9", "#2E7CA8", "#0A5A85"])

counties = gpd.read_file(ROOT / "us_census_gis_lab 2" / "us_census_acs2022.gpkg", layer="us_counties_acs2022")
y = counties["poverty_pct"]
lower48 = counties[~counties["state_abbr"].isin(["AK", "HI"])].to_crs(5070)
schemes = [("Equal Interval", mc.EqualInterval(y, k=5), "cuts the RANGE into 5 equal steps"),
           ("Quantile", mc.Quantiles(y, k=5), "puts an equal COUNT in each class"),
           ("Natural Breaks (Jenks)", mc.FisherJenks(y, k=5), "minimises variance WITHIN classes")]

fig = plt.figure(figsize=(8.58, 4.345), dpi=200)
fig.text(0.5, 0.985, f"One dataset · {len(y):,} U.S. counties · % below poverty (darker = higher) · 5 classes",
         ha="center", va="top", fontsize=11.5, fontweight="bold", color=NAVY)
for j, (name, cls, how) in enumerate(schemes):
    x0 = 0.01 + j * 0.335
    ax = fig.add_axes([x0, 0.535, 0.31, 0.37])
    yb = cls.yb[lower48.index.to_numpy()]
    lower48.assign(c=yb).plot(ax=ax, column="c", cmap=BLUES, vmin=0, vmax=4, edgecolor="white", lw=0.05)
    ax.set_axis_off()
    ax.set_title(name, fontsize=11, fontweight="bold", color=NAVY, pad=2)
    lx = fig.add_axes([x0 + 0.02, 0.51, 0.27, 0.026])
    lx.imshow(np.arange(5)[None, :], cmap=BLUES, vmin=0, vmax=4, aspect="auto", extent=(0, 5, 0, 1))
    lx.set_xticks(range(6))
    lx.set_xticklabels([f"{v:.1f}" for v in [y.min(), *cls.bins]], fontsize=8, color=GREY)
    lx.set_yticks([])
    lx.tick_params(axis="x", length=1.5, pad=1)
    for side in lx.spines.values():
        side.set_color("white")
    fig.text(x0 + 0.155, 0.425, how, ha="center", fontsize=8.5, color=GREY)
    fig.text(x0 + 0.155, 0.38, f"darkest class: {cls.counts[-1]:,} of {len(y):,} counties",
             ha="center", fontsize=8.5, fontweight="bold", color=RED)

    hx = fig.add_axes([x0 + 0.01, 0.12, 0.29, 0.2])
    hx.hist(y, bins=np.arange(0, 57, 1.5), color=BAR, edgecolor="white", lw=0.4)
    for b in cls.bins[:-1]:
        hx.axvline(b, color=RED, ls=(0, (4, 3)), lw=1.3)
    hx.set_xlim(0, 57)
    hx.set_yticks([])
    hx.set_xticks([0, 10, 20, 30, 40, 50])
    hx.tick_params(axis="x", colors=GREY, labelsize=8.5, length=2)
    for side in ("top", "right", "left"):
        hx.spines[side].set_visible(False)
    hx.spines["bottom"].set_color(BAR)
    hx.set_xlabel("% below poverty · red = class breaks", fontsize=8.5, color=GREY, labelpad=2)

fig.text(0.5, 0.005, "Maps show the lower 48; classes computed over all 50 states + DC. "
         "Source: U.S. Census Bureau, ACS 2018–2022 5-year.", ha="center", va="bottom", fontsize=7, color=GREY)
out = ROOT / "outputs" / "classification_three_schemes_slide.png"
fig.savefig(out, dpi=200, facecolor="white")
print("wrote", out, [(n, c.counts[-1]) for n, c, _ in schemes])
