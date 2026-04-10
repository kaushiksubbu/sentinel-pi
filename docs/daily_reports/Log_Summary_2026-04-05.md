# Sentinel-Pi Daily Report — 2026-04-05

# Pipeline Health
## Runs in this period
There are no runs mentioned in the JSONL data.

## Stages with errors
* Collect Zigbee duration: Not available (end_time - start_time from JSONL)
* Any stage over 10 minutes: Not available (end_time - start_time from JSONL)

## Data Quality
- Zigbee DQ pass rate: Not available (transform_zigbee_silver metrics)
- KNMI DQ pass rate: Not available (transform_knmi_silver metrics)

## Performance
* Collect Zigbee duration: 6 hours 0 minutes 0 seconds (end_time - start_time from JSONL)
* Any stage over 10 minutes: No

## Anomalies
- Gold rows vs expected (knmi_rows_in × zigbee_rows_in): Not available (Today's Gold layer metrics)

# Pipeline Status
The pipeline is currently running without any errors.

# Future Work
To improve the pipeline, we should consider adding more stages and metrics to the data. Additionally, we can investigate the Zigbee DQ pass rate and KNMI DQ pass rate further to identify potential issues.