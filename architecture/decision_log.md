# 📔 Decision Log: Sentinel-Pi

## [ADR-001] Medallion Storage Pattern
**Status:** Implemented
**Why:** To ensure data integrity, we store "Raw" API responses in `data/bronze` (JSON) before transforming them into "Clean" Iceberg tables in `data/silver`. This allows us to re-process data if our business logic changes without re-calling the API.

## ADR-002: Schema Expansion (Humidity) Decision: Added humidity to the Silver table schema. Why: Requirement change to support broader climate analytics. Using Iceberg allows us to evolve the schema (Schema Evolution) without needing to drop and recreate the table, preserving our historical temperature-only rows.

## ADR-005: Resolved environment path conflicts caused by legacy direnv configurations during migration to external storage. Standardized on local .venv for portability.

## [ADR-007] Automated Ingestion via Crontab
**Status:** Implemented
**Reason:** To build a historical dataset for future AI training (Ollama). 
**Strategy:** Set to hourly frequency to balance data granularity with API rate limits. All output is redirected to `/logs/cron.log` for observability and troubleshooting.