select
    observed_at,
    location,
    data_provider,
    temp,
    humidity,
    wind_speed,
    is_valid,
    dq_flag,
    processed_at
from {{ source('silver', 'weather_silver') }}
where data_provider = 'zigbee'
