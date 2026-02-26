#!/bin/bash

LOG_FILE="/mnt/data/sentinel-pi/logs/cron.log"

echo "--- Generating Sentinel-Pi Daily Report ---"
echo "Date: $(date)"
echo "------------------------------------------"

# 1. Check if the log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "Error: Log file not found at $LOG_FILE"
    exit 1
fi

# 2. Extract the last 24 entries and pipe them to Phi-3
# We ask the AI to be concise to save RPi4 processing time
tail -n 48 "$LOG_FILE" | ollama run phi3 "
You are a weather data analyst. Review the following logs from a Raspberry Pi 4.
Identify:
1. The average temperature for the period.
2. Any DATA_QUALITY_ALERT issues (nulls or out-of-range).
3. A brief summary of the weather trend in the Netherlands (Almere/Schiphol area).
Be concise."

echo "------------------------------------------"
echo "Report Complete."

#  Keep live
tail -n 48 "$LOG_FILE" | ollama run phi3 --keepalive 10m "Summarize these logs..."
