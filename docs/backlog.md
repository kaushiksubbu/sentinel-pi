# Sentinel-Pi — Backlog

## 🚫 WIP Gate
Gold aggregation and AI log summarization must complete before any backlog item moves to WIP.
**Gold: ✅ Complete. AI log summarization: 🔜 Tomorrow.**

---

## 🔴 High Priority

### DevOps
- [ ] Cron lock mechanism (flock) — pipeline runtime ~6 mins, interval 10 mins, overlap risk
- [ ] venv health check cron job — silent failures before pipeline runs
- [ ] Separate prod/dev directories — 
      BLOCKED: solved by Prefect Phase 2

### Data Platform
- [ ] AI log summarization — Phi3/Ollama daily report ← **NEXT SESSION**
- [ ] pipeline_runs table in ops.db (observability + lineage)

---

## 🟡 Medium Priority

### Platform Observability
- [ ] Pipeline lineage tracking
- [ ] Record level error handling (DLQ)
- [ ] DuckDB savepoints investigation
- [ ] DQ summary table in ops.db

### Storage
- [ ] Parquet migration (Bronze → Parquet files)
- [ ] Storage/Parquet audit post migration

### Data Platform
- [ ] contracts.py — KNMI contract validation
- [ ] Zigbee streaming gate criteria review
- [ ] OKRs — Define platform OKRs for TPM positioning
- [ ] Rename create_silver_tables.py → create_db_schemas.py

### Privacy / Compliance
- [ ] ADR-020 implementation — pii_guard.py Bronze→Silver
- [ ] data_classification column to Iceberg metadata
- [ ] Retention cleanup job (bronze_raw: 30 days)

---

## 🟢 Planned Phases

### Phase 2 — Docker
- [ ] Docker containerise read/validate/write modules
- [ ] Docker Compose orchestration
- [ ] Prefect — replace cron (ADR-016)
- [ ] DLQ (Dead Letter Queue) for failures
- [ ] Formal connection pooling strategy
### Phase 2 Tech Debt
Task:   Migrate all logging to log_utils.log_event()
Reason: Reduce logging debt, enable structured observability,
        path to microservice adoption
Scope:  ingest_data.py, load_knmi_to_bronze.py,
        transform_knmi_to_silver.py,
        transform_zigbee_to_silver.py,
        transform_silver_to_gold.py
Blocked by: Phase 1 closure

### Phase 3 — Enterprise
- [ ] Iceberg migration — DuckDB tables → Parquet → Iceberg (ADR-015)
- [ ] Airflow — enterprise orchestration transition (ADR-016)
- [ ] Kubernetes conceptual + one toy deployment
- [ ] Terraform mental model
- [ ] Kafka/MQTT streaming ingestion
- [ ] API gateway for real-time queries
- [ ] Feature store serving ML

---

## 🔵 Git / CI/CD
- [ ] PR description for feature/knmi-silver-transform
- [ ] Git branching strategy formalised
- [ ] GitHub Actions CI/CD pipeline
- [ ] Linting — flake8 or ruff added to pipeline
- [ ] flake8 linting added to GitHub Actions pipeline

---

## 📚 Learning Backlog
- [ ] Docker orchestration concepts
- [ ] Prefect flows and tasks
- [ ] Airflow DAGs
- [ ] Kubernetes pods, deployments, services
- [ ] Terraform plan/apply/modules mental model
- [ ] CTE deep dive — SQL pattern practice
- [ ] Git branching — feature/dev/main strategy

---

## 🗂 Housekeeping
- [ ] Rename create_silver_tables.py → create_db_schemas.py
- [ ] ADR cleanup — standardise numbering and format
- [ ] PI_INFRASTRUCTURE_CONSTRAINTS.md — committed ✅
- [ ] scratch.py → always use connect_to_db_readonly()

# Governance Documentation
- [ ] docs/dpia_sentinel.md    — 30 mins, high value
- [ ] docs/governance/ropa.md  — 30 mins, high value
- [ ] docs/legal/privacy_notice.md — 15 mins
- [ ] data_subject_api.py      — mock endpoints, Phase 2
- [ ] breach_detector.py       — Phase 2
Priority: After Phase 1 closure