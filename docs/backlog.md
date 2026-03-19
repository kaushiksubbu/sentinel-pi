# Sentinel-Pi — Backlog
**Last Updated:** 2026-03-18

---

## ✅ Completed

- [x] FileLock concurrency — ADR-029
- [x] AI log summarization — Llama 1B instruct live
- [x] config.py consolidation
- [x] flake8 clean codebase
- [x] Bronze → Silver → Gold automated pipeline
- [x] Percentage-based DQ — ADR-022
- [x] Read-only connection strategy — ADR-023
- [x] Gold clean slate policy — ADR-024
- [x] ADR cleanup — 35 ADRs documented
- [x] PI_INFRASTRUCTURE_CONSTRAINTS.md
- [x] Git branch strategy — main + feature/govern-1-docker
- [x] All 4 Dockerfiles built and tested
- [x] docker-compose.yml — full path volumes
- [x] Ollama network — OLLAMA_HOST=0.0.0.0
- [x] OLLAMA_URL — env var, localhost default + Docker override
- [x] Prefect installed — RAM measured ~300MB server
- [x] pipeline_flow.py — all 4 tasks, retry logic
- [x] Full chain Prefect run — Completed ✅
- [x] Prefect confirmed — 3.6GB peak, no swap

---

## 🔴 Immediate — This Week

### Govern.1 Remaining
- [ ] Fix Docker container user — runs as root
      Add user: "1000:1000" to docker-compose.yml
      Prevents permission conflicts with Pi user
- [ ] Re-enable cron OR schedule Prefect deployment
      Cron disabled — data not flowing
      Option A: re-enable cron temporarily
      Option B: Prefect deployment schedule now
- [ ] pipeline.jsonl structured logging
      Replace cron.log parsing in ai_summary.py
      Feeds exact metrics → eliminates hallucination
- [ ] log_utils.py migration — all modules
- [ ] pipeline_runs table in ops.db
- [ ] Commit docker-compose.yml user fix

### Bugs
- [ ] KNMI station mismatch — pre-existing
      "not all values found in index 'station'"
      Fix: method='nearest' in station lookup
      Priority: Medium
- [ ] Remove sudo requirement for docker
      sudo usermod -aG docker kaushik

### Housekeeping
- [ ] .gitignore — add locks/, __pycache__/, *.pyc
- [ ] Remove venv health check cron (58 * * * *)
- [ ] Rename create_silver_tables.py → create_db_schemas.py
- [ ] Automate daily log creation — cron 0 7 * * *
- [ ] PR description for feature/govern-1-docker
- [ ] Restructure src/ to reflect processing stages
      Current: flat src/ folder
      Target:  src/ingestion/    → land-bronze scripts
               src/transforms/   → silver + gold scripts
               src/pipeline/     → pipeline_flow.py ✅ already done
               src/ai/           → ai_summary.py
               src/utils/        → config.py, db_utils.py,
                                   contracts.py, log_utils.py
      Priority: Low — do during Phase 2 cleanup
### Career
- [ ] CV rewrite — all 6 roles
- [ ] LinkedIn headline + About section

---

## 🟡 Govern.1 — Week 2

### Core
- [ ] dbt integration
      pip install dbt-core dbt-duckdb
      models/silver/weather_silver.sql
      models/gold/gold_weather.sql
      tests/ → DQ thresholds as dbt tests
      docs/ → auto-generated lineage
- [ ] gold_weather_features table — ML feature store
- [ ] Prefect deployment schedule
      Replace cron permanently

### Schema Registry
- [ ] contracts.json — extract from contracts.py
- [ ] schema_versions table in ops.db
- [ ] BLOCKED Week 3: Pydantic validators
- [ ] BLOCKED Week 3: Prefect pre-condition tasks

### Governance
- [ ] docs/dpia_sentinel.md
- [ ] docs/governance/ropa.md
- [ ] docs/legal/privacy_notice.md
- [ ] ADR-032 EU AI Act compliance

---

## 🟠 Govern.2 — Week 3

### DQ Evolution
- [ ] Soda Core — pip install soda-core-duckdb
- [ ] soda.yml from contracts.py thresholds
- [ ] Dual validation: Custom + Soda → ops.db
- [ ] Pydantic validators in land-bronze
- [ ] Prefect pre-condition tasks

### Lineage Stack
- [ ] pip install openlineage-python sqllineage
- [ ] Marquez Docker service in docker-compose.yml
- [ ] Table-level lineage: KNMI→Silver→Gold
- [ ] Prefect OpenLineage integration
- [ ] Column-level: SQLLineage parses transforms
- [ ] EU AI Act Article 13 compliance statement
- [ ] RAM verification: 320MB claimed → measure

### Data Freshness
- [ ] freshness_check() function
- [ ] freshness_log table in ops.db
- [ ] Prefect task: freshness after chain
- [ ] Streamlit freshness indicator (stretch)
      Green/Amber/Red per layer

### Observability
- [ ] DQ summary table in ops.db
- [ ] Pipeline lineage tracking
- [ ] Record level error handling (DLQ)


### Govern.2
- [ ] Modularise pipeline_flow.py → 4 Docker tasks
      Each @task runs its Docker container
      Prefect orchestrates containers not Python functions
      Closes the Docker + Prefect integration properly
Priority: Govern.2 Week 3
---

## 🟢 Phase 3 — Scale

### RAG Pipeline
- [ ] ChromaDB Docker service (ARM64)
- [ ] sentence-transformers embedding pipeline
- [ ] Basic retrieval — top-5 cosine
- [ ] RAG pipeline: embed→query→context→Llama
- [ ] RAGAS evaluation — 100 KNMI queries
      Target: 92% context precision (measure, not assume)
- [ ] A/B: cosine vs alternatives
- [ ] Pi RAM proof
Blocked by: Govern.2 complete

### Storage Evolution
- [ ] Parquet migration
- [ ] Iceberg migration — ADR-019

### Enterprise Transition
- [ ] Airflow — ADR-020
- [ ] Kafka/MQTT streaming
- [ ] Kubernetes conceptual
- [ ] Weather extremes: cold/heat snap

---

## 🔵 Phase 4 — Explain

- [ ] Streamlit full dashboard
      Freshness + lineage + DQ + RAG + AI summaries
- [ ] Full LLM deployment
- [ ] RAG Streamlit demo interface

---

## 🔵 Git / CI/CD

- [ ] GitHub Actions CI/CD pipeline
- [ ] Platform flag: --platform linux/arm64/v8
- [ ] flake8 / ruff in GitHub Actions
- [ ] PR description for feature/govern-1-docker

---

## 📚 Market Fitment

### KM-04: Dutch AI Governance Tool
- [ ] Mock AI product backlog — 3 features
- [ ] MoSCoW prioritisation
- [ ] 1 LLM tie-in per feature

### KM-05: Hands-on AI Tech Depth
- [ ] Hugging Face tutorials
- [ ] Doorbell PoC MVP — bounded 2-3 hrs

### KM-06: Dutch Compliance & Governance
- [ ] EU AI Act summary (Articles 9-15)
- [ ] Mock governance framework

### KM-07: Prompt Engineering Fluency
- [ ] Hybrid human-AI workflows
- [ ] Map to ai_summary.py prompt design

### KM-08: PESTLE-AI Daily Scan
- [ ] 15 min daily — Dutch AI market pulse
- [ ] Bank of 10 insights before first interview

---

## 📚 Learning Backlog

- [ ] Prefect flows and tasks — done ✅ basic
- [ ] Prefect deployment schedules
- [ ] Airflow DAGs mental model
- [ ] dbt models and tests
- [ ] Kubernetes pods, deployments
- [ ] CTE deep dive — SQL practice