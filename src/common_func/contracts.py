# contracts.py
# Data contracts for Bronze → Silver transformation.
# Defines known field aliases per source.
# Add new aliases here when schema drift is detected.
# Never modify Silver transformation logic for new aliases.

ZIGBEE_CONTRACT = {
    "temperature": ["temperature", "temp", "tmp"],
    "humidity":    ["humidity", "hum", "rh"],
    "battery":     ["battery", "bat"],
}

KNMI_CONTRACT = {
    "temperature": ["ta"],
    "humidity":    ["rh"],
    "wind_speed":  ["ff"],
}
