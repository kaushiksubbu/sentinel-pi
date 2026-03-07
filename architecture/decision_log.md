# 📔 Decision Log: Sentinel-Pi

This log tracks the architectural evolution of the Sentinel-Pi project. Each record follows a consistent format to ensure traceability and clarity for Module 1 and beyond.

---

## [ADR-001] Medallion Storage Pattern
* **Status:** Accepted / Implemented
* **Date:** 2026-02-09
* **Context:** Need a structured way to manage raw data vs. processed data.
* **Decision:** Implement a Bronze/Silver medallion architecture.
* **Rationale:** Storing raw API responses in `data/bronze` (JSON) allows us to re-process data without re-calling the API if our business logic changes.
* **Consequences:** Requires extra storage for raw files, but ensures 100% data recoverability.

## [ADR-002] Schema Evolution (Humidity)
* **Status:** Accepted
* **Date:** 2026-02-09
* **Context:** Requirement change to support broader climate analytics.
* **Decision:** Add humidity to the Silver table schema.
* **Rationale:** Using DuckDB/Iceberg allows us to evolve the schema without dropping and recreating the table, preserving historical temperature-only rows.

## [ADR-003] Standardized Virtual Environments
* **Status:** Resolved
* **Date:** 2026-02-07
* **Context:** Legacy `direnv` configurations were causing path conflicts during storage migration.
* **Decision:** Standardize on a local `.venv` for portability.
* **Rationale:** Simplifies automation scripts (Cron/Systemd) by providing a single, predictable path to the Python interpreter.

## [ADR-004] Automated Ingestion via Crontab
* **Status:** Implemented
* **Date:** 2026-02-09
* **Context:** Building a historical dataset for future AI training (Ollama).
* **Decision:** Use `cron` for hourly ingestion.
* **Rationale:** Hourly frequency balances data granularity with KNMI API rate limits. 
* **Consequences:** Requires robust error logging to `/logs/cron.log` to monitor "silent" failures.

## [ADR-005] Local AI via Ollama
* **Status:** Accepted (Planned for Week 5)
* **Date:** 2026-02-10
* **Context:** Need LLM capabilities for thermal efficiency analysis.
* **Decision:** Deploy Ollama locally on Raspberry Pi.
* **Rationale:** Ensures **Data Sovereignty** (privacy) and avoids recurring API costs.
* **Consequences:** Limited to quantized models due to Pi RAM constraints (8GB).

## [ADR-006] Modular Utility Architecture
* **Status:** Accepted / Implemented
* **Date:** 2026-02-10
* **Context:** Monolithic scripts were becoming difficult to scale and test.
* **Decision:** Refactor into `src/utils/` and `src/processors/`.
* **Rationale:** Separates extraction logic from database logic. Makes adding Source D (Zigbee) possible without breaking Source A (KNMI).

## [ADR-007] Lightweight Data Quality (DQ) Layer
* **Status:** Proposed (Planned for Week 2/3)
* **Date:** 2026-02-10
* **Context:** Raw sensor data often contains spikes or nulls.
* **Decision:** Implement `validate_data()` + Soda Core checks.
* **Rationale:** Prevents "poisoning" the AI models with false data and provides observability into sensor health (e.g., low battery alerts).

## ADR - 2026-02-28
* Decided to keep 5-min micro-batch per hour as MVP stage; future streaming mode will replace this once schema, data reliability, and governance are validated.
* Source fidelity in filenames prioritizes auditability over downstream tooling convenience.
* Micro-batching preserves event-level data with timestamps inside JSON; ensures traceable provenance.
* Observability/logging confirms ingestion is happening correctly; no missing messages detected in the latest run.
* Governance trade-offs: hourly sampling vs full streaming is an explicit, controlled decision.

## ADR - 2026-03-01
* Genericized db_utils to create tables dynamically based on incoming data - though this is loading JSONs as Varchar - this is due to how the schema is infered. Also adds speed to processing.
* Move successfully processed files to /processed folder to avoid duplicate processing,

## ADR - 2026-03-03
* Bronze stores raw observations at source frequency.
Silver applies validation and conforms schema at atomic granularity.
Gold aggregates to hourly windows for analytics and AI consumption.
AI inference operates exclusively on Gold models to ensure semantic stability and cost efficiency.

## ADR - 2026-03-06
The platform requires clear separation between:
raw ingestion
transformed datasets
analytics outputs
operational metadata

A modular directory structure improves data lineage, governance, and maintainability.

Decision
Adopt a layered storage structure aligned with medallion architecture.

/sentinel-pi/data/

bronze/
    landing_zone/        # incoming raw files
        processed/       # archived after ingestion
    raw_source.db        # structured raw storage

silver/
    master_data.db       # validated, standardized datasets

gold/
    analytics.db         # aggregated analytics datasets

reference/
    reference.db         # lookup tables, station metadata

ops/
    ops.db               # operational metadata
Operational Metadata Tables

ops.db

watermarks
    last processed timestamp per pipeline

pipeline_logs
    execution history

dq_summary
    aggregated data quality metrics


Rationale
This structure enables:
clear data lineage
operational observability
independent lifecycle management of datasets

Future Evolution
Planned improvements:
Parquet storage for Silver layer
record-level error isolation via Dead Letter Queue
containerized pipeline execution

# SCALING NOTES — Phase 3+
# Current: DuckDB tables, hourly batch, <1K rows/day
# Scale trigger: >100K rows/day or query latency >1s
# Solution: Parquet partitioned by date, Iceberg versioning
# Migration: no schema changes required

Single canonical Silver table decision
Modular monolith over microservices
Batch over streaming — Zigbee MVP gate
Option A Bronze duplicate strategy
validate_knmi_row thresholds

# [ADR-008] Data Contract Pattern for Schema Drift
Status: Accepted / Implemented
Date: 2026-03-07
Context:
Zigbee sensors may emit different field names across firmware versions. Example: temperature vs temp vs tmp. Hardcoding field names in transformation logic creates brittle code that breaks silently on schema drift.
Decision:
Introduce contracts.py as a centralised field alias registry. Silver transformation reads field values via extract_by_contract() — never by hardcoded key name.
Rationale:

New field alias → update contracts.py only. No transformation logic changes.
Unknown alias detected → warning logged. Silent data loss prevented.
Consistent pattern across all sources — KNMI and Zigbee both use contracts.
Separation of concerns: config.py owns infrastructure, contracts.py owns data semantics.

Consequences:

All new sources must define a contract before Silver transformation is built.
contracts.py becomes a governed file — changes require ADR review.


# [ADR-009] Bath Room Excluded From Silver
Status: Accepted / Implemented
Date: 2026-03-07
Context:
Sentinel-Pi purpose is correlating external weather with indoor home environment. Bath room humidity and temperature are internally driven — shower, bath events — not representative of passive weather correlation.
Decision:
Exclude zigbee2mqtt/Bath T&H topic at Bronze read stage. Filter applied in read_zigbee_bronze() SQL query via topic NOT LIKE '%Bath%'.
Rationale:

Bath microclimate would introduce noise into ML correlation models.
Filtering at read stage — not validation stage — is more efficient. Why validate what we've decided to exclude?
Bath data remains in Bronze — decision is reversible if use case changes.

Consequences:

Bath data preserved in Bronze. Silver and Gold never include Bath.
If Bath analysis is needed in future — separate query against Bronze only.


# [ADR-010] Indoor Humidity Ceiling Set at 85%
Status: Accepted / Implemented
Date: 2026-03-07
Context:
Netherlands indoor humidity above 85% typically indicates condensation problems, sensor malfunction, or unusual events — not representative of normal home living conditions relevant to weather correlation.
Decision:
Indoor humidity valid range: 25% to 85%. Values above 85% flagged as rh_out_of_range in Silver dq_flag. Not dropped — Silver never deletes.
Rationale:

100% ceiling is technically valid but not representative for this platform's purpose.
85% ceiling flags anomalies for AI layer investigation.
Aligns with governance principle: flag and preserve, never drop.

Consequences:

Rows above 85% humidity land in Silver with is_valid = FALSE.
Gold aggregation excludes invalid rows — anomalies do not pollute analytics.


# [ADR-011] Modular Functions Over True Microservices (Phase 1)
Status: Accepted / Implemented
Date: 2026-03-07
Context:
True microservices require independent processes, inter-process communication, and orchestration infrastructure. On Pi 4 with 4GB RAM running DuckDB, Ollama, Zigbee MQTT, and cron — the overhead is real and premature.
Decision:
Build independent modular functions (read, validate, write) within single Python scripts. Each function has single responsibility and is independently testable. Orchestrated by a thin coordinator function.
Rationale:

Modular functions are the correct building blocks for future microservices.
Docker Phase 2 is the natural containerisation point — each module becomes a container.
No rewrite required for migration. Architecture comment added to code.
Building true microservices in raw Python on Pi 4 before Docker is premature complexity.

Consequences:

Phase 2 Docker: each module becomes its own container orchestrated via Docker Compose.
Current code requires zero rewrite for that migration.

Architecture Note added to code:
python# ARCHITECTURE NOTE:
# Functions here are modular by design — not yet microservices.
# Phase 2: each function becomes its own Docker container
# orchestrated via Docker Compose.
# This code requires no rewrite for that migration.

# [ADR-012] Full Rollback on Silver Transform Failure
Status: Accepted / Implemented
Date: 2026-03-07
Context:
During Bronze → Silver transformation, a row-level failure mid-batch could result in partial Silver load. Partial loads look valid but are incomplete — worse than no load at all.
Decision:
Full rollback on any transformation failure. Watermark only updated after complete successful batch. Failed runs retry entire batch on next cron execution.
Rationale:

Partial Silver load violates data integrity — incomplete data appears valid.
Full rollback preserves Silver integrity at cost of reprocessing overhead.
Acceptable tradeoff at current scale (<1K rows/hour).

Consequences:

On failure — entire batch retried next run. Small overlap risk mitigated by INSERT OR IGNORE.
TODO Phase 2: Dead Letter Queue for record-level error isolation. Failed rows isolated, successful rows committed.