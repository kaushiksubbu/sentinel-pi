# Sentinel-Pi Daily Report — 2026-03-17

## **Daily Operations Report - March 17, 2026**
=====================================================

### Pipeline Health
-------------------

*   Runs completed: **5** (no failures or skips)
*   Run times:
    *   Zigbee data collection: **4.15 minutes** (avg.)
    *   Loading data into database: **1 minute**
*   Pipeline health score: **95%**

### Data Quality
----------------

*   Valid percentage: **100%**
*   DQ flags observed: 
    *   0% invalid messages in "z zigbee2mqtt_Hall_T&H_2026031723.json"
    *   1% invalid message in "zigbee_zigbee2mqtt_Bedroom1_T&H_2026031723.json"

### Performance
----------------

*   Average run time: **4.33 minutes**
*   Median run time: **2.78 minutes**

### Sensor Coverage
---------------------

*   Outdoor locations reporting data: **2** (Attic, Bedroom 1)
*   Indoor locations reporting data: **4** (Attic, Bedroom 2, Bathroom)

### Anomalies
--------------

*   None observed in this run

### Recommendation
-------------------

*   One actionable suggestion for tomorrow:
    + Monitor the "z zigbee2mqtt_Hall_T&H_2026031723.json" file for any changes or invalid messages.

## **Additional Observations**
-----------------------------

-   The current DQ score is within a reasonable range, but there are some minor issues in the data quality report.
-   The average run time of 4.33 minutes suggests that the pipeline is running smoothly, with most runs taking less than 5 minutes to complete.
-   The sensor coverage analysis indicates that outdoor and indoor locations are being reported by Zigbee devices.