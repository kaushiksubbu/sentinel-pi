# Run with: src/temp_and_scratch/scratch.py
# NOT with: python3 src/scratch.py
# /mnt/data/sentinel-pi/.venv/bin/python3 src/temp_and_scratch/
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common_func'))

# scratch.py — always read-only
from db_utils import connect_to_db_readonly

# example - con = connect_to_db_readonly(GOLD_DB)


import duckdb
from datetime import datetime, timezone, timedelta
from config import GOLD_DB,OPS_DB,SILVER_DB
gold_con = connect_to_db_readonly(GOLD_DB)
silver_con = connect_to_db_readonly(SILVER_DB)
ops_con = duckdb.connect(OPS_DB)

# print(con.execute('''
#     describe gold_weather
# ''').fetchall())
# print(con.execute('''
#     SELECT is_valid, COUNT(*),
#     MIN(window_start), MAX(window_start)
#     FROM gold_weather
#     GROUP BY is_valid
# ''').fetchall())


# con.execute('DROP TABLE IF EXISTS gold_weather')
# print('Dropped:', con.execute('SHOW TABLES').fetchall())



# con.execute('''DELETE FROM watermarks WHERE source = 'gold_weather' ''')
# print('Watermark reset:', con.execute('SELECT * FROM watermarks').fetchall())

# from config import SILVER_DB
# con = duckdb.connect(SILVER_DB)
# knmi_rows = con.execute("""
#         SELECT
#             DATE_TRUNC('hour', observed_at) AS window_start,
#             location                        AS outdoor_location,
#             AVG(temp)                       AS avg_outdoor_temp,
#             AVG(humidity)                   AS avg_outdoor_humidity,
#             AVG(wind_speed)                 AS avg_wind_speed,
#             COUNT(*)                        AS knmi_reading_count
#         FROM weather_silver
#         WHERE data_provider = 'knmi'
#         AND is_valid = TRUE
#         AND DATE_TRUNC('hour', observed_at) + INTERVAL '1 hour' 
#     < NOW()
#         GROUP BY DATE_TRUNC('hour', observed_at), location
#     """).fetchall()

# print(len(knmi_rows))

# gold.execute('DROP TABLE IF EXISTS gold_weather')
# gold.close()
# ops_con.execute('''DELETE FROM watermarks WHERE source = 'gold_weather' ''')
# print('Done. Watermarks:', ops_con.execute('SELECT * FROM watermarks').fetchall())
# ops_con.close()

print(silver_con.execute('''
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'main'
  AND table_type = 'BASE TABLE';
    ''').fetchall()
)

print(silver_con.execute('''
SELECT * from knmi_silver_validated;
    ''').fetchall()
)


#print(ops_con.execute('SELECT * FROM watermarks').fetchall())