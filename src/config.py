# config.py
BRONZE_DB    = '/mnt/data/sentinel-pi/data/bronze/raw_source.db'
SILVER_DB    = '/mnt/data/sentinel-pi/data/silver/master_data.db'
GOLD_DB      = '/mnt/data/sentinel-pi/data/gold/analytics.db'
REFERENCE_DB = '/mnt/data/sentinel-pi/data/reference/reference.db'

LANDING_DIR    = '/mnt/data/sentinel-pi/data/bronze/landing_zone'
PROCESSED_DIR  = '/mnt/data/sentinel-pi/data/bronze/landing_zone/processed'

STATIONS = ['06269', '06240']  # Lelystad, Schiphol

OPS_DB = '/mnt/data/sentinel-pi/data/ops/ops.db'