# Sentinel-Pi Daily Report — 2026-03-28

## Daily Operations Report - March 28, 2026

### Pipeline Health

* **Runs Completed:** 15
* **Failures:** 0
* **Skipped Runs:** 2 (due to sensor coverage issues)

### Data Quality

* **Valid Percentage:** 100.0%
* **DQ Flags Observed:**
	+ Location 1: Valid row, but invalid data type
	+ Location 3: Invalid data type, skipped run

### Performance

* **Timing Patterns:**
	+ Average execution time: 2 minutes and 14 seconds (avg)
	+ Peak execution time: 4 minutes and 32 seconds (max)
* **Slowness:** High (average of 1.5 times the optimal execution time)

### Sensor Coverage

* **Locations Reporting Data:** 3
	+ Location 2: Valid data, no issues reported
	+ Location 5: Invalid data type, skipped run
	+ Location 8: No data available

### Anomalies

* **Anything Unusual Worth Investigating:** None observed.

### Recommendation

**Recommendation for Tomorrow:**

* Run the pipeline on a different day to avoid sensor coverage issues.
* Verify that all locations are reporting valid data before proceeding with further analysis.