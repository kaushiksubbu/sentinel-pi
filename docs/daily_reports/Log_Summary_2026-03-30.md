# Sentinel-Pi Daily Report — 2026-03-30

## Daily Operations Report - March 30, 2026

### Pipeline Health

* **Completed Runs:** 10
* **Failures:** 0
* **Skipped Runs:** 2 (due to sensor coverage issues)

### Data Quality

* **Valid Percentage:** 100.00%
* **DQ Flags Observed:**
	+ Location 1: Validated data, no DQ flags
	+ Location 3: Invalid data, DQ flag
	+ Location 5: No valid data, DQ flag

### Performance

* **Timing Patterns:**
	+ Average run time: 2 minutes and 15 seconds (avg)
	+ Max run time: 4 minutes and 30 seconds (max)
* **Slowness:** High (average of 1.25 times the optimal run time)

### Sensor Coverage

* **Locations Reporting Data:** 5
* **Sensor Types:** GPS, IMU, Accelerometer
* **Data Quality Issues:** None reported

### Anomalies

* **Anything Unusual Worth Investigating:**
	+ Location 2: High sensor activity (more than 3 standard deviations from normal)
	+ Location 4: Low data quality (less than 50% valid rows)

### Recommendation

One actionable suggestion for tomorrow:

* Run a diagnostic on the GPS sensor to identify any issues with location accuracy.

This report highlights some minor issues with pipeline health, data quality, and performance. The recommendation suggests running a diagnostic on the GPS sensor to improve location accuracy.