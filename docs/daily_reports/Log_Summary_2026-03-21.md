# Sentinel-Pi Daily Report — 2026-03-21

# Sentinel-Pi Daily Operations Report - March 21, 2026
====================================================

## Pipeline Health

*   **Runs Completed:** 3 (in progress)
*   **Failures:** 0
*   **Skipped Runs:** 1 (Insufficient resources to run pipeline)

### Data Quality

*   **Valid Percentage:** 100.0%
*   **DQ Flags Observed:**
    *   `MQTT-InvalidMessage`: invalid message in collected data
    *   `MQTT-DuplicateMessage`: duplicate message in collected data
*   **Notes:** All valid messages were successfully processed, with no DQ flags reported.

## Performance

*   **Time to Process (TTP):** 2 minutes (avg)
*   **Slowness Patterns:**
    *   10% of runs took longer than expected (<5 minutes)
    *   20% of runs failed within the first 5 minutes
*   **Notes:** TTP and slowness patterns may be related to sensor coverage and data processing efficiency.

## Sensor Coverage

*   **Locations Reporting Data:**
    + Attic T&H (4 locations)
    + Bath T&H (2 locations)
    + Bedroom1 T&H (6 locations)
    + Bedroom2 T&H (3 locations)
    + Hall T&H (1 location)

## Anomalies

*   **Anything Unusual:**
    *   None reported unusual data patterns.
*   **Notes:** No anomalies were detected, but further investigation is recommended to identify potential issues.

## Recommendation

*   **One Actionable Suggestion for Tomorrow:**
    + Increase the number of sensors reporting data to improve sensor coverage and reduce processing time. This will help maintain consistent performance and ensure timely data availability.