# 📔 Architecture Decision Records (ADR): Sentinel-Pi
**Last Updated:** 2026-03-18

Format: Context → Decision → Rationale → Consequences
Rule: ADR numbering is chronological and immutable.

---

## [ADR-001] Medallion Storage Pattern
**Status:** Accepted / Implemented
**Date:** 2026-02-09

**Context:** Need structured way to manage raw vs processed data.
**Decision:** Bronze/Silver/Gold medallion architecture.
**Rationale:** Raw API responses in bronze allow re-processing without re-calling API.
**Consequences:** Extra storage for raw files. 100% data recoverability. Each layer applies stricter governance than previous.

---

## [ADR-002] Schema Evolution — Humidity Field Added
**Status:** Accepted / Implemented
**Date:** 2026-02-09

**Context:** Requirement change for broader climate analytics.
**Decision:** Add humidity to Silver table schema.
**Rationale:** DuckDB allows schema evolution without dropping tables.
**Consequences:** Historical rows have NULL humidity. No data loss.

---

## [ADR-003] Standardised Virtual Environment
**Status:** Resolved → superseded by Docker Phase 2
**Date:** 2026-02-07

**Context:** Legacy direnv caused path conflicts.
**Decision:** Standardise on local .venv.
**Rationale:** Single predictable path for automation scripts.
**Consequences:** Docker Phase 2 supersedes — containers carry own dependencies.

---

## [ADR-004] Automated Ingestion via Crontab
**Status:** Accepted / Implemented — Updated 2026-03-09
**Date:** 2026-02-09

**Context:** Pipeline requires scheduled execution. Hourly frequency insufficient for Gold DQ.
**Decision:** Three cron jobs:
```
58 * * * *   → venv health check (review — redundant, remove Phase 2)
*/10 * * * * → pipeline ingestion
30 8 * * *   → AI daily summary
```
**Frequency Change:** Hourly → 10 minutes. KNMI publishes 6 files/hour. Hourly cron = 2 rows/hour → all Gold invalid.
**Consequences:** 6x more Bronze rows/hour. Overlap risk managed by FileLock. Phase 2: Prefect replaces cron entirely.

---

## [ADR-005] Local AI via Ollama
**Status:** Accepted / Implemented — Updated 2026-03-11
**Date:** 2026-02-10

**Context:** LLM capabilities needed for summaries and future thermal analysis.
**Decision:** Ollama locally on Pi. Model: llama3.2:1b-instruct-q4_K_M
**Model Evaluation:**
| Model | Actual RAM | Decision |
|-------|-----------|----------|
| phi3:mini | 3.6GB | ❌ Too heavy |
| Gemma:2b | 1.2GB | ❌ 4 min response |
| TinyLlama | ~800MB | ❌ Hallucinated |
| Llama 3.2 1B instruct-q4_K_M | ~600MB | ✅ Selected |

**Key Finding:** Advertised size ≠ actual RAM. Always measure.
**Ollama Config:** OLLAMA_HOST=0.0.0.0 — must bind to all interfaces for Docker access.
**Consequences:** Data sovereignty confirmed. Phase 4 full models on cloud.

---

## [ADR-006] Modular Utility Architecture
**Status:** Resolved → superseded by ADR-012
**Date:** 2026-02-10

**Context:** Monolithic scripts difficult to scale.
**Resolution:** Implemented as modular read/validate/write functions. See ADR-012.

---

## [ADR-007] Data Quality Layer
**Status:** Accepted / Implemented → evolved via ADR-022
**Date:** 2026-02-10

**Evolution:**
```
Phase 1a → validate_data() range checks in Silver
Phase 1b → hardcoded record count thresholds in Gold
Phase 1c → percentage-based completeness (ADR-022) ✅
Phase 2  → Soda Core SQL validation (Week 3)
Phase 3  → Great Expectations documentation (Week 4)
```
**Core principle:** Bad data never reaches Gold.

---

## [ADR-008] Source Fidelity and Micro-Batch Ingestion
**Status:** Accepted / Implemented
**Date:** 2026-02-28

**Decision:** 5-minute micro-batch. Source filenames preserved exactly.
**Rationale:** Source fidelity prioritises auditability over convenience. Streaming deferred until MVP gate criteria met.

---

## [ADR-009] Dynamic Schema Inference for Bronze Loading
**Status:** Accepted / Implemented
**Date:** 2026-03-01

**Decision:** Tables created dynamically from JSON structure. JSONs loaded as VARCHAR — typed at Silver.
**Consequences:** Bronze stores VARCHAR. Silver responsible for type casting.

---

## [ADR-010] Three-Layer Semantic Boundaries
**Status:** Accepted / Implemented
**Date:** 2026-03-03

**Decision:**
```
Bronze → raw at source frequency
Silver → validated, schema-conformed
Gold   → aggregated for analytics and AI
AI     → operates exclusively on Gold
```

---

## [ADR-011] Layered Directory Structure
**Status:** Accepted / Implemented
**Date:** 2026-03-06

**Decision:**
```
data/bronze/landing_zone/processed/
data/bronze/raw_source.db
data/silver/master_data.db
data/gold/analytics.db
data/reference/reference.db
data/ops/ops.db
```
**Scale trigger:** >100K rows/day or query latency >1s.

---

## [ADR-012] Modular Functions Over True Microservices (Phase 1)
**Status:** Accepted / Implemented → Docker Phase 2
**Date:** 2026-03-07

**Decision:** Independent modular functions (read/validate/write) within single scripts.
**Phase 2 Container Map:**
```
land-bronze      → Bronze ingestion
transform-silver → Silver transform
transform-gold   → Gold aggregation
ai-summary       → AI summary
```
**Consequences:** Zero rewrite for Docker migration.

---

## [ADR-013] Data Contract Pattern for Schema Drift
**Status:** Accepted / Implemented
**Date:** 2026-03-07

**Decision:** contracts.py as centralised field alias registry.
**Contracts:**
```python
ZIGBEE_CONTRACT = {"temperature": ["temperature","temp","tmp"], ...}
KNMI_CONTRACT   = {"temperature": ["ta"], "humidity": ["rh"], ...}
```
**Consequences:** All new sources need contract first. contracts.py is governed.

---

## [ADR-014] Bath Room Excluded From Silver
**Status:** Accepted / Implemented
**Date:** 2026-03-07

**Decision:** Exclude zigbee2mqtt/Bath T&H at Bronze read stage.
**Rationale:** Bath microclimate introduces noise into ML correlation models.

---

## [ADR-015] Indoor Humidity Ceiling at 85%
**Status:** Accepted / Implemented
**Date:** 2026-03-07

**Decision:** Valid range 25-85%. Above 85% → rh_out_of_range flag.
**Rationale:** Flag and preserve, never drop.

---

## [ADR-016] Full Rollback on Silver Transform Failure
**Status:** Accepted / Implemented
**Date:** 2026-03-07

**Decision:** Full rollback on failure. Watermark updated only after complete batch.
**Consequences:** Phase 2: Dead Letter Queue for record-level isolation.

---

## [ADR-017] Pinned Requirements File
**Status:** Accepted → superseded by Docker Phase 2
**Date:** 2026-03-08

**Context:** System upgrades broke venv silently. xarray, duckdb lost.
**Decision:** pip freeze output in requirements.txt.
**Recovery:** pip install -r requirements.txt

---

## [ADR-018] NAS Mount Permanence via fstab UUID
**Status:** Accepted / Implemented
**Date:** 2026-03-08

**Decision:** UUID-based fstab mount with nofail.
**Safe Rule:** Any change to /mnt/data → check fstab and config.py first.

---

## [ADR-019] Iceberg Migration Strategy
**Status:** Accepted — Backlog Phase 3
**Date:** 2026-03-09

**Sequence:** DuckDB → Parquet → Iceberg
**Rationale:** Iceberg portable across AWS/Azure/GCP. No schema changes between phases.

---

## [ADR-020] Orchestrator Selection Strategy
**Status:** Accepted / Implemented — Updated 2026-03-18
**Date:** 2026-03-09

**Decision:**
```
Phase 2 (Pi)    → Prefect (~300MB actual RAM measured)
Phase 3 (Cloud) → Airflow (enterprise standard)
```

**Prefect Evaluation (2026-03-18):**
```
Dagster evaluated → rejected
Reason: 5-15% Dutch market JDs vs Prefect 25-35%
        Asset model does not transfer to Airflow cleanly
        Prefect → Airflow mental model preserved

RAM Measured:
Server only:        ~300MB ✅
Full chain peak:    ~1.4GB (xarray is heavy component)
Available at peak:  4.0GB → no swap ✅
Decision rule met:  < 400MB server overhead ✅
```

**Mental Model Transfer:**
```
Prefect Flow  → Airflow DAG
@flow         → DAG()
@task         → PythonOperator
wait_for      → depends_on
```

**ARM64:** python:3.11-slim confirmed multi-arch. No platform flag needed on Pi.
**DuckDB locking:** Ephemeral sequential design sufficient. Health checks not needed.

**Orchestration Principles To Own:**
```
1. Dependency graph    → wait_for chain
2. Retry logic         → retries=2, retry_delay_seconds=30
3. Backfill            → watermark pattern
4. Observability       → pipeline_runs table
5. Lineage             → OpenLineage Govern.2
```

---

## [ADR-021] Privacy & EU Compliance Strategy
**Status:** Accepted — Stage 1 Implemented, Stage 2 Backlog
**Date:** 2026-03-10

**Data Classification:**
| Layer | Classification |
|-------|---------------|
| bronze/ | INTERNAL |
| silver/ | INTERNAL |
| gold/ | PUBLIC |
| ops/ | INTERNAL |
| logs/ | INTERNAL |

**EU AI Act Mapping:**
| Article | Sentinel Implementation |
|---------|------------------------|
| 9 — Risk management | DQ thresholds |
| 10 — Data governance | Medallion architecture |
| 13 — Transparency | AI summary output |
| 14 — Human oversight | Daily report reviewed |
| 15 — Accuracy | Gold 100% valid |

---

## [ADR-022] Percentage-Based DQ Completeness
**Status:** Accepted / Implemented
**Date:** 2026-03-10

**Decision:**
```python
KNMI_COMPLETENESS_MIN   = 0.84
ZIGBEE_COMPLETENESS_MIN = 0.94
```
**Rationale:** Self-calibrating. Streaming-ready. IoT devices built for reliability — 94% threshold enforced strictly.

---

## [ADR-023] Read-Only Connection Strategy
**Status:** Accepted / Implemented
**Date:** 2026-03-10

**Decision:**
```python
connect_to_db()          → pipeline writes only
connect_to_db_readonly() → AI scripts, queries, reporting
```

---

## [ADR-024] Gold Clean Slate Policy
**Status:** Accepted / Implemented
**Date:** 2026-03-10

**Decision:** Drop and rebuild Gold when processing logic changes.
**Rule:** Bad data → Silver. Incorrect processing → fix logic, rebuild Gold.

---

## [ADR-025] Observability and Platform Metrics
**Status:** Accepted — Partially Implemented
**Date:** 2026-03-11

**Phases:**
```
Phase 1 → AI reads cron.log (approximate) ✅
Phase 2 → pipeline_runs table in ops.db (exact)
Phase 3 → Prefect built-in observability
Phase 4 → Streamlit dashboard
```

---

## [ADR-026] Dual Gold Layer
**Status:** Accepted — Partially Implemented
**Date:** 2026-03-11

**Decision:**
```
gold_weather          → reporting rollups (live ✅)
gold_weather_features → ML feature store (Phase 2)
```

---

## [ADR-027] AI Model Selection
**Status:** Accepted / Implemented
**Date:** 2026-03-11

**Selected:** llama3.2:1b-instruct-q4_K_M (~600MB actual)
**Backup:** qwen2:0.5b (~450MB)
**Key finding:** Advertised ≠ actual RAM. Always measure.

---

## [ADR-028] Two-Layer AI Design
**Status:** Accepted / Implemented
**Date:** 2026-03-11

**Decision:**
```
Layer 1 → Python: exact metrics from Gold + logs
Layer 2 → LLM: narrative + pattern recognition
```
**Phase 2:** pipeline.jsonl feeds exact metrics → eliminates hallucination.

---

## [ADR-029] FileLock Concurrency Control
**Status:** Accepted / Implemented → superseded by Prefect
**Date:** 2026-03-11

**Decision:** OS-level atomic lock. timeout=0 → skip if locked.
**Superseded:** Prefect wait_for chain prevents overlap. FileLock kept until Prefect fully replaces cron.

---

## [ADR-030] DQ Evolution Strategy
**Status:** Accepted — Backlog
**Date:** 2026-03-12

**Sequence:**
```
Phase 1 → Custom thresholds ✅
Phase 2 → Soda Core (Week 3, after Docker stable)
Phase 3 → Great Expectations (Week 4, optional)
```
**Core principle:** Framework supports governance story, not the other way around.

---

## [ADR-031] Schema Validation Evolution
**Status:** Accepted — Backlog
**Date:** 2026-03-13

**Sequence:**
```
Week 2 → contracts.json + schema_versions table in ops.db
Week 3 → Pydantic validators in land-bronze
Week 3 → Prefect pre-condition tasks
```
**Blocked by:** Docker Phase 2 stable.

---

## [ADR-032] Docker Containerisation Strategy
**Status:** Accepted / Implemented
**Date:** 2026-03-17

**Decision:** 4 ephemeral services. Full Pi paths as volumes (not aliases).
**Volume Strategy:**
```
Left = real Pi path = right = same path inside container
config.py paths preserved — zero script rewrites
```
**Ollama Config:**
```
OLLAMA_HOST=0.0.0.0 → binds to all interfaces
host.docker.internal → container reaches host Ollama
OLLAMA_URL → env var, defaults to localhost for cron
```
**ARM64:** python:3.11-slim confirmed. No platform flag needed locally.
**DuckDB locking:** depends_on sequential chain sufficient.
**User:** Docker runs as root → permission conflicts with Pi user. Fix: user: "1000:1000" in docker-compose.yml (backlog).
**CI/CD:** Platform flag deferred to GitHub Actions.

---

## [ADR-033] OpenLineage Edge Lakehouse Lineage
**Status:** Accepted — Govern.2 Backlog
**Date:** 2026-03-18

**Context:** TPM must demonstrate lineage ownership. EU AI Act Article 13 requires AI transparency.
**Decision:** Three-tool lineage stack:
```
SQLLineage    → column-level SQL parsing
OpenLineage   → CNCF standard event format
Marquez       → lightweight collector + UI (Docker native)
```
**RAM budget:** 320MB total confirmed.
**Blocked by:** Prefect stable (Govern.1 complete).

Update
Marquez rejected on ARM64 constraint. Official image not published for linux/arm64. JVM build overhead disproportionate to Pi hardware budget. Lineage capability preserved via OpenLineage Python client. Sink changed from Marquez (Postgres) to lineage_events table in ops.db — schema enforced, JOINable with watermarks and freshness_log, queryable via DuckDB. JSONL sink explicitly rejected — ops.db is the single governance store. Marquez deferred to Phase 3 cloud deployment where ARM64 constraint does not apply.

---

## [ADR-034] Data Freshness SLAs
**Status:** Accepted — Govern.2 Backlog
Update status: implementation Week 3
**Date:** 2026-03-18

**SLA Thresholds:**
```
KNMI Bronze:   < 15 mins from latest file
Zigbee Bronze: < 15 mins from latest reading
Silver:        < 20 mins from source
Gold:          < 70 mins from source
```
**Implementation:** freshness_check() Prefect task. freshness_log table in ops.db.

---

## [ADR-035] RAG Vector Store — ChromaDB Edge
**Status:** Accepted — Phase 3 Scale
**Date:** 2026-03-18

**Decision:** ChromaDB ARM64, sentence-transformers, RAGAS evaluation.
**Use case boundary:**
```
RAG → pattern-based NL queries
SQL → exact metric retrieval
```
**Target:** 92% context precision (measured, not assumed).
**Blocked by:** Govern.2 complete.

---

## Backlog ADRs
```
ADR-036 → Weather extremes prediction (Phase 3)
ADR-037 → Streamlit dashboard architecture (Phase 4)
```

ADR-038 — Pipeline Telemetry Schema Contract
Status: Accepted / Implemented
Date: 2026-03-22
Context: Pipeline stages need structured metrics for AI summary consumption. Generic fields like records_in/records_out caused ambiguity — gold layer produces more rows than it consumes by design (cartesian join), which would trigger false LLM anomalies.
Decision: Per-stage TypedDict schemas defined in metrics_contract.py. Each stage imports its own contract. Logger accepts metrics: dict — schema enforced at call site.
Rationale: Schema drift caught at code review not runtime. LLM receives unambiguous named fields per stage. Separates telemetry contracts from source field contracts in contract.py.
Consequences: Zero schema drift across 8 pipeline stages. Enterprise evolution path: TypedDict → versioned package → DataHub/Atlan registry.

ADR-039 — LLM Prompt Encodes Relationships Not Values
Status: Accepted / Implemented
Date: 2026-03-22
Context: Early prompt design hardcoded expected gold_rows = 8. Adding a third KNMI station would silently break the prompt without any code change — a hidden contract violation.
Decision: Prompts encode relationship rules not expected values. Rule: gold_rows_written MUST equal knmi_rows_in × zigbee_rows_in. Values come from JSONL at runtime.
Rationale: Prompt remains valid regardless of sensor count changes. LLM detects anomalies by applying the rule to actual data — not by comparing against hardcoded expectations.
Consequences: Zero hardcoded expectations in prompts. Generalises to any pipeline topology change automatically.

ADR-040 — Bronze Raw-As-Is Principle
Status: Accepted / Implemented
Date: 2026-03-22
Context: KNMI API returns data for multiple stations in one file. Question arose whether to filter by station at collection or bronze load time.
Decision: Bronze accepts raw data exactly as received from source. No filtering, no transformation, no validation at bronze layer. Station filtering belongs in Silver only.
Rationale: Bronze is a faithful landing zone. Its job is faithfulness to source not cleanliness. Silver owns all transformation logic. Keeps medallion layer responsibilities clean and non-overlapping.
Consequences: Bronze is always replayable from source. Any reprocessing logic change requires only Silver changes — Bronze is never touched.

ADR-041 — Structured Logging Replaces cron.log
Status: Accepted / Implemented
Date: 2026-03-22
Context: Phase 1 AI summary hallucinations traced to unstructured cron.log input — verbose, noisy, 10-20 lines unparseable by a 1B parameter model. Root cause was input quality not model capability.
Decision: pipeline.jsonl replaces cron.log as primary pipeline observability artifact. One JSON line per stage per run. JSONL_RUNS_TO_READ=5, JSONL_LINES_PER_RUN=8 — reads last 40 lines (~10KB).
Rationale: AI summary has ground truth metrics. Hallucination root cause eliminated at source. JSONL is append-only, lightweight (~250 bytes/line), and trivially queryable. cron.log deprecated — removal in Govern.2.
Consequences: Zero AI hallucinations from logging input. Structured observability enables future Soda Core and OpenLineage integration in Govern.2.

ADR-042: CI/CD Lint Enforcement via GitHub Actions - flake8 + GitHub Actions as Code Quality Gate
Status: Implemented
Date: 2026-03-23

Context:
  Duplicate function definition in collect_knmi caused
  silent wrong behaviour in Govern.1. No automated check
  existed to catch this class of error.

Decision:
  GitHub Actions workflow triggers flake8 on every push
  to feature/** and main. max-line-length=100.
  temp_and_scratch excluded. Zero tolerance on F-class
  errors (undefined names, unused imports).

Consequences:
  + Silent bugs caught before merge
  + CI caught flow_run F821 that local env missed
  + Enterprise engineering practice on portfolio project
  + Every commit is now provably clean

Evidence: d1c616b — green CI in 13s

# ADR-043: NAS Failover Dual-Write Strategy

**Status:** Accepted — Backlog (Govern.2 Week 2)
          Update: deferred — Iceberg MVCC supersedes
          staging/production swap not needed
**Date:** 2026-03-26

## Context
NAS drive (sda1/sdb1) disconnected mid-session on 2026-03-23.
Prefect server died due to SQLite lock on prefect.db stored
on NAS. Pipeline data collection stopped silently for 3.5hrs.
No alert. No failover. Single point of failure confirmed.

## Decision
Dual-write pipeline.jsonl and DuckDB databases to:
- Primary:   /mnt/data/sentinel-pi/ (NAS)
- Secondary: /home/kaushik/sentinel-pi/data-failover/ (Pi SD)

Cron healthcheck every 5 mins:
If /mnt/data unmounted → symlink failover path → log alert.

## Rationale
Pi SD card (mmcblk0, 235GB) has sufficient headroom.
Ephemeral containers read latest timestamp via watermark —
zero pipeline break on failover activation.
NAS is convenience not necessity for pipeline operation.

## Consequences
+ Pipeline survives NAS disconnect automatically
+ No data loss on drive failure
+ Alert logged for human review
- Dual-write adds minor I/O overhead (acceptable)

## Implementation
Week 2.

# ADR-044: Cron Scheduling + Prefect Execution

**Status:** Accepted / Implemented
          pattern implemented
          cron schedules, Prefect executes
**Date:** 2026-03-26

## Context
Prefect serve() managing 4 concurrent high-frequency
deployments (6min, 10min, 10min, daily) caused scheduler
starvation on Pi 8GB. last_polled froze. Flows stopped
firing silently. AI summary continued (hourly) but
collection flows dead for 3.5+ hours on two occasions.

Root cause: serve() scheduler loop starved under
concurrent schedule pressure on constrained hardware.

## Decision
Separate scheduling from execution:
- Cron: triggers deployments on schedule (4 entries)
- Prefect: executes flows, handles retry, observability, UI

serve() removed from pipeline_flow.py.
anchor_date removed — not supported in Prefect 3.6.22.

## Cron Schedule
*/10  collect-knmi    (KNMI publish cadence)
*/6   collect-zigbee  (MQTT 5-min window + 1-min gap)
*/10  load-transform  (watermark-driven, safe overlap)
08:30 ai-summary      (daily digest)

## Rationale
Cron has scheduled Linux jobs reliably for 50 years.
Prefect's value is execution (retry, UI, observability)
not scheduling on constrained hardware.
Same pattern as enterprise: Airflow DAGs triggered by
external schedulers (AWS EventBridge, GCP Cloud Scheduler).

## Consequences
+ Zero scheduler starvation — cron never freezes
+ Prefect UI still shows all flow runs + retry logic
+ Enterprise pattern preserved and transferable
+ Separation of concerns documented and defensible
- Manual crontab management (mitigated by docs/backlog.md)

## Evidence
pipeline.jsonl + cron.log both updating cleanly post-fix.
Commit: feature/govern-2

# ADR-045 — dbt Integration Strategy
Status: Accepted / Implemented
Date: 2026-04-02

Context: Pipeline validation logic embedded inside Python 
transform scripts. No independent test layer. 
Silver/Gold quality assertions coupled to pipeline code — 
cannot be run independently or reported separately.

Decision: dbt-core + dbt-duckdb as transformation 
test layer. Models wrap existing Silver/Gold SQL. 
Tests defined in schema.yml — independent of 
pipeline execution. Prefect remains orchestrator — 
dbt runs as one task inside pipeline.

Rationale: 
- Decouples validation from transformation code
- Tests run independently of pipeline (dbt test)
- Dutch market JD standard — dbt in 60%+ data roles
- Enterprise path: local dbt → dbt Cloud (Phase 3)
- Zero rewrite — existing Silver SQL becomes dbt models

Consequences:
- sentinel_dbt/ folder under project root
- profiles.yml at ~/.dbt/ — not in repo (gitignore)
- Silver materialised as table — physical artifact per 
  medallion principle
- BL-011: dbt test task added to Prefect pipeline (Phase 3)

**ADR-046 draft:**
ADR-046 — Soda Core Independent Validation Layer
Status: Accepted / Implemented
Date: 2026-04-03

Decision: Soda Core DuckDB scans Silver table 
independently of pipeline execution.
Thresholds mirror pipeline config (KNMI 84%, Zigbee 94%).
FAIL on KNMI temp range confirms 3 out-of-range rows — 
correct behaviour, pipeline preserves them with is_valid=False.

Rationale: dbt tests transformation output at build time.
Soda Core scans live table at any time independently.
Two systems agreeing on the same bad rows = 
governance story is provable.

**ADR-047 draft:**
ADR-047 — OpenLineage + Marquez Lineage Stack
Status: Accepted / Implemented
Date: TBD

Context: EU AI Act Article 13 requires AI transparency
and provenance. TPM CV requires provable lineage
ownership. Pi RAM constraint (HA baseline 1.3-2.5GB)
prevents always-on Marquez.

Decision:
- Marquez on-demand via docker-compose.marquez.yml
  API + Postgres only — no UI in production
- OpenLineage Python client in container scripts
  not pipeline_flow.py — event tied to producing stage
- Baseline measured before and after Marquez deploy
  Numbers recorded for CV and ADR evidence

Constraints (from Arch Guru):
- HA + addons: 1.3-2.5GB baseline
- Total active cap: 5-6GB (2-3GB headroom for HA)
- Marquez must not exceed 1GB additional RAM

Consequences:
- Lineage emission non-blocking — fails silently
- Pipeline never blocked by lineage failure
- Clean audit trail: Bronze → Silver → Gold provable
- EU AI Act Article 13 compliance statement enabled

**ADR-048 draft:**
ADR-048 — Staging/Production DB Swap Pattern
Status: DEFERRED
Reason: Iceberg MVCC supersedes staging/production 
        swap pattern entirely.
        Building now = throwaway work.
Date: 2026-04-06

Context: DuckDB file-level locking causes write-read 
contention between pipeline writes and Soda/Gold reads.
Current connect_to_db_readonly() insufficient — 
lock contention still occurs during heavy writes.

Decision (proposed):
- Silver: master_data_staging.db → master_data.db (swap)
- Gold: analytics_staging.db → analytics.db (swap)
- All reads (Soda, AI summary, Gold) from production only
- Swap is atomic OS rename — not a copy
- Watermark advances only after successful swap

Rationale:
- Atomic rename is OS-level operation — cannot partially fail
- Readers never see incomplete state
- Soda scan decoupled from pipeline write cycle
- Blue/green deployment pattern at DB file level

Consequences:
- config.py needs SILVER_STAGING_DB, GOLD_STAGING_DB constants
- connect_to_db() writes to staging
- swap_to_production() called after write + validation
- Watermark update moves inside swap transaction
- Soda scan schedule can run any time safely

### ADR-049 — OpenLineage + Marquez Lineage Stack
Status: Accepted / Partially Implemented
Update: Marquez ARM64 constraint confirmed
          JSONL emission pattern implemented
          Marquez deferred to Phase 3 cloud
Date: 2026-04-08

Context: EU AI Act Article 13 requires provenance.
Marquez evaluated as lineage collector + UI.

Decision:
- Marquez DEFERRED — no ARM64 image available
  exec format error confirmed on Pi ARM64
- OpenLineage Python client IMPLEMENTED
  Events emitted to JSONL file
  Lineage provable from structured file
- dbt-ol wrapper pattern adopted for dbt runs
  Captures dbt artifacts + emits OpenLineage metadata

Rationale:
- Lineage DATA is the compliance artifact
  not the visualisation tool
- JSONL lineage file queryable, auditable, CV-defensible
- Marquez revisited in Phase 3 when cloud deployment
  removes ARM64 constraint

Consequences:
- lineage/openlineage_events.jsonl as audit artifact
- dbt-ol wraps dbt run in pipeline
- Zero RAM overhead — no container needed

# ADR-050 — Pi-Margin Unified Platform
Status: Accepted
Date: 2026-04-08
          New ADR to file:
          Two business units, shared medallion
          Two ChromaDB collections
          ENTSO-E + CBS NL data sources

# ADR-051 — dbt Certification Gate Between Silver and Gold 
Status: New
Context: dbt Silver validation models produce weather_silver_validated which was disconnected from Gold consumption. Gold was reading from weather_silver directly, bypassing dbt certification. Two scheduling concerns were conflated — raw ingestion (10 min) and analytical certification (hourly).
Decision: Three-tier scheduling separation.
Every 10 min → Bronze → weather_silver (Python)
Every hour   → weather_silver → weather_silver_validated (dbt)
Every hour   → weather_silver_validated → gold_weather (Python)
Daily 08:30  → gold_weather → ai_summary
Gold reads exclusively from weather_silver_validated. Single Gold table. Single source of truth.
Rationale: Gold must be correct before it is fresh. Hourly Gold sufficient for current analytical use case. Architecture is streaming-ready — Phase 3 Zigbee streaming feeds the same weather_silver table. dbt cadence adjusts per platform capability without Gold schema changes. Two Gold tables explicitly rejected — split truth breaks consumer trust.
Phase 3 Direction: Zigbee moves to streaming. Silver Zigbee near real-time. dbt + Gold sub-hourly on Databricks/Snowflake when platform migrates. Pi architecture does not block this transition.
Consequences: Gold freshness moves from near-real-time to hourly. Acceptable for home environment analytics and predictive modelling. dbt requires hourly cron entry. Gold Prefect flow separated from 10-minute collection flow.

# ADR-052 — lineage_events Schema in ops.db
Status: New
Context: Gate 3 originally designed to emit OpenLineage events to lineage_events.jsonl. JSONL rejected — cannot JOIN with watermarks or freshness_log, no schema enforcement, requires parsing on every query.
Decision: OpenLineage events written to lineage_events table in ops.db.
sqlCREATE TABLE IF NOT EXISTS lineage_events (
    event_time        TIMESTAMP,
    run_id            VARCHAR,
    job_name          VARCHAR,
    event_type        VARCHAR,
    input_dataset     VARCHAR,
    output_dataset    VARCHAR,
    input_location    VARCHAR,
    output_location   VARCHAR,
    row_count         INTEGER,
    processed_at      TIMESTAMP
)
Six emit points covering both raw sources:
knmi_raw → weather_silver → weather_silver_validated → gold_weather
zigbee_raw → weather_silver → weather_silver_validated → gold_weather
Rationale: ops.db is the single governance database. Lineage JOINable with watermarks and freshness_log. Full provenance query derivable in SQL. EU AI Act Article 13 compliance statement derivable from single query across ops.db tables.
Consequences: OpenLineage Python client used as emission standard. DuckDB ops.db replaces Marquez as lineage store. Stronger story than Marquez on Pi — governed schema, no JVM, no additional RAM overhead.