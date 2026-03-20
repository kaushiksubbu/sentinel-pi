#create_silver_tables.py
from db_utils import connect_to_db, close_db, create_table_with_ddl
import logging
from config import SILVER_DB, GOLD_DB
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common_func'))

CREATE_WEATHER_SILVER = """
    CREATE TABLE IF NOT EXISTS weather_silver (
        observed_at      TIMESTAMP,
        location         VARCHAR,
        data_provider    VARCHAR,
        temp             DOUBLE,
        humidity         DOUBLE,
        wind_speed       DOUBLE,
        is_valid         BOOLEAN,
        dq_flag          VARCHAR,
        source_file      VARCHAR,
        processed_at     TIMESTAMP,
        PRIMARY KEY (observed_at, location, data_provider)
    )
"""

CREATE_GOLD_WEATHER = """
    CREATE TABLE IF NOT EXISTS gold_weather (
        window_start             TIMESTAMP,
        window_end               TIMESTAMP,
        outdoor_location         VARCHAR,    -- Lelystad, Schiphol
        indoor_location          VARCHAR,    -- hall, attic, bedroom1, bedroom2
        avg_outdoor_temp         DOUBLE,
        avg_outdoor_humidity     DOUBLE,
        avg_wind_speed           DOUBLE,
        avg_indoor_temp          DOUBLE,
        avg_indoor_humidity      DOUBLE,
        knmi_valid_count         INTEGER,
        zigbee_valid_count     INTEGER,
        is_valid                 BOOLEAN,
        dq_flag                  VARCHAR,
        processed_at             TIMESTAMP,
        PRIMARY KEY (window_start, outdoor_location, indoor_location)
    )
"""

def create_silver_tables():
    con = connect_to_db(SILVER_DB)
    try:
        create_table_with_ddl(con, CREATE_WEATHER_SILVER)
        logging.info("Silver tables ensured.")
    except Exception as e:
        logging.error(f"Silver table creation failed | {e}")
        raise
    finally:
        close_db(con)

def create_gold_tables():
    con = connect_to_db(GOLD_DB)
    try:
        create_table_with_ddl(con, CREATE_GOLD_WEATHER)
        logging.info("Gold tables ensured.")
    except Exception as e:
        logging.error(f"Gold table creation failed | {e}")
        raise
    finally:
        close_db(con)

if __name__ == "__main__":
    create_silver_tables()
    create_gold_tables()