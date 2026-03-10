# config.py
BRONZE_DB    = '/mnt/data/sentinel-pi/data/bronze/raw_source.db'
SILVER_DB    = '/mnt/data/sentinel-pi/data/silver/master_data.db'
GOLD_DB      = '/mnt/data/sentinel-pi/data/gold/analytics.db'
REFERENCE_DB = '/mnt/data/sentinel-pi/data/reference/reference.db'

LANDING_DIR    = '/mnt/data/sentinel-pi/data/bronze/landing_zone'
PROCESSED_DIR  = '/mnt/data/sentinel-pi/data/bronze/landing_zone/processed'

STATIONS = ['06269', '06240']  # Lelystad, Schiphol

OPS_DB = '/mnt/data/sentinel-pi/data/ops/ops.db'

# thresholds limits
KNMI_COMPLETENESS_MIN    = 0.84
ZIGBEE_COMPLETENESS_MIN  = 0.94

# db_utils.py functions:
# connect_to_db()          → write connections (pipeline only)
# connect_to_db_readonly() → read connections (AI, queries, reporting)
# close_db()               → always close after use