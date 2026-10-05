# GLBL 570 Week 7: Fundamentals of GIS & Mapping (hands-on notebook)

`GLBL570_Week7_GIS_Lab.ipynb` walks through the Week 7 lecture in slide order (§1 What is GIS → §9 Lab & milestone), running each GIS operation on U.S. county ACS data and 2025 USGS earthquakes.

## Contents

| Path | What it is |
|---|---|
| `GLBL570_Week7_GIS_Lab.ipynb` | The notebook (saved with outputs) |
| `us_census_gis_lab 2/` | Input data: GeoPackage (counties + earthquakes), ACS attribute CSV + `.csvt`, data README (Chinese) |
| `outputs/` | Files the notebook writes: maps (PNG/PDF), GeoTIFF, GeoJSON/KML/Shapefile, GeoPackage, memo |
| `requirements.txt` | Python libraries |

## Run

* CPU only, no GPU needed. Full run ≈ 1 minute, < 2 GB RAM.
* Python ≥ 3.9 with the libraries in `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```
* Open the notebook from the repository root (paths are relative), then *Run All*.

## Data sources

U.S. Census Bureau, 2018–2022 ACS 5-Year Estimates and 2022 TIGER/Line boundaries; U.S. Geological Survey Earthquake Catalog (2025, M ≥ 2.5).
