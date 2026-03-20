# Sentinel-Pi Daily Report — 2026-03-20

## Daily Operations Report - March 20, 2026

### Pipeline Health

| Run ID | Status |
| --- | --- |
| Bedroom1 T&H | Completed |
| Bedroom2 T&H | Completed |
| Attic T&H | Completed |

**Failures:** None
**Skipped Runs:** None
**Total Runs:** 3 (Bedroom1, Bedroom2, Attic)

### Data Quality

| Metric | Value |
| --- | --- |
| Valid Percentage | 100.0% |
| DQ Flags | [] |

No data quality issues were reported.

### Performance

| Interval | Time |
| --- | --- |
| 5-minute window | 60ms (90%) |
| 10-minute window | 130ms (67%) |
| 15-minute window | 190ms (93%) |

The platform's performance is generally good, with a small increase in latency between intervals.

### Sensor Coverage

There are 5 locations reporting data:

| Location | Message Sent |
| --- | --- |
| Bedroom1 | |
| Bedroom2 | |
| Attic | |
| Hall | |
| Bath | |

No unusual sensor activity was reported.

### Anomalies

None worth investigating were observed.

### Recommendation

For tomorrow, I recommend sending a message to Bedroom3 for 5-minute window data. Consider implementing a queue-based architecture to reduce latency.

This report provides an overview of the pipeline's health, data quality, performance, and sensor coverage. While there are no issues reported, it is essential to continue monitoring and optimizing the platform to ensure optimal performance and reliability.