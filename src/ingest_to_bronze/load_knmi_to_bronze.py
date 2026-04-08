# load_knmi_to_bronze.py

import os
import shutil
import logging
import xarray as xr
from datetime import datetime, timezone
from pathlib import Path
from db_utils import (
    connect_to_db,
    close_db,
    create_table_with_ddl,
    bulk_insert_ignore,
)
from config import BRONZE_DB, BRONZE_LANDING, PROCESSED_DIR, STATIONS
from openlineage_emitter import emit_lineage_event, get_run_id

from pipeline_logger import write_jsonl_entry
from metrics_contract import BronzeMetrics

import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', 'common_func'))

# ── Constants ──────────────────────────────────────────────────────
TABLE_NAME = "knmi_raw"
# ── Schema ─────────────────────────────────────────────────────────
# Explicit. No inference. Every column declared.
CREATE_KNMI_RAW = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        station_id    VARCHAR,
        observed_at   TIMESTAMP,
        -- Meteorological variables (all from .nc)
        D1H DOUBLE, Q1H DOUBLE, Q24H DOUBLE,
        R12H DOUBLE, R1H DOUBLE, R24H DOUBLE, R6H DOUBLE,
        Sav1H DOUBLE, Sax1H DOUBLE, Sax3H DOUBLE, Sax6H DOUBLE,
        Sx1H DOUBLE, Sx3H DOUBLE, Sx6H DOUBLE,
        Tb1n6 DOUBLE, Tb1x6 DOUBLE, Tb2n6 DOUBLE, Tb2x6 DOUBLE,
        Tgn12 DOUBLE, Tgn14 DOUBLE, Tgn6 DOUBLE,
        Tn12 DOUBLE, Tn14 DOUBLE, Tn6 DOUBLE,
        Tx12 DOUBLE, Tx24 DOUBLE, Tx6 DOUBLE,
        W10 DOUBLE, W10_10 DOUBLE,
        dd DOUBLE, dn DOUBLE, dr DOUBLE, dsd DOUBLE, dx DOUBLE,
        ff DOUBLE, ffs DOUBLE, fsd DOUBLE, fx DOUBLE, fxs DOUBLE,
        gff DOUBLE, gffs DOUBLE,
        h DOUBLE, h1 DOUBLE, h2 DOUBLE, h3 DOUBLE,
        hc DOUBLE, hc1 DOUBLE, hc2 DOUBLE, hc3 DOUBLE,
        n DOUBLE, n1 DOUBLE, n2 DOUBLE, n3 DOUBLE,
        nc DOUBLE, nc1 DOUBLE, nc2 DOUBLE, nc3 DOUBLE,
        nhc DOUBLE,
        p0 DOUBLE, pg DOUBLE, pp DOUBLE, pr DOUBLE, ps DOUBLE,
        pwc DOUBLE,
        qg DOUBLE, qgn DOUBLE, qgx DOUBLE, qnh DOUBLE,
        rg DOUBLE, rh DOUBLE,
        sq DOUBLE, ss DOUBLE,
        ta DOUBLE,
        tb DOUBLE, tb1 DOUBLE, tb2 DOUBLE, tb3 DOUBLE,
        tb4 DOUBLE, tb5 DOUBLE,
        td DOUBLE, tg DOUBLE, tgn DOUBLE, tn DOUBLE,
        tsd DOUBLE, tx DOUBLE,
        vv DOUBLE, ww DOUBLE, ww_10 DOUBLE,
        za DOUBLE, zm DOUBLE,
        -- Station metadata
        wsi VARCHAR, stationname VARCHAR,
        lat DOUBLE, lon DOUBLE, height DOUBLE,
        -- Governance columns
        source_file  VARCHAR,
        ingested_at  TIMESTAMP,
        PRIMARY KEY (station_id, observed_at)
    )
"""


# ── Helpers ────────────────────────────────────────────────────────
def get_unprocessed_files(landing_dir: str) -> list:
    """Returns all .nc files not yet in /processed."""
    return [
        str(f) for f in Path(landing_dir).glob("*.nc")
        if f.is_file()
    ]


def extract_all_variables(ds: xr.Dataset, station_id: str, source_file: str) -> dict:
    """
    Extracts ALL variables from .nc dataset for one station.
    No filtering. No cleaning. Bronze stores what arrived.
    observed_at converted to UTC — normalises against Zigbee CET.
    """
    # Time → UTC timestamp
    observed_at = ds.coords['time'].values[0]
    observed_at_utc = str(observed_at)  # xarray returns numpy datetime64

    def get(var):
        """Safely extract variable — returns None if missing."""
        try:
            val = ds[var].values[0]
            return float(val) if val is not None else None
        except Exception:
            return None

    return {
        "station_id": station_id,
        "observed_at": observed_at_utc,
        "D1H": get("D1H"), "Q1H": get("Q1H"), "Q24H": get("Q24H"),
        "R12H": get("R12H"), "R1H": get("R1H"), "R24H": get("R24H"),
        "R6H": get("R6H"), "Sav1H": get("Sav1H"), "Sax1H": get("Sax1H"),
        "Sax3H": get("Sax3H"), "Sax6H": get("Sax6H"),
        "Sx1H": get("Sx1H"), "Sx3H": get("Sx3H"), "Sx6H": get("Sx6H"),
        "Tb1n6": get("Tb1n6"), "Tb1x6": get("Tb1x6"),
        "Tb2n6": get("Tb2n6"), "Tb2x6": get("Tb2x6"),
        "Tgn12": get("Tgn12"), "Tgn14": get("Tgn14"), "Tgn6": get("Tgn6"),
        "Tn12": get("Tn12"), "Tn14": get("Tn14"), "Tn6": get("Tn6"),
        "Tx12": get("Tx12"), "Tx24": get("Tx24"), "Tx6": get("Tx6"),
        "W10": get("W10"), "W10_10": get("W10-10"),
        "dd": get("dd"), "dn": get("dn"), "dr": get("dr"),
        "dsd": get("dsd"), "dx": get("dx"),
        "ff": get("ff"), "ffs": get("ffs"), "fsd": get("fsd"),
        "fx": get("fx"), "fxs": get("fxs"),
        "gff": get("gff"), "gffs": get("gffs"),
        "h": get("h"), "h1": get("h1"), "h2": get("h2"), "h3": get("h3"),
        "hc": get("hc"), "hc1": get("hc1"), "hc2": get("hc2"), "hc3": get("hc3"),
        "n": get("n"), "n1": get("n1"), "n2": get("n2"), "n3": get("n3"),
        "nc": get("nc"), "nc1": get("nc1"), "nc2": get("nc2"), "nc3": get("nc3"),
        "nhc": get("nhc"),
        "p0": get("p0"), "pg": get("pg"), "pp": get("pp"),
        "pr": get("pr"), "ps": get("ps"), "pwc": get("pwc"),
        "qg": get("qg"), "qgn": get("qgn"), "qgx": get("qgx"), "qnh": get("qnh"),
        "rg": get("rg"), "rh": get("rh"),
        "sq": get("sq"), "ss": get("ss"),
        "ta": get("ta"),
        "tb": get("tb"), "tb1": get("tb1"), "tb2": get("tb2"),
        "tb3": get("tb3"), "tb4": get("tb4"), "tb5": get("tb5"),
        "td": get("td"), "tg": get("tg"), "tgn": get("tgn"),
        "tn": get("tn"), "tsd": get("tsd"), "tx": get("tx"),
        "vv": get("vv"), "ww": get("ww"), "ww_10": get("ww-10"),
        "za": get("za"), "zm": get("zm"),
        "wsi": str(ds["wsi"].values),
        "stationname": str(ds["stationname"].values),
        "lat": float(ds["lat"].values),
        "lon": float(ds["lon"].values),
        "height": float(ds["height"].values),
        "source_file": source_file,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }

# ── Main Load Function ─────────────────────────────────────────────


def load_knmi_files_to_bronze():
    """
    Reads ALL unprocessed .nc files.
    Bulk inserts ALL rows in one transaction.
    Moves files to /processed only after successful insert.
    Caller does NOT manage connection — self contained.
    Read pattern: each file opened and closed independently.
    Write pattern: single external connection for bulk insert.
    """
    start_time = datetime.now(timezone.utc)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    files = get_unprocessed_files(BRONZE_LANDING)
    run_id = get_run_id()          # added as a part of Openlineage

    if not files:
        logging.info("KNMI Bronze: No unprocessed files found.")
        return

    # ── Step 1: Build all rows first — no DB open yet ──
    rows = []
    files_to_move = []

    for file_path in files:
        try:
            ds = xr.open_dataset(file_path)
            for station_id in STATIONS:
                # Filter dataset to this station
                station_ds = ds.sel(station=station_id) \
                    if 'station' in ds.dims else ds
                row = extract_all_variables(
                    station_ds, station_id, os.path.basename(file_path)
                )
                rows.append(row)
            files_to_move.append(file_path)
            logging.info(f"KNMI Bronze: Extracted {file_path}")
        except Exception as e:
            logging.error(f"KNMI Bronze: Failed to extract {file_path} | {e}")
            # Skip this file — do not add to files_to_move
            continue

    if not rows:
        logging.warning("KNMI Bronze: No rows extracted.")
        return

    # ── Step 2: Single connection, bulk insert ──
    # Explicit external pattern for writes
    con = connect_to_db(BRONZE_DB)
    try:
        emit_lineage_event(
            job_name="load_knmi_files_to_bronze",
            run_id=run_id,
            state="START",
            inputs=["bronze.landing_zone"],
            outputs=["bronze.knmi_raw"]
        )

        create_table_with_ddl(con, CREATE_KNMI_RAW)
        # bulk load

        insert_log = bulk_insert_ignore(con, TABLE_NAME, rows)

        logging.info(
            f"KNMI Bronze | "
            f"Attempted: {insert_log['attempted']} | "
            f"Inserted: {insert_log['inserted']} | "
            f"Duplicates: {insert_log['duplicates']}"
        )

        # ── Step 3: Move files ONLY after successful insert ──
        for file_path in files_to_move:
            shutil.move(
                file_path,
                os.path.join(PROCESSED_DIR, os.path.basename(file_path))
            )
            logging.info(f"KNMI Bronze: Moved {file_path} → processed/")

        emit_lineage_event(
            job_name="load_knmi_files_to_bronze",
            run_id=run_id,
            state="COMPLETED",
            inputs=["bronze.landing_zone"],
            outputs=["bronze.knmi_raw"]
        )

        write_jsonl_entry(
            stage="load_knmi_bronze",
            status="success",
            start_time=start_time,
            metrics=BronzeMetrics(records_landed=len(rows))
        )

    except Exception as e:
        logging.error(f"KNMI Bronze: Bulk insert failed | {e}")
        emit_lineage_event(
            job_name="load_knmi_files_to_bronze",
            run_id=run_id,
            state="FAIL",
            inputs=["bronze.landing_zone"],
            outputs=["bronze.knmi_raw"]
        )
        # Files stay in landing zone — safe to retry next cron run
        write_jsonl_entry(
            stage="load_knmi_bronze",
            status="error",
            start_time=start_time,
            error=str(e)
        )
        raise
    finally:
        close_db(con)


if __name__ == "__main__":
    load_knmi_files_to_bronze()
