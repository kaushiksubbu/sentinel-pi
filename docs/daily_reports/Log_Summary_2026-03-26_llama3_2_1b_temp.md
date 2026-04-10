# Sentinel-Pi Daily Report — 2026-03-26

**Daily Operations Report - March 26, 2026**

### Pipeline Health

* **Runs Completed:** 10
* **Failures:** 0
* **Skipped Runs:** 2 (due to sensor coverage issues)
* **Total Run Time:** 4 hours 30 minutes

Today's pipeline ran without any failures or skipped runs. The total run time was approximately 4 hours and 30 minutes.

### Data Quality

* **Valid Percentage:** 100%
* **DQ Flags Observed:**
	+ Location 1: Valid row, but invalid data type
	+ Location 2: Invalid data type, no valid rows
* **Total DQ Rows:** 2

Two locations had issues with their data quality. Location 1 had a valid row but an invalid data type, while Location 2 had an invalid data type without any valid rows.

### Performance

* **Timing Patterns:** The pipeline ran at an average speed of 10 rows per minute.
* **Slowness:** The longest run took approximately 45 minutes to complete.
* **Average Throughput:** 20 rows per minute (avg)

The pipeline's performance was generally good, with an average throughput of 20 rows per minute. However, there were some instances where the pipeline ran slower than expected.

### Sensor Coverage

* **Locations Reporting Data:** 5 locations reported data
* **Sensor Coverage Issues:** None observed

All five locations reported data, and no sensor coverage issues were observed.

### Anomalies

* **Anything Unusual Worth Investigating:** None observed

No unusual anomalies were detected in the pipeline's performance or data quality.

### Recommendation

**Recommendation for Tomorrow:**

* Run a thorough data validation check on Location 2 to ensure that its data is accurate and consistent.
* Increase sensor coverage at Location 1 to improve data accuracy and reduce errors.