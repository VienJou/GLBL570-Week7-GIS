"""Download the lab rasters from Google Earth Engine into lab_data/raster/ (GeoTIFF, EPSG:5070).

  illinois_dem_srtm_150m.tif        SRTM elevation (m), int16            -> stretch / classify renderers
  illinois_landcover_nlcd2021_150m.tif  NLCD 2021 classes, uint8 + colour table -> unique-values renderer, VAT
  champaign_sentinel2_2023_10m.tif  Sentinel-2 L2A summer median, bands R,G,B,NIR (reflectance x 10000) -> RGB renderer
  illinois_worldpop_2020_1km.tif    WorldPop 2020 people per 1 km cell, float32 -> zonal statistics by county

Needs an Earth Engine service-account key: set GEE_KEY (path to JSON) and GEE_PROJECT.
Run from the repository root:  python scripts/fetch_rasters_gee.py
"""
import csv
import io
import os
from pathlib import Path

import ee
import geopandas as gpd
import numpy as np
import rasterio
import requests
from google.oauth2 import service_account
from rasterio.features import geometry_mask

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "lab_data" / "raster"
OUT.mkdir(parents=True, exist_ok=True)
CRS = "EPSG:5070"

key = os.environ["GEE_KEY"]                                  # path to your service-account JSON (never commit it)
cred = service_account.Credentials.from_service_account_file(key, scopes=["https://www.googleapis.com/auth/earthengine"])
ee.Initialize(cred, project=os.environ["GEE_PROJECT"])

states = gpd.read_file(ROOT / "lab_data" / "vector" / "us_states.shp").to_crs(CRS)
illinois = states.loc[states["state_abbr"] == "IL", "geometry"].iloc[0]
CHAMPAIGN_BBOX = (-88.36, 40.04, -88.12, 40.17)                 # Champaign-Urbana, lon/lat


def grid(bounds, res):
    xmin, ymin, xmax, ymax = (np.floor(bounds[0] / res) * res, np.floor(bounds[1] / res) * res,
                              np.ceil(bounds[2] / res) * res, np.ceil(bounds[3] / res) * res)
    w, h = int((xmax - xmin) / res), int((ymax - ymin) / res)
    return [float(res), 0.0, float(xmin), 0.0, -float(res), float(ymax)], w, h


def download(img, bounds, res, name, dtype, nodata, clip_geom=None, colormap=None, descriptions=None):
    transform, w, h = grid(bounds, res)
    url = img.getDownloadURL({"crs": CRS, "crs_transform": transform, "dimensions": f"{w}x{h}",
                              "format": "GEO_TIFF"})
    r = requests.get(url, timeout=600)
    if not r.ok:
        raise RuntimeError(f"{name}: HTTP {r.status_code}: {r.text[:500]}")
    with rasterio.open(io.BytesIO(r.content)) as src:
        data, profile = src.read().astype(dtype), src.profile
    if clip_geom is not None:                                   # outside the state = nodata, not 0
        outside = geometry_mask([clip_geom], out_shape=(h, w), transform=profile["transform"])
        data[:, outside] = nodata
    profile.update(driver="GTiff", dtype=dtype, nodata=nodata, compress="deflate", predictor=2 if dtype != "uint8" else 1,
                   tiled=True, blockxsize=256, blockysize=256, count=data.shape[0])
    path = OUT / name
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(data)
        if colormap:
            dst.write_colormap(1, colormap)
        for i, d in enumerate(descriptions or [], start=1):
            dst.set_band_description(i, d)
        dst.build_overviews([2, 4, 8, 16], rasterio.enums.Resampling.nearest if colormap else rasterio.enums.Resampling.average)
    print(f"{name}: {w}x{h}x{data.shape[0]} {dtype}  {path.stat().st_size / 1e6:.1f} MB")


il_bounds = illinois.bounds
ONLY = set(filter(None, os.environ.get("ONLY", "").split(",")))   # e.g. ONLY=worldpop to refetch one layer


def want(layer):
    return not ONLY or layer in ONLY


# 1. SRTM elevation (30 m) resampled bilinearly to 150 m (reduceResolution over all of Illinois exceeds EE limits)
dem = ee.Image("USGS/SRTMGL1_003").select("elevation").resample("bilinear")
if want("dem"):
    download(dem.unmask(-32768).toInt16(), il_bounds, 150, "illinois_dem_srtm_150m.tif", "int16", -32768,
             clip_geom=illinois, descriptions=["elevation_m"])

# 2. NLCD 2021 land cover (30 m) -> 150 m, with the official colour table
nlcd_col = ee.ImageCollection("USGS/NLCD_RELEASES/2021_REL/NLCD")
nlcd = nlcd_col.filter(ee.Filter.eq("system:index", "2021")).first().select("landcover")
info = nlcd.getInfo()["properties"]
values, palette = info["landcover_class_values"], info["landcover_class_palette"]
cmap = {int(v): tuple(int(p[i:i + 2], 16) for i in (0, 2, 4)) + (255,) for v, p in zip(values, palette)}
cmap[0] = (0, 0, 0, 0)
if want("nlcd"):
    # Nearest-neighbour sampling of the 30 m classes; majority (mode) aggregation over all of Illinois exceeds EE limits.
    download(nlcd.unmask(0).toUint8(), il_bounds, 150, "illinois_landcover_nlcd2021_150m.tif", "uint8", 0,
             clip_geom=illinois, colormap=cmap, descriptions=["nlcd_class"])
with open(OUT / "nlcd_classes.csv", "w", newline="") as fh:              # value attribute table (labels contain commas)
    csv.writer(fh).writerows([("value", "label")] + [(v, n.split(":")[0].strip()) for v, n in zip(values, info["landcover_class_names"])])

# 3. Sentinel-2 L2A median composite, Jun-Sep 2023, 10 m, bands R G B NIR
aoi = ee.Geometry.Rectangle(list(CHAMPAIGN_BBOX))
s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(aoi).filterDate("2023-06-01", "2023-09-30")
      .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20)).median().select(["B4", "B3", "B2", "B8"]))
champ_bounds = gpd.GeoSeries.from_xy([CHAMPAIGN_BBOX[0], CHAMPAIGN_BBOX[2]], [CHAMPAIGN_BBOX[1], CHAMPAIGN_BBOX[3]],
                                     crs=4326).to_crs(CRS).total_bounds
if want("s2"):
    download(s2.toUint16(), champ_bounds, 10, "champaign_sentinel2_2023_10m.tif", "uint16", 0,
             descriptions=["B4_red", "B3_green", "B2_blue", "B8_nir"])

# 4. WorldPop 2020 (people per ~100 m cell): download on its native lon/lat grid in tiles, then aggregate to 1 km
#    locally with GDAL's "sum" resampling, which preserves the total (EE reduceResolution did not, in our tests).
def fetch_worldpop_1km(name="illinois_worldpop_2020_1km.tif", res=1000, tile=2000):
    from rasterio.warp import Resampling, reproject
    wp = (ee.ImageCollection("WorldPop/GP/100m/pop").filter(ee.Filter.eq("country", "USA"))
          .filter(ee.Filter.eq("year", 2020)).first())
    proj = wp.projection().getInfo()
    sx, _, x0, _, sy, y0 = proj["transform"]                     # native: ~0.000833 deg, EPSG:4326
    lon0, lat0, lon1, lat1 = gpd.GeoSeries([illinois], crs=CRS).to_crs(4326).total_bounds
    c0, c1 = int(np.floor((lon0 - x0) / sx)) - 2, int(np.ceil((lon1 - x0) / sx)) + 2
    r0, r1 = int(np.floor((lat1 - y0) / sy)) - 2, int(np.ceil((lat0 - y0) / sy)) + 2
    mosaic = np.zeros((r1 - r0, c1 - c0), "float32")          # tiles placed by offset; masked (-inf) -> 0
    for r in range(r0, r1, tile):
        for c in range(c0, c1, tile):
            w, h = min(tile, c1 - c), min(tile, r1 - r)
            url = wp.unmask(0).toFloat().getDownloadURL({"crs": proj["crs"], "dimensions": f"{w}x{h}", "format": "GEO_TIFF",
                                                        "crs_transform": [sx, 0, x0 + c * sx, 0, sy, y0 + r * sy]})
            resp = requests.get(url, timeout=600)
            if not resp.ok:
                raise RuntimeError(f"worldpop tile: HTTP {resp.status_code}: {resp.text[:300]}")
            a = rasterio.open(io.BytesIO(resp.content)).read(1)
            mosaic[r - r0:r - r0 + h, c - c0:c - c0 + w] = np.where(np.isfinite(a) & (a > 0), a, 0)
    mtrans = rasterio.Affine(sx, 0, x0 + c0 * sx, 0, sy, y0 + r0 * sy)
    native_total = float(mosaic.sum())
    transform, w, h = grid(illinois.bounds, res)
    dst = np.zeros((h, w), "float32")
    reproject(mosaic, dst, src_transform=mtrans, src_crs=proj["crs"], dst_transform=rasterio.Affine(*transform[:6]),
              dst_crs=CRS, resampling=Resampling.sum)
    outside = geometry_mask([illinois], out_shape=(h, w), transform=rasterio.Affine(*transform[:6]))
    dst[outside] = -1.0
    profile = dict(driver="GTiff", width=w, height=h, count=1, dtype="float32", crs=CRS, nodata=-1.0,
                   transform=rasterio.Affine(*transform[:6]), compress="deflate", predictor=2)
    with rasterio.open(OUT / name, "w", **profile) as out:
        out.write(dst, 1)
        out.set_band_description(1, "population_2020")
    print(f"{name}: {w}x{h} float32  bbox total {native_total:,.0f} (native grid)  {dst[dst >= 0].sum():,.0f} inside Illinois")


if want("worldpop"):
    fetch_worldpop_1km()
