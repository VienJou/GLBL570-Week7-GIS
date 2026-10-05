# Workflow memo: High poverty is regionally clustered (Delta, Appalachia, border, reservations), not random

## Data
- us_counties_acs2022 (3144 counties, EPSG:4269), ACS 2018–2022 5-year; joined from CSV on GEOID = geoid (3144 rows, 0 unmatched)
- usgs_earthquakes_2025_m25 (3754 points, reprojected EPSG:4979 → 4269)
- Data fix: 1 county with median_hh_income = -666,666,666 set to No data

## Steps
1. Join CSV attributes (GEOID read as text; integer keys would drop 318 counties)
2. Classified poverty_pct: equal interval / quantile / natural breaks (breaks in §5.6)
3. Projected to EPSG:5070 (equal-area) with AK/HI insets
4. Final map: natural breaks [10.0, 14.4, 19.3, 26.4, 55.8]
5. Spatial join: earthquakes → counties (count/mean/max mag), per 10,000 km²
6. Global Moran's I for poverty_pct = 0.496 (pseudo p = 0.001)

## Design choice and why
- (write: e.g. natural breaks vs quantile; what changed on the map — 1804 counties change class)

## Ethical consideration
- (write: e.g. 20% vs 25% "high-poverty" threshold moves 335 counties; stigma of labelling places)

## AI suggestion captured
- (paste one suggestion from your AI map brief and whether you accepted it)

Sources: U.S. Census Bureau, 2018–2022 ACS 5-Year Estimates; U.S. Geological Survey Earthquake Catalog.
