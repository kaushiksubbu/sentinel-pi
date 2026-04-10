# Sentinel-Pi Daily Report — 2026-04-10

# Pipeline Health Report
## April 10, 2026

### Runs in this period:
* 5 runs

### Stages with errors:
* None

### Stages successful:
* 4 runs ( transform_zigbee_silver, transform_knmi_silver, collect_zigbee, collect_knmi )

### Data Quality
- Zigbee DQ pass rate: 100.0%
- KNMI DQ pass rate: not available

### Performance
- Collect Zigbee duration: 6 hours 30 minutes (from JSONL)
- Any stage over 10 minutes: None

### Anomalies
- Gold rows vs expected (knmi_rows_in × zigbee_rows_in): 2/56 = 0.36% mismatch