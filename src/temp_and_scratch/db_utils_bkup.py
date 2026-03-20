import duckdb

def save_weather_to_duckdb(db_path, table, data, station_id):
    """
    Saves weather telemetry to a specific table for a specific station.
    
    Args:
        db_path (str): Path to the .db file
        table (str): Name of the table (e.g., 'weather_observations')
        data (dict): Dictionary containing 'timestamp', 'temp', 'hum'
        station_id (int): The station code (e.g., 269)
    """
    con = duckdb.connect(db_path)
    
    # 1. Dynamically create the table if it doesn't exist
    create_query = f"""
        CREATE TABLE IF NOT EXISTS {table} (
            timestamp TIMESTAMP PRIMARY KEY,
            station_id INTEGER,
            temperature_c DOUBLE,
            humidity_pct DOUBLE
        )
    """
    con.execute(create_query)
    
    # 2. Insert the data using safe placeholders for the values
    insert_query = f"INSERT OR IGNORE INTO {table} VALUES (?, ?, ?, ?)"
    
    con.execute(insert_query, [
        data["timestamp"], 
        station_id, 
        data["temp"], 
        data["hum"]
    ])
    
    con.close()