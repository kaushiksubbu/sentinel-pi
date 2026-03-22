# metrics_contract.py
# Pipeline observability contracts — per stage telemetry schemas.
# Defines required metrics fields for each pipeline stage.
# Add new stage contracts here when new stages are introduced.
# Never define metrics fields inside pipeline scripts directly.

from typing import TypedDict


class CollectMetrics(TypedDict):
    files_collected:  int
    api_calls_made:   int


class BronzeMetrics(TypedDict):
    records_landed:   int


class SilverMetrics(TypedDict):
    records_in:       int
    records_out:      int
    dq_pass_rate:     float


class GoldMetrics(TypedDict):
    knmi_rows_in:      int
    zigbee_rows_in:    int
    gold_rows_written: int
    dq_pass_rate:      float


class AISummaryMetrics(TypedDict):
    entries_read:       int
    summary_generated:  bool


class KNMICollectMetrics(TypedDict):
    files_collected: int   # one per station — expect 2
    api_calls_made:  int   # one per station per run


class ZigbeeCollectMetrics(TypedDict):
    files_collected:   int  # one per zone
    messages_received: int  # total MQTT messages across all zones
