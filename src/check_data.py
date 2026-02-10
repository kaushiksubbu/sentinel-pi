import xarray as xr
import os

# Find the file you just downloaded
landing_dir = "/mnt/data/sentinel-pi/data/landing_zone"
files = [f for f in os.listdir(landing_dir) if f.endswith('.nc')]
latest_file = os.path.join(landing_dir, files[0])

print(f"Opening: {latest_file}")

# Open the dataset
ds = xr.open_dataset(latest_file)

# KNMI station 269 is Lelystad. Let's find its index.
station_id = '06269'
ds.close()
try:
    # We select the station and pull 'ta' (Air Temperature in Celsius)
    # Note: Variable names in KNMI NetCDF are often 'ta' for temperature
    temp_data = ds.sel(station=station_id)
    current_temp = temp_data['ta'].values
    humidity=temp_data['rh'].values
    
    print(f"Station: Lelystad (06269)")
    print(f"Temperature: {current_temp} °C")
    print(f"Humidity: {humidity} RH")
except Exception as e:
    print(f"Could not find station 269. Available stations: {ds.station.values[:5]}...")
    print(f"Available variables: {list(ds.keys())}")