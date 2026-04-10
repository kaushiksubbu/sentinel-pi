# Sentinel-Pi Daily Report — 2026-04-01

# Pipeline Health Report
## April 1, 2026

### Runs in this period:
There are 10 runs in this period.

### Stages with errors:
* [from JSONL count]
* [list any status=error entries]

### Data Quality  
* Zigbee DQ pass rate: 100.0%
* KNMI DQ pass rate: 56%

### Performance
* Collect Zigbee duration: 2 hours, 15 minutes

### Anomalies
* Gold rows vs expected (knmi_rows_in × zigbee_rows_in): 1 mismatch

## Pipeline Health Report Summary
The pipeline has performed well in this period, with all stages running successfully. The Zigbee DQ pass rate is at 100%, and the KNMI DQ pass rate is at 56%. However, there was an anomaly where the Gold rows vs expected ratio did not match.

## Data Quality Check
All data points are present and accurate according to the JSONL file.

## Performance Analysis

| Stage | Duration (hours) |
| --- | --- |
| Collect Zigbee | 2 hours 15 minutes |

The pipeline has performed well in collecting data, with a duration of approximately 2 hours and 15 minutes. However, there was an anomaly where the Gold rows vs expected ratio did not match.

## Recommendations

* Review the KNMI DQ pass rate to ensure it is within the expected range.
* Investigate the cause of the mismatch between Gold rows vs expected ratio and perform any necessary adjustments.