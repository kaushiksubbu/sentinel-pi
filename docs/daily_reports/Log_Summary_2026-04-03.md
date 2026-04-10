# Sentinel-Pi Daily Report — 2026-04-03

## Pipeline Health
### Runs in this period:
There are 10 runs in this period.

### Stages with errors:
* `transform_zigbee_silver` (4 runs) - status "error"
* `collect_zigbee` (2 runs) - status "error"

### Stages successful:
* `transform_knmi_silver` (6 runs) - status "success"
* `transform_gold` (3 runs) - status "success"
* `collect_zigbee` (1 run) - status "success"

## Data Quality
- Zigbee DQ pass rate: 100.0%
- KNMI DQ pass rate: 100.0%

## Performance
### Collect Zigbee duration:
The collect zigbee stage took a total of 2 hours and 30 minutes.

### Any stage over 10 minutes:
There are no stages that exceeded 10 minutes in this period.

## Anomalies
- Gold rows vs expected (knmi_rows_in × zigbee_rows_in): 56.0% vs 56.0%

Note: The "not available" metric is used for metrics not present in the data, such as `transform_gold` and its stages.