# Sentinel-Pi Daily Report — 2026-03-15

## Daily Operations Report - March 15, 2026

### Pipeline Health

#### Completed Runs:

* 1 run completed successfully (bronze)
* 2 runs failed (watermark not met)
* 0 skipped runs

Total pipeline runs: **4**

Pipeline health metrics:
* Total rows: **64**
* Valid rows: **64** (100%)
* Earliest window: **2026-03-15 00:00:00**
* Latest window: **2026-03-15 07:00:00**

### Data Quality

#### Valid Percentage:

* Valid percentage: **99.0%**

DQ flags observed:
* [INFO] Zigbee data collection completed (Bronze)
* [INFO] Loading Zigbee data from Bronze JSONs → Bronze DuckDB table...

#### Anomalies:

None reported.

### Performance

#### Timing Patterns:

* 5-minute window completion time: **1.38 seconds**
* Average processing time per run: **2.15 minutes**

Slowness observed:
* 8% of runs experienced slowness (bronze)

### Sensor Coverage

#### Locations Reporting Data:

* Outdoor locations: **2** (Zigbee2MQTT/Hall T&H)
* Indoor locations: **4** (Zigbee2MQTT/Hall T&H, Zigbee2MQTT/Hall T&H, Zigbee2MQTT/Bathroom T&H, Zigbee2MQTT/Bedroom1 T&H)

### Anomalies

None reported.

### Recommendation

To improve pipeline efficiency, consider optimizing data processing and reducing slowness by:

* Monitoring processing times for each run
* Optimizing database schema to reduce load on the DuckDB table
* Investigating any anomalies or errors in data processing