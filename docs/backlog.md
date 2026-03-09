# Sentinel-Pi — Backlog

## Platform Observability
- [ ] Pipeline lineage tracking
- [ ] Record level error handling (DLQ)
- [ ] DuckDB savepoints investigation

## Storage
- [ ] Parquet migration

## DevOps
- [ ] Docker Phase 2 — containerise read/validate/write modules
- [ ] Docker Compose orchestration
- [ ] Kubernetes conceptual + one toy deployment
- [ ] Terraform mental model

## Data Platform
- [ ] pipeline_runs table in ops.db (observability + lineage)
- [ ] contracts.py — KNMI contract validation
- [ ] ADR cleanup and numbering standardisation
- [ ] Zigbee streaming gate criteria review
- [ ] Storage/Parquet audit post migration
- [ ] Iceberg migration (after Parquet — ADR-015)
      Sequence: DuckDB tables → Parquet → Iceberg
      Blocked by: Parquet migration

## Git / CI/CD
- [ ] PR description for feature/knmi-silver-transform
- [ ] Git branching strategy formalised
- [ ] GitHub Actions CI/CD pipeline

## Blocked By Week 3 Closure
Gold aggregation and AI log summarization must complete before any backlog item moves to WIP.

## Housekeeping
- [ ] Rename create_silver_tables.py → create_db_schemas.py
- [ ] venv health check cron job
- [ ] PI_INFRASTRUCTURE_CONSTRAINTS.md commit to repo

## Orchestration  
- [ ] Prefect Phase 2 — replace cron (ADR-016)
- [ ] Airflow Phase 3 — enterprise transition