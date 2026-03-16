# 📔 Architecture Decision Records (ADR): Sentinel-Pi

This repository uses ADRs to document significant architectural and
data governance decisions.

**Format:** Context → Decision → Rationale → Consequences
**Rule:** ADR numbering is chronological and immutable.
New decisions never modify old ADRs — they supersede them.

---

## [ADR-001] Medallion Storage Pattern
**Status:** Accepted / Implemented
**Date:** 2026-02-09

**Context:**
Need a structured way to manage raw data vs processed data.

**Decision:**
Implement a Bronze/Silver/Gold medallion architecture.

**Rationale:**
Storing raw API responses in `data/bronze` allows re-processing
without re-calling the API if business logic changes.

**Consequences:**
- Requires extra storage for raw files
- Ensures 100% data recoverability
- Each layer applies stricter governance than the previous

---

## [ADR-002] Schema Evolution — Humidity Field Added
**Status:** Accepted / Implemented
**Date:** 2026-02-09

**Context:**
Requirement change to support broader climate analytics.

**Decision:**
Add humidity to the Silver table schema.

**Rationale:**
DuckDB allows schema evolution without dropping and recreating
tables — preserving historical temperature-only rows.

**Consequences:**
- Historical rows without humidity have NULL in humidity column
- No data loss on schema change

---

## [ADR-003] Standardised Virtual Environment
**Status:** Resolved → superseded by Docker Phase 2
**Date:** 2026-02-07

**Context:**
Legacy `direnv` configurations caused path conflicts during
storage migration.

**Decision:**
Standardise on a local `.venv` for portability.

**Rationale:**
Simplifies automation scripts (cron/systemd) by providing a
single, predictable path to the Python interpreter.

**Consequences:**
- `.venv` path locked: `/mnt/data/sentinel-pi/.venv`
- Recovery: `pip install -r requirements.txt`
- Docker Phase 2 supersedes — containers carry own dependencies

---

## [ADR-004] Automated Ingestion via Crontab
**Status:** Accepted / Implemented — Updated 2026-03-09
**Date:** 2026-02-09
**Updated:** 2026-03-09

**Context:**
Pipeline requires scheduled execution. Originally designed for
hourly ingestion. Updated when Gold DQ exposed insufficient
KNMI reading counts per hour.

**Decision:**
Three cron jobs via `sudo crontab`:
```bash
58 * * * *   → venv health check (review — may be removed Phase 2)
*/10 * * * * → pipeline ingestion every 10 minutes
30 8 * * *   → AI daily summary at 08:30
```

**Frequency Change Rationale:**
- KNMI publishes 6 files/hour — one every 10 minutes
- Hourly cron captured only 1 file = 2 rows/hour
- Gold DQ threshold required ≥ 10 KNMI rows/hour
- All Gold rows invalid at hourly frequency → root cause fixed

**Rationale:**
- 10-minute frequency captures all KNMI files
- Cron stability proven before frequency increase
- Overlap risk managed by FileLock (ADR-022)

**Consequences:**
- 6x more Bronze KNMI rows per hour
- Pipeline runtime ~6 mins, interval 10 mins — FileLock required
- Phase 2: Prefect replaces cron entirely (ADR-016)

---

## [ADR-005] Local AI via Ollama
**Status:** Accepted / Implemented — Updated 2026-03-11
**Date:** 2026-02-10
**Updated:** 2026-03-11

**Context:**
Need LLM capabilities for operational summaries and future
thermal efficiency analysis. Must run locally on Pi for
data sovereignty.

**Decision:**
Deploy Ollama locally on Raspberry Pi.
Model selected: `llama3.2:1b-instruct-q4_K_M`

**Model Evaluation (Actual RAM Footprint):**
| Model | Advertised | Actual RAM | Decision |
|-------|-----------|------------|----------|
| phi3:mini | 2.2GB | 3.6GB | ❌ Rejected — too heavy |
| Gemma:2b | 1.7GB | 1.2GB | ❌ Rejected — 4 min response |
| TinyLlama | 636MB | ~800MB | ❌ Rejected — hallucinated |
| Llama 3.2 1B instruct-q4_K_M | 807MB | ~600MB | ✅ Selected |

**Key Finding:**
Advertised model size ≠ actual RAM under load.
Always measure actual footprint before committing.

**Rationale:**
- Data sovereignty — no data leaves home network
- Avoids recurring API costs
- Llama 3.2 1B instruct: <10s response, accurate, 600MB actual
- 128K context window — future ML analytics ready
- Meta pedigree — Dutch enterprise standard

**Consequences:**
- Daily summary runtime: ~3-4 minutes for full report
- Phase 4 full models reserved for cloud deployment
- Backup model: Qwen2-0.5b (~450MB) if primary fails

---

## [ADR-006] Modular Utility Architecture
**Status:** Resolved → superseded by ADR-011
**Date:** 2026-02-10
**Resolved:** 2026-03-07

**Context:**
Monolithic scripts were becoming difficult to scale and test.

**Decision:**
Original plan: refactor into `src/utils/` and `src/processors/`.

**Resolution:**
Implemented as modular read/validate/write functions per source
rather than directory-based separation. See ADR-011 for full
pattern decision and Docker migration path.

---

## [ADR-007] Data Quality Layer
**Status:** Accepted / Implemented → evolved via ADR-018 and ADR-021
**Date:** 2026-02-10
**Updated:** 2026-03-11

**Context:**
Raw sensor data often contains spikes or nulls. Need a DQ
layer to prevent poisoning AI models with false data.

**Decision:**
Implement DQ validation at Silver and Gold layers.

**Evolution:**
```
Phase 1a → validate_data() range checks in Silver
Phase 1b → hardcoded record count thresholds in Gold (ADR-018)
Phase 1c → percentage-based completeness thresholds (ADR-021)
Phase 2  → Soda Core SQL validation layer (Week 3)
Phase 3  → Great Expectations documentation layer (Week 4)
```

**Current Implementation (ADR-021):**
```python
KNMI_COMPLETENESS_MIN   = 0.84  # 84% of hourly records valid
ZIGBEE_COMPLETENESS_MIN = 0.94  # 94% of hourly records valid
```

**Rationale:**
- Percentage-based DQ is streaming-ready and self-calibrating
- Soda Core adds enterprise validation layer — zero rewrite
- Great Expectations adds documentation — supports narrative
- Core principle: bad data never reaches Gold

**Consequences:**
- DQ evolution is incremental — no pipeline breaks
- Soda Core → Week 3 (after Docker stable)
- Great Expectations → Week 4 (optional, documentation focus)

---

## [ADR-008] Source Fidelity and Micro-Batch Ingestion
**Status:** Accepted / Implemented
**Date:** 2026-02-28

**Context:**
Zigbee data arrives via MQTT in real-time. Two options:
full streaming or micro-batch collection windows.

**Decision:**
5-minute micro-batch collection per cron run as MVP.
Source filenames preserved exactly as received.

**Rationale:**
- Micro-batching preserves event-level data with timestamps
- Source fidelity in filenames prioritises auditability over
  downstream tooling convenience
- Streaming deferred until schema, reliability, and governance
  are validated
- Hourly sampling vs full streaming is an explicit, controlled
  governance decision

**Consequences:**
- Streaming mode replaces micro-batch once MVP gate criteria met
- Source filename preservation enables full audit trail

---

## [ADR-009] Dynamic Schema Inference for Bronze Loading
**Status:** Accepted / Implemented
**Date:** 2026-03-01

**Context:**
Zigbee JSON files have variable structure across firmware versions.
Hardcoded schema breaks on new device types.

**Decision:**
Genericise `db_utils` to create tables dynamically based on
incoming data. Schema inferred from JSON structure.
JSONs loaded as VARCHAR initially — typed at Silver transform.

**Rationale:**
- Speed — no schema maintenance per device type
- Resilience — new device types load without code changes
- Type safety deferred to Silver where it belongs

**Consequences:**
- Bronze stores VARCHAR columns — not typed
- Silver transform responsible for type casting
- Processed files moved to `/processed` to avoid duplicates

---

## [ADR-010] Three-Layer Semantic Boundaries
**Status:** Accepted / Implemented
**Date:** 2026-03-03

**Context:**
Need clear contracts between pipeline layers to prevent
semantic confusion and ensure AI consumes stable data.

**Decision:**
```
Bronze → raw observations at source frequency
Silver → validated, schema-conformed at atomic granularity
Gold   → aggregated to hourly windows for analytics and AI
AI     → operates exclusively on Gold layer
```

**Rationale:**
- Each layer has a single, clear purpose
- AI on Gold ensures semantic stability and cost efficiency
- Gold aggregation isolates AI from raw data volatility

**Consequences:**
- AI scripts must never read Silver or Bronze directly
- Gold schema changes require ADR review

---

## [ADR-011] Layered Directory Structure
**Status:** Accepted / Implemented
**Date:** 2026-03-06

**Context:**
Platform requires clear separation between raw ingestion,
transformed datasets, analytics outputs, and operational metadata.

**Decision:**
```
/sentinel-pi/data/
├── bronze/
│   ├── landing_zone/        # incoming raw files
│   │   └── processed/       # archived after ingestion
│   └── raw_source.db        # structured raw storage
├── silver/
│   └── master_data.db       # validated, standardised
├── gold/
│   └── analytics.db         # aggregated analytics
├── reference/
│   └── reference.db         # lookup tables, station metadata
└── ops/
    └── ops.db               # operational metadata
```

**ops.db tables:**
- `watermarks` — last processed timestamp per pipeline
- `pipeline_runs` — execution history (Phase 2)
- `dq_summary` — aggregated DQ metrics (Phase 2)

**Rationale:**
- Clear data lineage
- Operational observability
- Independent lifecycle management per dataset

**Consequences:**
- All paths defined in `config.py` — single source of truth
- Scale trigger: >100K rows/day or query latency >1s
- Future: Parquet partitioned by date, Iceberg versioning

---

## [ADR-012] Modular Functions Over True Microservices (Phase 1)
**Status:** Accepted / Implemented → Docker Phase 2
**Date:** 2026-03-07

**Context:**
True microservices require independent processes, IPC, and
orchestration infrastructure. On Pi with DuckDB, Ollama,
Zigbee MQTT, and cron — overhead is premature.

**Decision:**
Build independent modular functions (read, validate, write)
within single Python scripts. Each function has single
responsibility and is independently testable.

**Rationale:**
- Modular functions are correct building blocks for microservices
- Docker Phase 2 is the natural containerisation point
- No rewrite required for migration
- Building true microservices in raw Python before Docker is
  premature complexity

**Phase 2 Container Map:**
```
land-bronze      → Bronze ingestion container
transform-silver → Silver transform container
transform-gold   → Gold aggregation container
ai-summary       → AI summary container
```

**Consequences:**
- Current code requires zero rewrite for Docker migration
- Each module already has single responsibility

---

## [ADR-013] Data Contract Pattern for Schema Drift
**Status:** Accepted / Implemented
**Date:** 2026-03-07

**Context:**
Zigbee sensors emit different field names across firmware versions.
Example: `temperature` vs `temp` vs `tmp`. Hardcoding field names
creates brittle code that breaks silently on schema drift.

**Decision:**
Introduce `contracts.py` as centralised field alias registry.
Silver transformation reads field values via `extract_by_contract()`
— never by hardcoded key name.

**Current Contracts:**
```python
ZIGBEE_CONTRACT = {
    "temperature": ["temperature", "temp", "tmp"],
    "humidity":    ["humidity", "hum", "rh"],
    "battery":     ["battery", "bat"],
}
KNMI_CONTRACT = {
    "temperature": ["ta"],
    "humidity":    ["rh"],
    "wind_speed":  ["ff"],
}
```

**Rationale:**
- New field alias → update `contracts.py` only
- Unknown alias → warning logged, silent data loss prevented
- Separation of concerns: `config.py` owns infrastructure,
  `contracts.py` owns data semantics

**Consequences:**
- All new sources must define a contract before Silver is built
- `contracts.py` is a governed file — changes require ADR review
- Week 4: pressure field added for weather extremes prediction

---

## [ADR-014] Bath Room Excluded From Silver
**Status:** Accepted / Implemented
**Date:** 2026-03-07

**Context:**
Sentinel-Pi purpose is correlating external weather with indoor
environment. Bath room humidity/temperature are internally driven
(shower, bath events) — not representative of passive weather
correlation.

**Decision:**
Exclude `zigbee2mqtt/Bath T&H` topic at Bronze read stage.
Filter: `topic NOT LIKE '%Bath%'`

**Rationale:**
- Bath microclimate introduces noise into ML correlation models
- Filtering at read stage is more efficient than validation stage
- Bath data preserved in Bronze — decision reversible

**Consequences:**
- Rooms included: hall, attic, bedroom1, bedroom2
- Bath analysis possible against Bronze only if needed

---

## [ADR-015] Indoor Humidity Ceiling at 85%
**Status:** Accepted / Implemented
**Date:** 2026-03-07

**Context:**
Netherlands indoor humidity above 85% indicates condensation,
sensor malfunction, or unusual events — not representative of
normal home living for weather correlation.

**Decision:**
Indoor humidity valid range: 25% to 85%.
Values above 85% flagged as `rh_out_of_range` in Silver `dq_flag`.

**Rationale:**
- 85% ceiling flags anomalies for AI investigation
- Governance principle: flag and preserve, never drop
- Aligns with Silver DQ philosophy

**Consequences:**
- Rows above 85% land in Silver with `is_valid = FALSE`
- Gold excludes invalid rows — anomalies do not pollute analytics

---

## [ADR-016] Full Rollback on Silver Transform Failure
**Status:** Accepted / Implemented
**Date:** 2026-03-07

**Context:**
Row-level failure mid-batch could result in partial Silver load.
Partial loads look valid but are incomplete.

**Decision:**
Full rollback on any transformation failure. Watermark only
updated after complete successful batch.

**Rationale:**
- Partial Silver load violates data integrity
- Full rollback preserves Silver integrity
- Acceptable tradeoff at current scale (<1K rows/hour)

**Consequences:**
- On failure — entire batch retried next run
- Small overlap risk mitigated by `INSERT OR IGNORE`
- Phase 2: Dead Letter Queue for record-level error isolation

---

## [ADR-017] Pinned Requirements File as Venv Safety Net
**Status:** Accepted / Implemented → superseded by Docker Phase 2
**Date:** 2026-03-08

**Context:**
System apt upgrades broke venv silently. `xarray` and `duckdb`
modules became unavailable. Pipeline failed for multiple hours.

**Incident:**
```
ModuleNotFoundError: No module named 'xarray'
ModuleNotFoundError: No module named 'duckdb'
```

**Decision:**
Replace unpinned `requirements.txt` with `pip freeze` output.
All transitive dependencies captured at exact versions.

**Recovery Command:**
```bash
/mnt/data/sentinel-pi/.venv/bin/python3 -m pip install \
    -r requirements.txt
```

**Consequences:**
- `requirements.txt` updated after every intentional upgrade
- Docker Phase 2 supersedes — containers isolate dependencies

---

## [ADR-018] NAS Mount Permanence via fstab UUID
**Status:** Accepted / Implemented
**Date:** 2026-03-08

**Context:**
Server operations changed NAS mount from `/mnt/data` to
`/media/m-m/c28c2621`. All pipeline scripts reference
`/mnt/data/sentinel-pi` via `config.py`. Mount change caused
silent path failures.

**Decision:**
Mount NAS permanently via `/etc/fstab` using UUID with `nofail`:
```
UUID=c28c2621-fe58-4591-8009-84983b3938bf /mnt/data ext4 defaults,nofail 0 2
```

**Rationale:**
- UUID-based mount survives device path changes
- `nofail` prevents Pi boot hang if NAS unavailable
- `/mnt/data` is a platform constant — must never change

**Safe Rule:**
> "If a change affects `/mnt/data` mount — stop and check
> fstab and `config.py` first."

**Consequences:**
- NAS replacement requires fstab UUID update
- Documented in `PI_INFRASTRUCTURE_CONSTRAINTS.md`

---

## [ADR-019] Iceberg Migration Strategy
**Status:** Accepted — Backlog (Phase 3)
**Date:** 2026-03-09

**Context:**
Enterprise standard requires modern table semantics — schema
evolution, time travel, ACID — without vendor lock-in.

**Decision:**
Migrate to Apache Iceberg in sequence:
```
Phase 1 → DuckDB tables (current) ✅
Phase 2 → Parquet files (export)
Phase 3 → Iceberg tables (migrate)
```

**Implementation Sequence:**
```sql
-- Step 1: Export DuckDB → Parquet
COPY (SELECT * FROM knmi_raw)
TO 'bronze/knmi_20260311.parquet';

-- Step 2: Create Iceberg from Parquet
CREATE TABLE iceberg_data.bronze_knmi
USING iceberg
LOCATION '/mnt/data/sentinel-pi/data/iceberg/bronze_knmi'
FROM read_parquet('bronze/knmi_*.parquet');

-- Step 3: Future writes → Iceberg directly
INSERT INTO iceberg_data.bronze_knmi VALUES (...);
```

**Rationale:**
- Iceberg skills portable across AWS/Azure/GCP
- Schema evolution without full rewrites
- Time-travel for ML experiments
- Vendor-agnostic before cloud commitment

**Consequences:**
- Parquet migration must complete before Iceberg begins
- No schema changes required between phases
- Blocked by: Phase 2 Docker stable

---

## [ADR-020] Orchestrator Selection Strategy
**Status:** Accepted — Planned Phase 2
**Date:** 2026-03-09

**Context:**
Cron is current orchestration. Growing pipeline complexity
requires retry logic, dependency management, observability.
Dutch market requires Airflow knowledge for €140k+ roles.

**Decision:**
```
Phase 2 (Pi)    → Prefect  (~120MB RAM, Python-first)
Phase 3 (Cloud) → Airflow  (enterprise standard)
```

**Mental Model Transfer:**
```
Prefect Flow     → Airflow DAG
@flow            → DAG()
@task            → PythonOperator
flow.deploy()    → scheduler + UI
```

**Rationale:**
- Prefect runs on constrained hardware
- Airflow in 80-85% of Dutch Data/AI PM roles
- Modular functions already Prefect-task ready — no rewrite

**Consequences:**
- Phase 2 Docker brings Prefect — replaces cron entirely
- Phase 3 Airflow transition requires no code rewrite

---

## [ADR-021] Privacy & EU Compliance Strategy
**Status:** Accepted — Stage 1 Implemented, Stage 2 Backlog
**Date:** 2026-03-10

**Context:**
Dutch Data/AI PM roles require GDPR and EU AI Act knowledge.
Current data: weather + IoT sensors — zero PII risk today.

**Decision:**
Two-stage implementation:

Stage 1 — Narrative (done):
- Data classification per layer documented
- GDPR principles mapped to architecture
- No code changes required

Stage 2 — Phase 2 implementation:
- `pii_guard.py` — PII screening Bronze→Silver
- Retention cleanup job (bronze_raw: 30 days)

**Data Classification:**
| Layer | Classification |
|-------|---------------|
| bronze/ | INTERNAL |
| silver/ | INTERNAL |
| gold/ | PUBLIC |
| ops/ | INTERNAL |
| logs/ | INTERNAL |

**GDPR 7 Principles Mapping:**
| Principle | Sentinel Implementation |
|-----------|------------------------|
| Lawfulness | Documented legal basis per table |
| Purpose Limitation | Table-level purpose in ADRs |
| Data Minimisation | PII screening (Phase 2) |
| Accuracy | Gold DQ thresholds enforced |
| Storage Limitation | 30-day retention (Phase 2) |
| Integrity | ACID writes + file permissions |
| Accountability | ADRs + full pipeline logging |

**EU AI Act Mapping (Articles 9-15):**
| Article | Sentinel Implementation |
|---------|------------------------|
| 9 — Risk management | DQ thresholds |
| 10 — Data governance | Medallion architecture |
| 13 — Transparency | AI summary output |
| 14 — Human oversight | Daily report reviewed |
| 15 — Accuracy | Gold 100% valid |

**Interview Answer:**
> "Sentinel implements GDPR-by-design and EU AI Act good
> practices — data classified per layer, DQ enforces accuracy,
> full audit trail in ops.db, AI output is transparent and
> human-reviewed."

---

## [ADR-022] Percentage-Based DQ Completeness for Gold Layer
**Status:** Accepted / Implemented — supersedes ADR-007 record counts
**Date:** 2026-03-10

**Context:**
Hardcoded record count thresholds brittle — every frequency
change requires manual update. Not streaming-ready.

**Decision:**
```python
knmi_completeness   = knmi_valid_count / knmi_total_count
zigbee_completeness = zigbee_valid_count / zigbee_total_count

KNMI_COMPLETENESS_MIN   = 0.84
ZIGBEE_COMPLETENESS_MIN = 0.94
```

**Rationale:**
> "IoT devices are built for reliability. Identify the cause
> rather than forgive the gap."

- Self-calibrating — adapts to any frequency
- Streaming-ready — percentage works regardless of volume
- Only thresholds in config — one place to update

**DQ Evolution Path:**
```
Phase 1 → Custom percentage thresholds (current) ✅
Phase 2 → Soda Core SQL validation layer (Week 3)
Phase 3 → Great Expectations documentation (Week 4)
```

**Consequences:**
- Gold 100% valid after implementation
- Phase 3 streaming: time-based windows replace percentage

---

## [ADR-023] Read-Only Connection Strategy
**Status:** Accepted / Implemented
**Date:** 2026-03-10

**Context:**
DuckDB single-writer lock. At 10-minute cron with ~6-minute
runtime — only 4-minute safe query window. AI script blocked
during pipeline runs.

**Decision:**
```python
def connect_to_db_readonly(db_path: str):
    return duckdb.connect(db_path, read_only=True)
```

**Usage Rule:**
```
connect_to_db()          → pipeline writes only
connect_to_db_readonly() → AI scripts, queries, reporting
```

**Consequences:**
- All AI scripts must use read-only connections
- Docker Phase 2 supersedes with proper connection pooling

---

## [ADR-024] Gold Clean Slate Policy
**Status:** Accepted / Implemented
**Date:** 2026-03-10

**Context:**
Gold accumulated 1410 invalid rows due to incorrect processing
logic — not bad data. Decision: fix in place or rebuild clean.

**Decision:**
Drop and rebuild Gold when processing logic changes.

> "Gold should always be clean — this was incorrect processing,
> not bad data."

**Rebuild Procedure:**
```bash
# 1. Drop Gold table
con.execute('DROP TABLE IF EXISTS gold_weather')
# 2. Reset watermark
con.execute("DELETE FROM watermarks WHERE source = 'gold_weather'")
# 3. Recreate schema
python3 src/create_silver_tables.py
# 4. Fix logic → rerun pipeline
```

**Rationale:**
- Bad data → stays in Silver, flagged, never dropped
- Incorrect processing → fix logic, rebuild Gold clean
- Corrupted Gold = corrupted model training

---

## [ADR-025] Observability and Platform Metrics Strategy
**Status:** Accepted — Partially Implemented
**Date:** 2026-03-11

**Context:**
Pipeline runs every 10 minutes. Silent failures and sensor
dropouts not visible without structured observability.

**Decision:**
Track per-run operational metrics:
| Metric | Source | Purpose |
|--------|--------|---------|
| pipeline_runtime | logs | Detect slowdowns |
| dq_valid_percentage | ops.db | Quality trends |
| rows_ingested | ops.db | Volume anomalies |
| cron_delay | logs | Scheduling drift |
| sensor_coverage | Silver | Room dropout |

**Implementation Phases:**
```
Phase 1 → AI reads cron.log (approximate) ✅
Phase 2 → pipeline_runs table in ops.db (exact)
Phase 3 → Prefect built-in observability
Phase 4 → Streamlit dashboard
```

---

## [ADR-026] Dual Gold Layer — Reporting + ML Feature Store
**Status:** Accepted — Partially Implemented
**Date:** 2026-03-11

**Context:**
Current `gold_weather` serves reporting rollups. ML consumers
need derived features, lag windows, binary indicators.

**Decision:**
```
gold_weather          → reporting rollups (live ✅)
gold_weather_features → ML feature store  (Week 2)
```

**gold_weather_features schema (Week 2):**
```sql
light_occupied    → temp < 18 AND humidity rising
cold_snap_prob    → NULL (Week 4 ML model)
temp_trend_7d     → LAG(temp,1) OVER (PARTITION BY location)
humidity_spike    → humidity > 70 AND rising
heat_snap_prob    → NULL (Week 4 ML model)
extreme_action    → PRE-HEAT / PRE-COOL / STANDBY
```

**Rationale:**
- Reporting consumers need pre-aggregated measures
- ML consumers need derived features + lag windows
- Clean separation of concerns
- Both migrate to Iceberg Phase 3

---

## [ADR-027] AI Model Selection — Constrained Pi Deployment
**Status:** Accepted / Implemented
**Date:** 2026-03-11

**Context:**
Pi 8GB has ~1.9GB available under full load. Multiple models
evaluated. Advertised size ≠ actual RAM under load.

**Model Evaluation:**
| Model | Advertised | Actual RAM | Time | Decision |
|-------|-----------|------------|------|----------|
| phi3:mini | 2.2GB | 3.6GB | timeout | ❌ |
| Gemma:2b | 1.7GB | 1.2GB | 4 mins | ❌ |
| TinyLlama | 636MB | ~800MB | 15-20s | ❌ hallucinated |
| Llama 3.2 1B instruct-q4_K_M | 807MB | ~600MB | <10s | ✅ |

**Decision:**
Primary: `llama3.2:1b-instruct-q4_K_M`
Backup: `qwen2:0.5b` (~450MB)

**Rationale:**
- instruct variant — fine-tuned for instruction following
- Q4_K_M — better quantization, Pi-optimised
- 128K context window — future analytics ready
- Meta pedigree — Dutch enterprise standard
- Data sovereignty — runs fully local

**Interview Answer:**
> "Evaluated four models against actual RAM footprint — not
> advertised specs. Selected Llama 3.2 1B instruct at 600MB
> actual. Production reliability over model size."

---

## [ADR-028] Two-Layer AI Design — Python + LLM
**Status:** Accepted / Implemented
**Date:** 2026-03-11

**Context:**
Daily AI summary requires both exact metrics and narrative
analysis. Using LLM for metric extraction risks hallucination.

**Decision:**
```
Layer 1 → Python: exact metrics from Gold + logs
Layer 2 → LLM:   narrative + pattern recognition
```

**Phase Evolution:**
```
Phase 1 → Python reads cron.log (approximate metrics)
           LLM narrates ✅
Phase 2 → Python reads pipeline.jsonl (exact metrics)
           LLM narrates with precise numbers
```

**Rationale:**
- Python is deterministic — exact counts never hallucinated
- LLM is probabilistic — narrative and patterns, not arithmetic
- Industry standard: Python extracts, AI narrates

**Consequences:**
- Phase 2 `pipeline.jsonl` structured logging fixes
  performance hallucinations in Phase 1 reports
- `log_utils.py` skeleton created — Phase 2 migration

---

## [ADR-029] FileLock Concurrency Control
**Status:** Accepted / Implemented
**Date:** 2026-03-11

**Context:**
Pipeline runtime ~6 minutes. Cron interval 10 minutes.
4-minute overlap risk. Concurrent runs would write to same
DuckDB simultaneously — data corruption risk.

**Decision:**
OS-level atomic lock via `filelock` library:
```python
with FileLock(LOCK_FILE, timeout=0):
    write_lock_meta()
    main()
    clear_lock_meta()
```

Lock metadata written per run:
```json
{"pid": 14523, "acquired_at": "2026-03-11T09:00:02Z",
 "script": "ingest_data.py"}
```

**Why filelock over touch file:**
- Touch file: Python-level check — race condition possible
- filelock: OS atomic lock — race condition impossible

**Rationale:**
- `timeout=0` — skip run if locked, no queue buildup
- Lock metadata parseable by AI summary for observability
- Phase 2 Prefect supersedes — git-aware, no overlap risk

**Consequences:**
- Skipped runs logged as WARNING — parseable
- Lock files added to `.gitignore` (backlog)
- Prefect Phase 2 makes this redundant

---

## [ADR-030] DQ Evolution Strategy — Custom → Soda Core → GX
**Status:** Accepted — Backlog
**Date:** 2026-03-12

**Context:**
Custom percentage-based DQ proven in production (100% Gold rows).
Dutch market (Booking.com/ING/Adyen) expects Soda Core and
Great Expectations familiarity. Need evolution path that
supports career narrative without replacing working system.

**Decision:**
```
Phase 1 → Custom contracts.py thresholds ✅ (live)
Phase 2 → Soda Core SQL validation (Week 3 — after Docker)
Phase 3 → Great Expectations documentation (Week 4 — optional)
```

**Soda Core Implementation (Week 3):**
```yaml
# soda.yml
checks for gold_weather:
  - row_count > 0
  - missing_count(temp) = 0
  - avg(temp) between -50 and 60
```

**Career Coach Framing:**
> "Framework integration supports governance story — not
> the other way around. Core principle: bad data never
> reaches Gold. The framework around it matures as the
> platform matures."

**Rationale:**
- 80% contracts.py → Soda/GX — zero rewrite
- Dual validation: Custom + Soda → confidence multiplier
- Great Expectations = documentation layer, not replacement
- Incremental evolution signals platform maturity thinking

**Consequences:**
- Soda Core blocked by: Docker Phase 2 stable
- Great Expectations optional — only if time permits
- Backlog note: keep lightweight, do not slow roadmap

---

## Backlog ADRs (To Be Written)

```
ADR-031 → Bi-directional weather extremes prediction
          Cold snap + heat snap capability (Week 4)
ADR-032 → EU AI Act compliance mapping
          Split from ADR-021 — dedicated AI governance ADR
```