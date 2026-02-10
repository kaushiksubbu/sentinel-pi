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