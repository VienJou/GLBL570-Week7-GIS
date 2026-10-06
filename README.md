# GLBL 570 Week 7: Fundamentals of GIS & Mapping (hands-on notebook + QGIS lab data)

`GLBL570_Week7_GIS_Lab.ipynb` carries out the GIS operations of the Week 7 lecture (`GLBL570_Week7_v5.pptx`) **in slide order**: §1 What is GIS → §8 Lab & milestone, plus an appendix for the reference slides. Every step names its slide and its QGIS equivalent.
The same data are packed for students in **`lab_data/`** (Shapefiles, CSV tables to join or geocode, GeoTIFF rasters) for the 60-minute QGIS lab.

## Contents

| Path | What it is |
|---|---|
| `GLBL570_Week7_GIS_Lab.ipynb` | The notebook (saved with outputs) |
| `lab_data/` | QGIS-ready data pack + `README.md` (file list, how to load, 60-minute lab sheet, pitfalls, sources) |
| `us_census_gis_lab 2/` | Original course pack: GeoPackage (counties + earthquakes), ACS CSV + `.csvt`, data README (Chinese) |
| `outputs/` | Files the notebook writes: maps (PNG/PDF), GeoJSON/KML/Shapefile/GeoPackage, memo; plus the slide-34 figure and its script |
| `scripts/build_lab_data.py` | Rebuilds `lab_data/vector`, `tables`, `other_formats` from the original pack and public downloads |
| `scripts/fetch_rasters_gee.py` | Rebuilds `lab_data/raster` from Google Earth Engine (needs a service-account key) |
| `requirements.txt` | Python libraries for the notebook |

## Data in `lab_data/`
- U.S. counties with ACS 2018–2022 attributes, states, USGS 2025 earthquakes (Shapefile + lat/lon CSV)
- World countries (Natural Earth) + World Bank GDP per capita 2022 + ND-GAIN climate index 2022 (CSV to join on ISO3)
- UCDP conflict events 2023 (lat/lon CSV, optional OSINT layer); HOLC redlining grades for Chicago
- Rasters (EPSG:5070): SRTM elevation and NLCD 2021 land cover for Illinois (150 m), Sentinel-2 summer 2023 for Champaign–Urbana (10 m, 4 bands), WorldPop 2020 for Illinois (1 km)

## Run
* CPU only, no GPU and no internet needed. Full run ≈ 70 s; peak memory ≈ 2.6 GB (use a machine or kernel with ≥ 4 GB).
* Tested on Python 3.9 (NumPy 1.26, pandas 2.3) and Python 3.12 (NumPy 2.5, pandas 3.0); on I-GUIDE use the `geoai-edu` kernel.
* Python ≥ 3.9 with the libraries in `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```
* Open the notebook from the repository root (paths are relative), then *Run All*.
* Rebuilding the data is optional and needs extra packages: `requests` for `build_lab_data.py`; `earthengine-api`, `google-auth` and an Earth Engine key (`GEE_KEY`, `GEE_PROJECT`) for `fetch_rasters_gee.py`.

## Data sources
U.S. Census Bureau (TIGER/Line 2022, ACS 2018–2022 5-year); U.S. Geological Survey Earthquake Catalog (2025, M ≥ 2.5); Natural Earth; World Bank WDI; ND-GAIN (University of Notre Dame); UCDP GED v24.1; Mapping Inequality (University of Richmond); SRTM, NLCD 2021, Sentinel-2 L2A and WorldPop 2020 via Google Earth Engine. Licences are listed in `lab_data/README.md`.
