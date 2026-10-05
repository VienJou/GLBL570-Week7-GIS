# 美国 Census GIS 课堂数据包

这套数据针对 `GLBL570_Week7_v3.pptx` 的 QGIS 实验设计，可完成属性表、表连接、分级设色、分类方法比较、归一化、投影比较、统计饼图、空间连接和地图导出。

## 文件

- `us_census_acs2022.gpkg`：QGIS 主文件，包含三个图层。
  - `us_counties_geometry`：美国 50 州和华盛顿特区的县级边界，仅含几何与标识字段，供练习表连接。
  - `us_counties_acs2022`：已经连接 ACS 属性的县级图层，供分级设色、饼图和空间分析使用。
  - `usgs_earthquakes_2025_m25`：2025 年发生在上述县界内、震级不低于 2.5 的 USGS 地震点。
- `acs2022_county_attributes.csv`：县级 ACS 属性表，使用 `geoid` 与几何图层的 `GEOID` 连接。
- `acs2022_county_attributes.csvt`：字段类型说明。必须与 CSV 放在同一目录，避免 GEOID 的前导零丢失。

GeoPackage 的县图层坐标参考系是 NAD83（EPSG:4269）。地震点原始坐标系是 WGS 84 三维坐标（EPSG:4979）。QGIS 可自动进行动态投影。

## 建议的 60 分钟课堂流程

### 0–10 分钟：加载数据与属性表

1. 将 `us_census_acs2022.gpkg` 拖入 QGIS。
2. 先添加 `us_counties_geometry`，打开属性表，说明一行对应一个县级空间单元。
3. 再把 `acs2022_county_attributes.csv` 作为分隔文本表添加。选择“无几何”。
4. 在县界图层属性的“连接”页，以 `GEOID = geoid` 连接 CSV。
5. 与已经连接好的 `us_counties_acs2022` 对照，检查是否得到 3,144 条记录。

### 10–25 分钟：量化数据与分类方法

建议使用 `poverty_pct` 或 `median_hh_income`：

1. 图层属性 → 符号系统 → 分级。
2. 设为 5 类，依次尝试 Equal Interval、Quantile、Natural Breaks (Jenks)。
3. 每次记录分类断点，并比较哪些县改变了颜色。
4. 再比较 `population` 与 `pop_density_km2`，讨论总量和归一化指标如何讲出不同故事。
5. 色带使用顺序色带；缺失值应单独显示，不要与最低值混为一类。

课堂讨论可直接对应课件中的问题：分类断点改变时，地图的信息与政策含义如何改变？

### 25–35 分钟：投影比较

1. 比较 EPSG:4269、EPSG:3857 和 EPSG:5070。
2. EPSG:3857 适合网络地图显示，但不是美国统计制图的等积选择。
3. EPSG:5070 是 NAD83 / Conus Albers；先过滤美国本土 48 州，再用于面积型专题图与空间分析。
4. 保留阿拉斯加和夏威夷时，观察它们的位置与尺度如何影响版面；可在打印布局中制作插图。
5. 在 <https://projectionwizard.org/> 选择美国范围，并比较 Equal-area、Conformal 和 Equidistant 的推荐结果。

### 35–45 分钟：添加统计饼图

打开 `us_counties_acs2022` 的“图表/Diagrams”页，选择 Pie chart。

方案 A：种族构成

- `race_white`
- `race_black`
- `race_aian`
- `race_asian`
- `race_nhpi`
- `race_other`
- `race_two_plus`

方案 B：通勤方式

- `commute_drive_alone`
- `commute_carpool`
- `commute_transit`
- `commute_bicycle`
- `commute_walk`
- `commute_other`
- `commute_wfh`

先过滤一个州，例如 Illinois (`state_fips = '17'`)，避免 3,144 个饼图互相遮挡。大小可按 `population` 或 `commuters_total` 缩放，并设置比例尺可见范围。

### 45–60 分钟：空间统计与制图

1. 添加 `usgs_earthquakes_2025_m25`。
2. 打开 Processing Toolbox，运行“Join attributes by location (summary)”。
3. 输入图层选择县，连接图层选择地震点，空间关系选择 intersects。
4. 对 `mag` 计算 count、mean 和 max。
5. 对地震数量制作分级设色图；再计算每 10,000 平方公里事件数，比较总量与面积标准化结果。
6. 讨论 Alaska、西部山区及构造带形成的空间聚集，以及只选 2025 年与震级阈值带来的选择偏差。

如需进一步分析，可对过滤后的美国本土县使用邻接权重，对 `poverty_pct` 计算 Global Moran's I 或 Local Moran/LISA。不同 QGIS 安装提供的统计工具可能不同，GeoDa 也可直接读取本 GeoPackage。

## 字段字典

### 标识与几何

- `geoid`：五位县级 GEOID，是推荐的连接键。
- `state_fips`：两位州 FIPS 代码。
- `state_abbr`、`state_name`：州邮政缩写与州名。
- `county_fips`：三位县 FIPS 代码。
- `county_name`、`county_label`：县名及完整行政名称。
- `land_km2`、`water_km2`：陆地和水域面积，平方公里。

### 专题制图字段

- `population`：总人口，ACS B02001。
- `pop_density_km2`：每平方公里人口，由人口除以陆地面积得到。
- `median_hh_income`：家庭收入中位数，2022 年经通胀调整的美元，ACS B19013。
- `poverty_universe`：确定贫困状态的人口基数，ACS B17001。
- `below_poverty`：低于贫困线的人口。
- `poverty_pct`：低于贫困线人口百分比。

### 饼图字段

- `race_*`：B02001 的互斥种族分类；所有分项之和等于 `population`。
- `commute_*`：B08301 的互斥主要通勤方式；所有分项之和等于 `commuters_total`。
- `transit_pct`：公共交通通勤比例。
- `wfh_pct`：居家工作比例。

### 地震字段

- `mag`：震级。
- `place`：USGS 对位置的文字描述。
- `time`、`updated`：Unix 时间戳，单位为毫秒。
- `felt`：公众报告有震感的数量。
- `mmi`：修订麦加利烈度。
- `sig`：USGS 事件显著性评分。
- `gap`、`rms`、`dmin`、`nst`：定位和观测质量相关字段。

## 数据范围与注意事项

- ACS 是调查估计，不是逐户普查计数。本精简教学包未保留 margin of error；正式研究应回到 Census 原表下载误差字段。
- 县级单元包括 Census 定义的 county equivalents。2022 年数据反映当年的地理体系。
- 县界采用 Census 1:5,000,000 制图边界，适合全国专题图和课堂空间连接，不用于精确面积、地籍或工程分析；面积字段来自详细 TIGER 数据，而不是由简化几何重新计算。
- 地震点按 2025-01-01 至 2026-01-01、震级至少 2.5 查询，并空间裁切到包内县界；它适合练习，不代表长期地震风险。
- `commute_other` 合并了出租车、摩托车及其他方式，使通勤饼图的分项能够加总到总体。
- 不要把饼图面积直接当作百分比；图例、大小字段和分类方法都应写进地图说明。

## 来源与引用

- U.S. Census Bureau, 2022 TIGER/Line with Selected Demographic and Economic Data, county geodatabase; 2018–2022 ACS 5-year estimates.
- U.S. Geological Survey, FDSN Earthquake Catalog, 2025 events with magnitude ≥ 2.5.
- 推荐在地图来源行写：`Sources: U.S. Census Bureau, 2018–2022 ACS 5-Year Estimates; U.S. Geological Survey Earthquake Catalog.`
