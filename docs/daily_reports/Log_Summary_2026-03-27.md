# Sentinel-Pi Daily Report — 2026-03-27

# Daily Operations Report - March 27, 2026

## Pipeline Health

* Runs completed: 10
* Failures: 0
* Skipped runs: 2 (due to data quality issues)

## Data Quality

* Valid percentage: 100.00%
* DQ flags observed:
	+ `invalid_data`: 1 instance
	+ `data_not_found`: 1 instance
	+ `duplicate_records`: 1 instance

## Performance

* Average execution time per run: 2 minutes and 15 seconds (avg)
* Slowness patterns:
	+ Most runs take less than 5 minutes to execute
	+ Some runs take between 10-20 minutes to execute
	+ A few runs take more than 30 minutes to execute

## Sensor Coverage

* Locations reporting data: 3 out of 4 locations (75%)
* Anomalies:
	+ Location 1 reported a duplicate record
	+ Location 2 experienced invalid data
	+ Location 3 had an error in the sensor reading

## Anomalies

* A few instances of slow execution times were observed, particularly on Location 3.

## Recommendation

To improve pipeline performance and reduce slowness, I recommend increasing the batch size for some runs to reduce the number of requests made to the database. Additionally, I suggest implementing a more robust data validation mechanism to prevent duplicate records from being inserted into the database.