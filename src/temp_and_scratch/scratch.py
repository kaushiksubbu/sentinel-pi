# Run with: /mnt/data/sentinel-pi/.venv/bin/python3 src/scratch.py
# NOT with: python3 src/scratch.py


# scratch.py — always read-only
from db_utils import connect_to_db_readonly

# example - con = connect_to_db_readonly(GOLD_DB)


import duckdb
from datetime import datetime, timezone, timedelta
from config import GOLD_DB,OPS_DB,SILVER_DB
gold_con = duckdb.connect(GOLD_DB)
silver_con = duckdb.connect(SILVER_DB)
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

print(gold_con.execute('''
    SELECT COUNT(*),
    MAX(window_start)
    FROM gold_weather
    WHERE is_valid = true
    ''').fetchall()
)


#print(ops_con.execute('SELECT * FROM watermarks').fetchall())