"""Build the QGIS-ready data pack lab_data/ (Shapefiles, CSV tables to join/geocode, other formats).

Inputs: us_census_gis_lab 2/ (GeoPackage + CSV) and raw downloads in plan/raw/ (Natural Earth 110m,
World Bank GDP per capita, ND-GAIN, UCDP GED, Mapping Inequality HOLC). See lab_data/README.md for URLs. Rasters are built separately by fetch_rasters_gee.py.
Run from the repository root:  python scripts/build_lab_data.py
"""
import json
import shutil
import warnings
import zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "us_census_gis_lab 2"
RAW = ROOT / "plan" / "raw"
OUT = ROOT / "lab_data"
VEC, TAB, OTHER = OUT / "vector", OUT / "tables", OUT / "other_formats"
for d in (VEC, TAB, OTHER):
    d.mkdir(parents=True, exist_ok=True)

# Shapefile (.dbf) field names are limited to 10 characters, so long ACS names get short aliases.
ACS_FIELDS = {
    "geoid": "geoid", "state_fips": "state_fips", "county_fips": "cnty_fips", "state_abbr": "state_abbr",
    "state_name": "state_name", "county_name": "cnty_name", "county_label": "cnty_label",
    "land_km2": "land_km2", "water_km2": "water_km2", "population": "pop",
    "pop_density_km2": "pop_dens", "median_hh_income": "med_income", "poverty_universe": "pov_univ",
    "below_poverty": "below_pov", "poverty_pct": "pov_pct",
    "race_white": "r_white", "race_black": "r_black", "race_aian": "r_aian", "race_asian": "r_asian",
    "race_nhpi": "r_nhpi", "race_other": "r_other", "race_two_plus": "r_two_plus",
    "commuters_total": "commuters", "commute_drive_alone": "c_drive", "commute_carpool": "c_carpool",
    "commute_transit": "c_transit", "commute_bicycle": "c_bicycle", "commute_walk": "c_walk",
    "commute_other": "c_other", "commute_wfh": "c_wfh", "transit_pct": "transit_pc", "wfh_pct": "wfh_pct",
}
assert all(len(v) <= 10 for v in ACS_FIELDS.values()), "dBASE field names must be <= 10 characters"
QUAKE_FIELDS = ["id", "mag", "place", "time", "updated", "felt", "cdi", "mmi", "alert", "status",
                "tsunami", "sig", "net", "nst", "dmin", "rms", "gap", "magType", "type", "title"]


def write_shp(gdf, name):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        gdf.to_file(VEC / f"{name}.shp", encoding="UTF-8")


def write_csvt(df, path):
    # QGIS reads column types from a .csvt next to the CSV (keeps GEOID / ISO codes as text).
    types = ['"String"' if df[c].dtype == object else ('"Integer"' if np.issubdtype(df[c].dtype, np.integer) else '"Real"')
             for c in df.columns]
    path.with_suffix(".csvt").write_text(",".join(types) + "\n")


# ---------------------------------------------------------------- US counties, states, earthquakes
counties = gpd.read_file(SRC / "us_census_acs2022.gpkg", layer="us_counties_acs2022")
counties.loc[counties["median_hh_income"] < 0, "median_hh_income"] = np.nan   # Census code -666666666 = not available
write_shp(counties.rename(columns=ACS_FIELDS), "us_counties_acs2022")
write_shp(gpd.read_file(SRC / "us_census_acs2022.gpkg", layer="us_counties_geometry"), "us_counties_geometry")
states = counties.dissolve(by="state_abbr", as_index=False,
                           aggfunc={"state_fips": "first", "state_name": "first", "population": "sum",
                                    "below_poverty": "sum", "poverty_universe": "sum", "land_km2": "sum"})
states["pov_pct"] = states["below_poverty"] / states["poverty_universe"] * 100
write_shp(states.rename(columns={"population": "pop", "below_poverty": "below_pov", "poverty_universe": "pov_univ"}),
          "us_states")

quakes = gpd.read_file(SRC / "us_census_acs2022.gpkg", layer="usgs_earthquakes_2025_m25")
quakes = quakes.to_crs(4269)
write_shp(quakes.rename(columns={"magType": "magtype"}), "usgs_earthquakes_2025_m25")
pd.DataFrame(
    [{"acs_field": k, "shapefile_field": v} for k, v in ACS_FIELDS.items()]
).to_csv(VEC / "us_counties_acs2022_field_dictionary.csv", index=False)

# ---------------------------------------------------------------- world countries (Natural Earth 110m)
ne = gpd.read_file(RAW / "ne110m" / "ne_110m_admin_0_countries.shp")
keep = ["NAME", "NAME_LONG", "ISO_A3", "ISO_A3_EH", "ADM0_A3", "CONTINENT", "REGION_UN", "SUBREGION",
        "POP_EST", "POP_YEAR", "GDP_MD", "GDP_YEAR", "INCOME_GRP", "ECONOMY", "geometry"]
write_shp(ne[keep], "world_countries_ne110m")

# HOLC "redlining" grades, Chicago, 1930s (Mapping Inequality, University of Richmond; slide 38)
holc = gpd.read_file(RAW / "mappinginequality.json")
holc = holc[holc["city"] == "Chicago"].copy()
holc["grade"] = holc["grade"].str.strip()                       # raw data has "A " / "C " next to "A" / "C"
write_shp(holc[["area_id", "grade", "label", "category", "fill", "geometry"]], "holc_chicago_1930s")

# ---------------------------------------------------------------- tables for joins / geocoding
shutil.copy(SRC / "acs2022_county_attributes.csv", TAB / "acs2022_county_attributes.csv")
shutil.copy(SRC / "acs2022_county_attributes.csvt", TAB / "acs2022_county_attributes.csvt")

wb = json.load(open(RAW / "wb_gdppc_2022.json"))[1]
gdp = pd.DataFrame([{"iso3": r["countryiso3code"], "country": r["country"]["value"],
                     "gdp_pc_usd": r["value"], "year": int(r["date"])} for r in wb])
gdp = gdp[gdp["iso3"].str.len() == 3]                            # aggregates keep 3-letter codes too (e.g. ARB): left in on purpose
gdp.to_csv(TAB / "worldbank_gdp_per_capita_2022.csv", index=False)
write_csvt(gdp, TAB / "worldbank_gdp_per_capita_2022.csv")

z = zipfile.ZipFile(RAW / "ndgain.zip")
gain = pd.read_csv(z.open("resources/gain/gain.csv"))[["ISO3", "Name", "2022"]]
vul = pd.read_csv(z.open("resources/vulnerability/vulnerability.csv"))[["ISO3", "2022"]]
rdy = pd.read_csv(z.open("resources/readiness/readiness.csv"))[["ISO3", "2022"]]
nd = (gain.rename(columns={"ISO3": "iso3", "Name": "country", "2022": "ndgain"})
      .merge(vul.rename(columns={"ISO3": "iso3", "2022": "vulnerab"}), on="iso3", how="left")
      .merge(rdy.rename(columns={"ISO3": "iso3", "2022": "readiness"}), on="iso3", how="left"))
nd.to_csv(TAB / "ndgain_climate_index_2022.csv", index=False)
write_csvt(nd, TAB / "ndgain_climate_index_2022.csv")

eq = pd.DataFrame({"id": quakes["id"], "longitude": quakes.geometry.x.round(5), "latitude": quakes.geometry.y.round(5),
                   "depth_km": quakes.geometry.z.round(2), "mag": quakes["mag"], "place": quakes["place"],
                   "time_utc": pd.to_datetime(quakes["time"], unit="ms").dt.strftime("%Y-%m-%d %H:%M:%S")})
eq.to_csv(TAB / "usgs_earthquakes_2025_m25_latlon.csv", index=False)
write_csvt(eq, TAB / "usgs_earthquakes_2025_m25_latlon.csv")

ged = pd.read_csv(zipfile.ZipFile(RAW / "ged241.zip").open("GEDEvent_v24_1.csv"), low_memory=False)
ged = ged[ged["year"] == 2023]
ged = ged[["id", "year", "type_of_violence", "conflict_name", "side_a", "side_b", "country", "region",
           "where_prec", "latitude", "longitude", "date_start", "best"]].rename(columns={"best": "deaths_best"})
ged["type_of_violence"] = ged["type_of_violence"].map({1: "state-based", 2: "non-state", 3: "one-sided"})
ged.to_csv(TAB / "ucdp_ged_events_2023.csv", index=False)
write_csvt(ged, TAB / "ucdp_ged_events_2023.csv")

# ---------------------------------------------------------------- other formats (slide 19)
il = counties[counties["state_fips"] == "17"].to_crs("OGC:CRS84")[["geoid", "county_name", "population", "poverty_pct", "geometry"]]
il.to_file(OTHER / "illinois_counties.geojson", driver="GeoJSON")
il.to_file(OTHER / "illinois_counties.kml", driver="KML")

for f in sorted(OUT.rglob("*")):
    if f.is_file():
        print(f"{f.relative_to(ROOT)}  {f.stat().st_size / 1e6:.2f} MB")
