# Sentinel-Pi Daily Report — 2026-04-08

# Pipeline Health Report
## April 8, 2026

### Runs in this period:
There were 10 runs in this period.

### Stages with errors:
* `electronic-partridge` (collect_zigbee) - error
* `spiffy-centipede` (collect_knmi) - error
* `steadfast-skunk` (collect_zigbee, collect_knmi, transform_gold) - error

### Stages successful:
* `electronic-partridge` (collect_zigbee)
* `opal-cormorant` (collect_zigbee)
* `clay-dolphin` (collect_zigbee)

## Data Quality
- Zigbee DQ pass rate: 100.0%
- KNMI DQ pass rate: not available

## Performance
- Collect Zigbee duration: 2 hours, 15 minutes
- Any stage over 10 minutes: yes

## Anomalies
- Gold rows vs expected (knmi_rows_in × zigbee_rows_in): 8/56 = 14.29% mismatch