# Sentinel-Pi — Backlog
**Last Updated:** 2026-03-13

---

## ✅ Completed

- [x] FileLock concurrency control — implemented ADR-029
- [x] AI log summarization — Llama 1B instruct live, 08:30 cron
- [x] config.py consolidation — single source of truth
- [x] flake8 clean codebase — all modules
- [x] Bronze → Silver → Gold automated pipeline
- [x] Percentage-based DQ — ADR-022
- [x] Read-only connection strategy — ADR-023
- [x] Gold clean slate policy — ADR-024
- [x] ADR cleanup — restructured, numbered, updated (2026-03-12)
- [x] PI_INFRASTRUCTURE_CONSTRAINTS.md — committed
- [x] Cron lock mechanism — solved by FileLock (ADR-029)
- [x] Separate prod/dev directories — solved by Prefect Phase 2

---

## 🔴 Immediate — This Week

### AI Summary
- [ ] Prompt engineering review — align role definition
      with platform purpose and TPM narrative
      Update: ai_summary.py build_prompt() role definition
- [ ] Investigate logs/ai_summary.log
      Where created? Why separate from cron.log?
      Should it consolidate or stay separate?
      Check if gitignored
- [ ] AI summary hallucinations — revisit Phase 2
      Root cause: unstructured cron.log
      Fix: pipeline.jsonl structured logging Phase 2
      AI Summary
- [ ] Phase 2: feed pipeline.jsonl to ai_summary.py
      Replace cron.log parsing entirely
      Structured JSON input → eliminates hallucination
      Blocked by: pipeline.jsonl implementation Phase 2

### Housekeeping
- [ ] .gitignore — add locks/, __pycache__/, *.pyc
- [ ] Remove venv health check cron job (58 * * * *)
      Reason: redundant with 10-min pipeline + FileLock
      Action: remove from sudo crontab
      Update: ADR-004 consequences section
- [ ] Rename create_silver_tables.py → create_db_schemas.py
- [ ] scratch.py → always use connect_to_db_readonly()
- [ ] PR description for feature/knmi-silver-transform

### Career
- [ ] LinkedIn body update — Phase 1 complete narrative
- [ ] CV update — five bullet points confirmed
- [ ] Reconstruct missing daily logs from git history
      Use: git log + ADR dates + cron.log
      Purpose: complete narrative for portfolio

---

## 🟡 Phase 2 — Week 2 (Docker Week)

### Foundational
- [ ] Docker containerise read/validate/write modules
      Services: land-bronze / transform-silver /
                transform-gold / ai-summary
- [ ] Docker Compose orchestration
- [ ] Prefect — replace cron (ADR-020)
      Flow → pipeline, Tasks → read/validate/write
- [ ] pipeline_runs table in ops.db
      Feed from log_utils.py structured logging
- [ ] Migrate all logging to log_utils.log_event()
      Scope: ingest_data.py, load_knmi_to_bronze.py,
             transform_knmi_to_silver.py,
             transform_zigbee_to_silver.py,
             transform_silver_to_gold.py

### Schema Registry (Week 2 prep, Week 3 execute)
- [ ] contracts.json — extract from contracts.py (30 min)
- [ ] schema_versions table in ops.db (30 min)
      Fields: contract_name, version, schema_json,
              pii_classification, business_rules, active
- [ ] BLOCKED Week 3: Pydantic validators in land-bronze
- [ ] BLOCKED Week 3: Prefect pre-condition tasks

### Governance Documentation
- [ ] docs/dpia_sentinel.md — 30 mins, high value
- [ ] docs/governance/ropa.md — 30 mins, high value
- [ ] docs/legal/privacy_notice.md — 15 mins
- [ ] ADR-032 — EU AI Act compliance (split from ADR-021)

### Gold ML Feature Store
- [ ] gold_weather_features table (ADR-026)
      Fields: light_occupied, temp_trend_7d,
              humidity_spike, cold_snap_prob (NULL Week 4)

---

## 🟠 Phase 2 — Week 3

### DQ Evolution
- [ ] pip install soda-core-duckdb
- [ ] soda.yml from contracts.py thresholds
- [ ] Docker service: soda scan
- [ ] Dual validation: Custom + Soda → ops.db
- [ ] Pydantic validators in land-bronze (ADR-031)
- [ ] Prefect pre-condition tasks (ADR-031)

### Observability
- [ ] DQ summary table in ops.db
- [ ] Pipeline lineage tracking
- [ ] Record level error handling (DLQ)

### Data Platform
- [ ] Zigbee streaming gate criteria review
- [ ] OKRs — formal document
- [ ] roi_calculator.py — discuss before building


### Phase 2 Addition
- [ ] dbt integration — replace raw SQL transforms
      Silver transform → dbt models
      Gold transform   → dbt models
      DQ thresholds    → dbt tests
      contracts.py     → dbt schema.yml
      Why: Dutch market expects dbt fluency
           Booking/ING/Adyen standard stack
Priority: Week 2-3 alongside Docker
---

## 🟢 Phase 3 — Week 4+

### DQ
- [ ] Great Expectations — Data Context + Expectations
      from contracts.py, Prefect Checkpoint integration
      Note: optional, documentation focus only

### Storage Evolution
- [ ] Parquet migration (Bronze → Parquet files)
- [ ] Storage/Parquet audit post migration
- [ ] Iceberg migration — DuckDB → Parquet → Iceberg (ADR-019)

### Enterprise Transition
- [ ] Airflow — enterprise orchestration (ADR-020)
- [ ] Kafka/MQTT streaming ingestion
- [ ] API gateway for real-time queries
- [ ] Feature store serving ML
- [ ] Kubernetes conceptual + one toy deployment
- [ ] Terraform mental model

### Privacy / Compliance (Phase 2-3)
- [ ] pii_guard.py Bronze→Silver
- [ ] data_classification column in Iceberg metadata
- [ ] Retention cleanup job (bronze_raw: 30 days)
- [ ] data_subject_api.py — mock endpoints
- [ ] breach_detector.py

### Weather Extremes (Week 4)
- [ ] Cold snap: temp < 4°C + pressure_drop > 2hPa
- [ ] Heat snap: temp > 28°C + humidity_drop > 10%
- [ ] action_recommend: PRE-HEAT / PRE-COOL / STANDBY
- [ ] contracts.py — add pressure field (pp, p0)

---

## 🔵 Git / CI/CD

- [ ] Git branching strategy formalised
- [ ] GitHub Actions CI/CD pipeline
- [ ] flake8 / ruff added to GitHub Actions

---

## 📚 Market Fitment

### KM-04: Dutch AI Governance Tool
- [ ] Mock AI product backlog — 3 features
      (NEA prompt tuner, GDPR audit trail,
       AI Act compliance checker)
- [ ] MoSCoW prioritisation of 3 features
- [ ] 1 LLM tie-in per feature
Priority: This week — +3-5% fit boost

### KM-05: Hands-on AI Tech Depth
- [ ] Hugging Face tutorials — LLM fine-tuning for PM
- [ ] 1 deployment in 2 weeks
- [ ] Map to Sentinel-Pi ML pipeline narrative
Priority: Week 2-3

### KM-06: Dutch Compliance & Governance
- [ ] EU AI Act summary review (Articles 9-15)
- [ ] Mock governance framework for AI backlog
- [ ] GDPR policy translation for non-tech stakeholders
Priority: This week — ties to ADR-021 + ADR-032

### KM-07: Prompt Engineering Fluency
- [ ] Hands-on hybrid human-AI workflows
- [ ] Lleverage tool exploration
- [ ] Map to ai_summary.py prompt design already built
Priority: Week 2

### KM-08: PESTLE-AI Daily Scan
- [ ] 15 min daily habit — Dutch AI market pulse
- [ ] Map each force to arch strength or CV bullet
- [ ] Build bank of 10 PESTLE insights before
      first interview
Priority: Start Monday alongside Phase 2
---

## 📚 Learning Backlog

- [ ] Docker orchestration concepts
- [ ] Prefect flows and tasks
- [ ] Airflow DAGs mental model
- [ ] Kubernetes pods, deployments, services
- [ ] Terraform plan/apply/modules
- [ ] CTE deep dive — SQL pattern practice
- [ ] Git branching — feature/dev/main strategy

---

## ADR Backlog

- [ ] ADR-031 — Schema validation evolution
      contracts.py → Pydantic + ops.db registry
      Week 2 prep, Week 3 execute
- [ ] ADR-032 — EU AI Act compliance mapping
      Split from ADR-021
- [ ] ADR-033 — Weather extremes prediction
      Cold snap + heat snap (Week 4)

### BACKLOG — Doorbell PoC (KM-05 bridge project)

Week 2 (this week) — MVP only, 2-3 hrs max:
- [ ] check_doorbell() pipeline — core function
      YOLOv8n person detection
      face_recognition comparison
      return: "you" / "visitor" / "no_person"
      log: latency, RAM, confidence
- [ ] HA motion trigger → /tmp/doorbell.jpg
- [ ] Alexa announcement via HA REST API
- [ ] Latency target: <10s confirmed on Pi

Week 3 — if Phase 2 stable:
- [ ] Confidence thresholding
- [ ] HA dashboard detection history
- [ ] Latency optimisation log (18s→3s story)

Week 4 — stretch only if time permits:
- [ ] Multi-face handling
- [ ] Model fine-tuning on personal photos
- [ ] HA custom component packaging

NOT this week:
→ Production logging
→ Fine-tuning
→ Multi-face