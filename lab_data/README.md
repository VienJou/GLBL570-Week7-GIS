# GLBL 570 · Week 7 lab data (QGIS-ready)

Everything here opens in QGIS 3.x without plug-ins. Vector layers are **Shapefiles**, tables are **CSV** (each with a `.csvt` type file), rasters are **GeoTIFF**.
The companion notebook `../GLBL570_Week7_GIS_Lab.ipynb` runs the same steps in Python.

## Files

| Folder / file | Type | CRS | What it is |
|---|---|---|---|
| `vector/us_counties_geometry.shp` | polygons, 3,144 | EPSG:4269 | U.S. county boundaries with IDs only — the **join target** |
| `vector/us_counties_acs2022.shp` | polygons, 3,144 | EPSG:4269 | Same counties with ACS 2018–2022 attributes (field names ≤ 10 characters, see `us_counties_acs2022_field_dictionary.csv`) |
| `vector/us_states.shp` | polygons, 51 | EPSG:4269 | States + DC, dissolved from the counties (population, poverty totals) |
| `vector/usgs_earthquakes_2025_m25.shp` | 3-D points, 3,754 | EPSG:4269 | USGS earthquakes 2025, M ≥ 2.5 (z = depth, km) |
| `vector/world_countries_ne110m.shp` | polygons, 177 | EPSG:4326 | Natural Earth 1:110m countries (codes `ISO_A3`, `ISO_A3_EH`, `ADM0_A3`) |
| `vector/holc_chicago_1930s.shp` | polygons, 703 | EPSG:4326 | HOLC "redlining" grades A–D, Chicago (Mapping Inequality) |
| `tables/acs2022_county_attributes.csv` | table | — | ACS attributes keyed by `geoid` (5-digit text) — join to `us_counties_geometry` on `GEOID` |
| `tables/worldbank_gdp_per_capita_2022.csv` | table | — | World Bank GDP per capita (current US$), 2022, keyed by `iso3` |
| `tables/ndgain_climate_index_2022.csv` | table | — | ND-GAIN climate index, vulnerability, readiness (2022), keyed by `iso3` |
| `tables/usgs_earthquakes_2025_m25_latlon.csv` | table with lon/lat | EPSG:4326 | Same earthquakes as a plain table — **geocode** it with *Add Delimited Text Layer* |
| `tables/ucdp_ged_events_2023.csv` | table with lon/lat | EPSG:4326 | UCDP georeferenced conflict events, 2023 (24,205 rows) — optional OSINT layer |
| `raster/illinois_dem_srtm_150m.tif` | int16, 1 band | EPSG:5070 | SRTM elevation (m), 150 m cells, Illinois |
| `raster/illinois_landcover_nlcd2021_150m.tif` | uint8, 1 band + colour table | EPSG:5070 | NLCD 2021 land cover classes, 150 m; class names in `raster/nlcd_classes.csv` |
| `raster/champaign_sentinel2_2023_10m.tif` | uint16, 4 bands | EPSG:5070 | Sentinel-2 L2A median, Jun–Sep 2023, Champaign–Urbana: bands 1–4 = red, green, blue, NIR (reflectance × 10,000) |
| `raster/illinois_worldpop_2020_1km.tif` | float32, 1 band | EPSG:5070 | WorldPop 2020 people per 1 km cell, Illinois |
| `other_formats/illinois_counties.geojson`, `.kml` | polygons, 102 | WGS 84 | Illinois counties in two web formats |

## How to add each kind of file in QGIS
- **Shapefile / GeoTIFF / GeoJSON / KML:** drag the file (`.shp`, `.tif`, …) from the Browser panel onto the map.
- **CSV to join (no coordinates):** *Layer → Add Layer → Add Delimited Text Layer* → *Geometry definition: No geometry* → then on the target layer: *Properties → Joins → +*.
- **CSV with coordinates:** *Add Delimited Text Layer* → *Point coordinates*, X field = `longitude`, Y field = `latitude`, Geometry CRS = EPSG:4326.

## 60-minute lab sheet (slide 48)
| Time | Step in QGIS |
|---|---|
| 0–10′ | Add `world_countries_ne110m.shp` (or `us_counties_geometry.shp`); open the attribute table. |
| 10–25′ | Add `worldbank_gdp_per_capita_2022.csv` / `ndgain_climate_index_2022.csv` (no geometry) and join: **join field `iso3`, target field `ISO_A3_EH`**. (For the U.S. track: `acs2022_county_attributes.csv`, `geoid` = `GEOID`.) *Symbology → Graduated* on the joined field. |
| 25–40′ | Try at least two modes (Quantile, Natural Breaks, Equal Interval) and write down the breaks. Set the project CRS to **EPSG:8857 Equal Earth** (world) or **EPSG:5070** (U.S.). Missing data: a separate grey/hatched class, never white. |
| 40–50′ | *Project → New Print Layout*: title, legend, source line, CRS note → export PNG/PDF. Write the 200–300-word memo. |
| 50–60′ | Optional: add `ucdp_ged_events_2023.csv` as points (aggregate before publishing!), or `usgs_earthquakes_2025_m25_latlon.csv` → *Processing → Join attributes by location (summary)* on counties; rasters → *Processing → Zonal statistics*. |

## Known pitfalls (on purpose — they are part of the lesson)
- **Keep the `.csvt` next to each CSV.** Without it QGIS reads `geoid` as a number, drops leading zeros (`01001` → `1001`) and 318 counties (7 states) fail to join.
- **Join countries on `ISO_A3_EH`, not `ISO_A3`.** Natural Earth stores France and Norway as `ISO_A3 = -99`. Even with `ISO_A3_EH`, 8 countries stay unmatched (e.g. Taiwan, Western Sahara, Kosovo) — an example of omission. The World Bank table also contains regional aggregates ("Arab World", …) that match no country.
- **Shapefile field names are cut to 10 characters**; `vector/us_counties_acs2022_field_dictionary.csv` maps them back to the ACS names.
- **Median income:** one county (Loving County, TX) has no estimate. The raw CSV stores the Census code `-666666666`; the Shapefile stores NULL. Never map the code as a value.
- **Earthquake points vs. county boundaries:** 464 events in coastal water (mostly Alaska) fall outside the generalised 1:5M shoreline and are dropped by an *intersects* join.
- **Rasters are all EPSG:5070 (metres)**; reproject other layers (or let QGIS do it on the fly) before zonal statistics. NLCD was resampled from 30 m to 150 m by nearest neighbour; the SRTM DEM by bilinear interpolation (10 cells in southern Illinois fall below 80 m — SRTM artefacts near rivers).
- **WorldPop is a model, ACS is a survey.** WorldPop sums to 13.41 M people in Illinois vs. 12.76 M in ACS (+5 %).
- **HOLC grades** were cleaned of trailing spaces (`"A "`, `"C "`); 20 Chicago areas have no grade.

## Sources and terms
- U.S. Census Bureau: TIGER/Line 2022 cartographic boundaries; ACS 2018–2022 5-year estimates (tables B02001, B08301, B17001, B19013). Public domain.
- U.S. Geological Survey: Earthquake Catalog (FDSN), 2025, M ≥ 2.5. Public domain.
- Natural Earth: Admin 0 – Countries, 1:110m (v5.1). Public domain.
- World Bank: World Development Indicators, NY.GDP.PCAP.CD (2022). CC BY 4.0.
- Notre Dame Global Adaptation Initiative (ND-GAIN) country index, 2022 scores. Free for non-commercial use with attribution.
- Uppsala Conflict Data Program: UCDP GED v24.1 (Sundberg & Melander 2013; Davies et al. 2024). CC BY 4.0.
- Mapping Inequality: Redlining in New Deal America, University of Richmond Digital Scholarship Lab. CC BY-NC-SA 4.0.
- Rasters via Google Earth Engine: SRTM v3 (NASA/USGS), NLCD 2021 (USGS/MRLC), Sentinel-2 L2A (Copernicus/ESA), WorldPop 2020 (University of Southampton, CC BY 4.0).

Rebuild: `python scripts/build_lab_data.py` (vectors and tables, from downloads listed above) and `python scripts/fetch_rasters_gee.py` (rasters; needs an Earth Engine service-account key in `GEE_KEY`).
