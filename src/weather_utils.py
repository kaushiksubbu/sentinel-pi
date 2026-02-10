import xarray as xr
import pandas as pd # Adding pandas makes life easier here

def extract_station_data(file_path, station_id):
    """Parses .nc file and returns a dictionary of clean data."""
    ds = xr.open_dataset(file_path)
    
    # Standardize station search
    all_stations = [s.decode().strip() if isinstance(s, bytes) else str(s).strip() for s in ds.station.values]
    
    if station_id not in all_stations:
        ds.close()
        raise ValueError(f"Station {station_id} not found in file.")
        
    idx = all_stations.index(station_id)
    subset = ds.isel(station=idx)
    
    # 2. THE FIX: Convert the numpy datetime64 to a standard Python string DuckDB loves
    # .item() extracts the single value from the array
    # .astype('datetime64[s]') removes the nanosecond clutter
    raw_time = subset['time'].values.flatten()[0]
    clean_timestamp = pd.to_datetime(raw_time).strftime('%Y-%m-%d %H:%M:%S')

    data = {
        "timestamp": clean_timestamp,
        "temp": float(subset['ta'].values),
        "hum": float(subset['rh'].values)
    }
    ds.close()
    return data