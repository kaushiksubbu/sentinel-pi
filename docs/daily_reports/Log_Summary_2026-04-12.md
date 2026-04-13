# Sentinel-Pi Daily Report — 2026-04-12

# Pipeline Health Report
## April 12, 2026

### Runs in this period:
There are no runs mentioned in the JSONL data.

### Stages with errors:
* None

### Stages successful:
* Collect Zigbee (start_time: 2026-04-11 00:00:00, end_time: 2026-04-12 06:00:00)
* Transform Knmi (start_time: 2026-04-11 00:00:00, end_time: 2026-04-12 10:00:00)

### Data Quality
* Zigbee DQ pass rate: 100.0%
* KNMI DQ pass rate: 80.0%

### Performance
* Collect Zigbee duration: 120 minutes (from JSONL)
* Any stage over 10 minutes: False

### Anomalies
* Gold rows vs expected (knmi_rows_in × zigbee_rows_in): 56 rows (expected: 56)