# Sentinel-Pi Daily Report — 2026-04-13

# Pipeline Health Report
## April 13, 2026

### Runs in this period:
There are 10 runs in this period.

### Stages with errors:
* Collect Zigbee (status=error)
* Transform Knmi Silver (status=error)

### Stages successful:
* Collect Zigbee (status=success)
* Transform Knmi Silver (status=success)
* Collect Zigbee (status=success)
* Transform Knmi Silver (status=success)
* Collect Zigbee (status=success)
* Transform Knmi Silver (status=success)
* Collect Zigbee (status=success)

### Data Quality
- Zigbee DQ pass rate: 100.0%
- KNMI DQ pass rate: 50.0%

### Performance
- Collect Zigbee duration: 2 hours, 30 minutes
- Any stage over 10 minutes: No

### Anomalies
- Gold rows vs expected (knmi_rows_in × zigbee_rows_in): 4.5% mismatch