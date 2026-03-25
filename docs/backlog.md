Sentinel-Pi — Backlog
Last Updated: 2026-03-22

✅ Completed

 FileLock concurrency — ADR-029
 AI log summarization — Llama 1B instruct live
 config.py consolidation
 Bronze → Silver → Gold automated pipeline
 Percentage-based DQ — ADR-022
 Read-only connection strategy — ADR-023
 Gold clean slate policy — ADR-024
 ADR cleanup — 41 ADRs documented
 PI_INFRASTRUCTURE_CONSTRAINTS.md
 Git branch strategy — main + feature/govern-1-docker
 All 8 Dockerfiles built and tested
 docker-compose.yml — 8 services, full path volumes
 Ollama network — OLLAMA_HOST=0.0.0.0
 OLLAMA_URL — env var, localhost default + Docker override
 Prefect installed — RAM measured ~300MB server
 pipeline_flow.py — 8 tasks, sequential, retry logic
 Full chain Prefect run — all 8 tasks Completed
 Prefect confirmed — 3.6GB peak, no swap
 Docker user — kaushik in docker group, no sudo
 src/ restructured — 9 module folders
 sys.executable — replaces hardcoded VENV_PYTHON
 sys.path.insert — added to all module scripts
 prefect-server.service — systemd, enabled
 prefect-flow.service — systemd, enabled
 Marker 1 — Prefect survives reboot ✅
 Marker 2 — Scheduled runs unattended ✅
 Marker 3 — Docker user mapping ✅
 Marker 4 — pipeline.jsonl structured logging ✅
 Marker 5 — src/ restructured ✅
 ingest_data.py retired → temp_and_scratch/
 Zigbee load bug fixed — missing main()
 Gold watermark caught up — 2,934 valid rows
 pipeline_logger.py — write_jsonl_entry() + read_recent_jsonl() + run_name
 metrics_contract.py — KNMICollectMetrics, ZigbeeCollectMetrics, BronzeMetrics, SilverMetrics, GoldMetrics, AISummaryMetrics
 All 8 stages wired with structured metrics
 ai_summary.py reads pipeline.jsonl — cron.log replaced
 ADR-038 Pipeline Telemetry Schema Contract
 ADR-039 LLM Prompt Encodes Relationships Not Values
 ADR-040 Bronze Raw-As-Is Principle
 ADR-041 Structured Logging Replaces cron.log
 flake8 clean on all modified files — Govern.1


🔴 Immediate — Govern.1 Closure

 Merge feature/govern-1-docker → main
PR description + merge
Tag: govern-1-complete
 One clean 8-stage Prefect run confirmed post-merge
 Cancel all pending Prefect runs from UI before merge

Career — Overdue

 CV rewrite — all 6 roles
 LinkedIn About section update
 Sentinel-Pi entry — Govern.1 bullet added


🟡 Govern.2 Week 1 — Starting 2026-03-22
BL-000 — Non-Negotiable First

 flake8 + autopep8 GitHub Actions — PRIORITY 1
Duplicate function def caused silent wrong behaviour today
Must be in CI before any new feature work
Block merges that fail flake8

Code Fixes

 BL-001 — Merge collect_zigbee_files.py into collect_data_zigbee.py
Two scripts doing one job — maintenance overhead
 BL-002 — Deprecate cron.log
Remove LOG_FILE from config.py
Keep file until full pipeline run confirms JSONL complete
 BL-003 — Fix remaining flake8 errors
db_utils.py — unused datetime, logging imports
load_zigbee_to_bronze.py — unused db_utils imports
collect_zigbee_files.py — logger.log unused, start_time scope
metrics_contract.py — Optional unused
 BL-006 — Retire collect_data_raw.py
Legacy pre-medallion script — no Dockerfile, no task
 BL-009 — TZ=Europe/Amsterdam in all scripts
All scripts currently use datetime.now(timezone.utc)
Fix: ZoneInfo("Europe/Amsterdam") in pipeline_logger.py + all 8 scripts
 BL-010 — Fix .env bash safety
MQTT_TOPICS commas break source .env
Docker handles correctly via --env-file
Direct Pi execution needs explicit export pattern

Infrastructure

 BL-007 — Lock Prefect server to 127.0.0.1 only in systemd
Currently 0.0.0.0 — no external exposure needed
 BL-008 — Prefect concurrency limit — max 1 run at a time
max_concurrent_runs not supported in current serve() version
Investigate prefect deployment set-concurrency-limit

Parallel Execution

 Implement .submit().result() pattern
collect-knmi + collect-zigbee → truly parallel
load-knmi + load-zigbee → truly parallel
transform-knmi-silver + transform-zigbee-silver → parallel
Confirm with arch guru before implementing

AI Summary

 Move ai-summary to separate daily schedule
Separate Prefect deployment
Cron: "0 8 * * *" — not every 10 mins
Wasteful to run every pipeline cycle

dbt Integration

 pip install dbt-core dbt-duckdb
 models/silver/weather_silver.sql
 models/gold/gold_weather.sql
 tests/ → DQ thresholds as dbt tests
 docs/ → auto-generated lineage

Schema Registry

 contracts.json — extract from contracts.py
 schema_versions table in ops.db
 Pydantic validators in collect containers
 Prefect pre-condition tasks

Governance Documentation

 docs/dpia_sentinel.md
 docs/governance/ropa.md
 ADR-036 EU AI Act compliance mapping


🟠 Govern.2 — Week 3
DQ Evolution

 Soda Core — pip install soda-core-duckdb
 soda.yml from contracts.py thresholds
 Dual validation: Custom + Soda → ops.db

Lineage Stack

 pip install openlineage-python sqllineage
 Marquez Docker service in docker-compose.yml
 Table-level lineage: KNMI→Silver→Gold
 Prefect OpenLineage integration
 Column-level: SQLLineage parses transforms
 EU AI Act Article 13 compliance statement
 ADR-033 OpenLineage + Marquez

Data Freshness

 freshness_check() Prefect task
 freshness_log table in ops.db
 SLA thresholds — ADR-034:
KNMI Bronze: < 15 mins
Zigbee Bronze: < 15 mins
Gold: < 70 mins
 Streamlit freshness indicator (stretch)

Observability

 pipeline_runs table in ops.db
 DQ summary table in ops.db
 Record level error handling (DLQ)


🟢 Phase 3 — Scale
RAG Pipeline

 ChromaDB Docker service (ARM64) — ADR-035
 sentence-transformers embedding
 RAGAS evaluation — 100 KNMI queries
Target: 92% context precision (measure not assume)
 A/B: cosine vs alternatives
Blocked by: Govern.2 complete

Storage Evolution

 Parquet migration
 Iceberg migration — ADR-019

Enterprise Transition

 Airflow DAGs — ADR-020
 Kafka/MQTT streaming
 Weather extremes prediction — ADR-037

CI/CD Enterprise Pattern

 BL-011 — Immutable image pattern
Git commit → GitHub Actions build → local registry → Prefect pulls new image
Replace volume mount dev shortcut
Phase 3-4 item


🔵 Phase 4 — Explain

 Streamlit full dashboard — ADR-039
 Full LLM deployment
 RAG Streamlit demo


🔵 CI/CD

 GitHub Actions — flake8 + autopep8 on merge to main ← BL-000
 Platform flag: --platform linux/arm64/v8
 PR descriptions


📚 Market Fitment

 KM-04: Dutch AI governance backlog mock (overdue)
 KM-05: Doorbell PoC MVP — bounded 2-3 hrs
 KM-06: EU AI Act summary — Articles 9-15 (overdue)
 KM-07: Prompt engineering hybrid workflows
 KM-08: PESTLE-AI daily scan (overdue)


🐛 Known Bugs

 KNMI station mismatch
"not all values found in index 'station'"
Fix: method='nearest' in station lookup
Priority: Medium
 TZ=Europe/Amsterdam — BL-009
All scripts log UTC not CET
Fix: ZoneInfo("Europe/Amsterdam") in pipeline_logger.py + all scripts
Priority: High — Govern.2 Week 1
 ai_summary.log investigation
Where created? Consolidate or gitignore?
Priority: Low
 venv health check cron (58 * * * *)
Redundant — remove
Priority: Low
 Prefect parallel runs — BL-008
No concurrency limit in current version
Multiple runs cause DuckDB lock conflicts
Priority: High — Govern.2 Week 1


📚 Learning Backlog

 Prefect .submit().result() parallel pattern
 dbt models and tests
 Airflow DAGs mental model
 Kubernetes pods, deployments
 CTE deep dive — SQL practice
 DataHub / Atlan — Dutch market contract registry tools
Atlan used at Booking.com and Adyen
Enterprise path from metrics_contract.py TypedDict

BL-000  CLOSED  flake8 + GitHub Actions CI (Govern.2 Day 1)

BL-001  OPEN  Merge collect_zigbee_files.py into 
              collect_data_zigbee.py

BL-002  OPEN  Deprecate cron.log / LOG_FILE

BL-003  CLOSED  Fix remaining flake8 errors (superseded 
              by BL-000 — can CLOSE)

BL-006  OPEN  Retire collect_data_raw.py

BL-007  OPEN  Lock Prefect to 127.0.0.1 
              (superseded by Dagster decision — REVIEW)

BL-008 — Prefect SQLite lock causes server death
Prefect DB locked mid-write → server killed → 
data collection stops silently.
No alert. No recovery. Hours of data lost.

Root fix: Dagster (Govern.2 Day 2)
Interim fix: systemd Restart=always on prefect-server
             + RestartSec=30

BL-009  OPEN  TZ=Europe/Amsterdam all scripts

BL-010  OPEN  .env not bash-safe fix

BL-011  OPEN  Enterprise CI/CD immutable image pattern
              (Phase 3 or 4)

BL-012  NEW   NAS health monitoring cron (Week 2)