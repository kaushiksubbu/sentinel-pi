"""
ai_summary.py — Daily operational report using Phi3/Ollama.
Reads: cron.log (last 24hrs) + gold_weather (today's metrics)
Writes: docs/daily_reports/Log_Summary_YYYY-MM-DD.md

Schedule: 08:30 daily via cron
"""

import os
import json
import requests
from datetime import datetime, timezone, timedelta
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common_func'))


from config import (
    GOLD_DB,
    LOG_FILE,
    REPORTS_DIR,
    OLLAMA_URL,
    OLLAMA_MODEL
)
from db_utils import connect_to_db_readonly

os.makedirs(REPORTS_DIR, exist_ok=True)


def read_recent_logs(hours: int = 24) -> str:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    lines = []
    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                lines.append(line.strip())
    except FileNotFoundError:
        return "No log file found."
    # Filter by timestamp prefix
    cutoff_str = cutoff.strftime('%Y-%m-%d %H')
    filtered = [line for line in lines if line[:13] >= cutoff_str]
    return "\n".join(filtered[-20:])


def read_gold_metrics() -> dict:
    """Read today's Gold layer metrics."""
    try:
        con = connect_to_db_readonly(GOLD_DB)

        metrics = con.execute("""
            SELECT
                COUNT(*)                                    AS total_rows,
                SUM(CASE WHEN is_valid THEN 1 ELSE 0 END)  AS valid_rows,
                MIN(window_start)                           AS earliest,
                MAX(window_start)                AS latest,
                COUNT(DISTINCT outdoor_location) AS outdoor_locations,
                COUNT(DISTINCT indoor_location)  AS indoor_locations
            FROM gold_weather
            WHERE window_start >= CURRENT_DATE
        """).fetchone()

        dq_flags = con.execute("""
            SELECT dq_flag, COUNT(*) as count
            FROM gold_weather
            WHERE window_start >= CURRENT_DATE
            AND dq_flag IS NOT NULL
            GROUP BY dq_flag
        """).fetchall()

        con.close()

        return {
            "total_rows": metrics[0],
            "valid_rows": metrics[1],
            "valid_pct": (
                round(metrics[1] / metrics[0] * 100, 1)
                if metrics[0] > 0 else 0
            ),
            "earliest_window": str(metrics[2]),
            "latest_window": str(metrics[3]),
            "outdoor_locations": metrics[4],
            "indoor_locations": metrics[5],
            "dq_flags": dq_flags,
        }
    except Exception as e:
        return {"error": str(e)}


def build_prompt(logs: str, metrics: dict) -> str:
    """Build Llama3.2:1b prompt from logs and metrics."""
    return f"""You are an AI assistant for Sentinel-Pi,
a governed IoT data lakehouse platform for home environment intelligence.
Your role is to generate a concise daily operations report
for the Technical Data Product Manager overseeing the platform.

Today's Gold layer metrics:
{json.dumps(metrics, indent=2, default=str)}

Recent pipeline logs:
{logs}

Write a concise daily operations report in markdown covering:
1. Pipeline Health — runs completed, failures, skipped runs
2. Data Quality — valid percentage, DQ flags observed
3. Performance — timing patterns, slowness
4. Sensor Coverage — locations reporting data
5. Anomalies — anything unusual worth investigating
6. Recommendation — one actionable suggestion for tomorrow

Keep the report under 400 words. Be specific about numbers.
Use markdown headers. Today's date: {datetime.now().strftime('%Y-%m-%d')}
"""


def call_llama3_2_1b(prompt: str) -> str:
    """Call llama3.2:1b via Ollama API."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=300,
        )
        response.raise_for_status()
        return response.json().get("response", "No response from Phi3.")
    except Exception as e:
        return f"Phi3 call failed: {str(e)}"


def save_report(content: str) -> str:
    """
    Save daily report to REPORTS_DIR.
    Output: REPORTS_DIR/Log_Summary_YYYY-MM-DD.md
    REPORTS_DIR defined in config.py
    """
    date_str = datetime.now().strftime('%Y-%m-%d')
    filepath = os.path.join(REPORTS_DIR, f"Log_Summary_{date_str}.md")
    with open(filepath, 'w') as f:
        f.write(f"# Sentinel-Pi Daily Report — {date_str}\n\n")
        f.write(content)
    return filepath


def main():
    print("Reading logs...")
    logs = read_recent_logs(hours=24)

    print("Reading Gold metrics...")
    metrics = read_gold_metrics()
    print(f"Metrics: {metrics}")

    print("Building prompt...")
    prompt = build_prompt(logs, metrics)

    print("Calling llama3.2:1b...")
    report = call_llama3_2_1b(prompt)

    print("Saving report...")
    filepath = save_report(report)
    print(f"Report saved: {filepath}")
    print("\n--- REPORT PREVIEW ---")
    print(report[:500])


if __name__ == "__main__":
    main()
