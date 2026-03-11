# 📔 Architecture Decision Records (ADR): Sentinel-Pi

This repository uses ADRs to document significant architectural and data governance decisions.

Format: Context → Decision → Rationale → Consequences

ADR numbering is chronological and immutable.
New decisions never modify old ADRs — they supersede them.

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
* **Status:** Resolved → superseded by ADR-011
* **Date:** 2026-02-10
* **Resolved:** 2026-03-07
* **Context:** Monolithic scripts were becoming difficult to scale and test.
* **Decision:** Refactor into `src/utils/` and `src/processors/`.
* **Rationale:** Separates extraction logic from database logic. Makes adding 
  Zigbee possible without breaking KNMI.
* **Resolution:** Implemented as modular read/validate/write functions per 
  source. See ADR-011 for full pattern decision and Docker migration path.

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

# [ADR-013] Pinned Requirements File as Venv Safety Net
Status: Accepted / Implemented
Date: 2026-03-08
Context:
Server operations on the Pi broke the virtual environment silently. xarray and duckdb modules became unavailable. Cron pipeline failed for multiple hours before detected. Unpinned requirements.txt existed but listed package names only — no versions. Latest version installs on rebuild may break code.
Incident:
ModuleNotFoundError: No module named 'xarray'
ModuleNotFoundError: No module named 'duckdb'
Pipeline ran degraded — Zigbee Silver continued, KNMI Bronze/Silver failed.
Decision:
Replace unpinned requirements.txt with pinned version output from pip freeze. All dependencies including transitive dependencies captured at exact versions.
Rationale:

Pinned versions = reproducible environment every rebuild
pip install -r requirements.txt restores exact working state
Transitive dependencies captured — manual lists miss these
One command recovery until Docker Phase 2

Recovery Command:
bash/mnt/data/sentinel-pi/.venv/bin/python3 -m pip install -r requirements.txt
Consequences:

requirements.txt must be updated after every intentional package upgrade
Docker Phase 2 supersedes this — containers carry own dependencies
This is a temporary safety net, not a permanent solution

Permanent Solution: Docker Phase 2 — containers isolate dependencies from host server operations entirely.

# [ADR-014] NAS Mount Permanence via fstab UUID
Status: Accepted / Implemented
Date: 2026-03-08
Context:
Server operations changed the NAS mount location from /mnt/data to /media/m-m/c28c2621-fe58-4591-8. All pipeline scripts reference /mnt/data/sentinel-pi via config.py. Mount change caused silent path failures across entire platform.
Incident:
Pipeline scripts could not locate databases
/mnt/data/sentinel-pi path unavailable
Decision:
Mount NAS permanently via /etc/fstab using full UUID with nofail flag:
UUID=c28c2621-fe58-4591-8009-84983b3938bf /mnt/data ext4 defaults,nofail 0 2
Rationale:

UUID-based mount survives device path changes (sda1 → sdb1 etc.)
nofail prevents Pi boot hang if NAS unavailable
Permanent mount survives reboots — temporary mount does not
Single mount point /mnt/data is hardcoded in config.py — must never change

Consequences:

Any NAS replacement requires fstab UUID update
/mnt/data path is now a platform constant — treat as locked
Added to PI_INFRASTRUCTURE_CONSTRAINTS.md

Safe Rule:

"If a change affects /mnt/data mount — stop and check fstab and config.py first."


## [ADR-015] Iceberg-First Data Layer Strategy

**Status:** Accepted — Backlog (Blocked by Parquet migration)
**Date:** 2026-03-09

**Context:**
Current data layer uses DuckDB tables. Enterprise standard requires modern
table semantics — schema evolution, time travel, branching — without
immediately committing to a cloud vendor.

**Decision:**
Migrate to Apache Iceberg tables in sequence:
```
DuckDB tables → Parquet files → Iceberg tables
```
Use DuckDB + Iceberg locally on Raspberry Pi before cloud deployment.
Delay cloud-specific technologies (S3, Snowflake, Databricks) until
core Iceberg skills are mastered.

**Rationale:**
- Iceberg skills are portable across AWS/Azure/GCP and Snowflake/Databricks
- Schema evolution without full rewrites
- Time-travel and snapshot queries for ML experiments
- Local Iceberg + DuckDB keeps stack lightweight for Pi constraints
- Vendor-agnostic foundation before cloud commitment

**Sequence:**
```
Phase 1 → DuckDB tables (current)
Phase 2 → Parquet migration (ADR backlog)
Phase 3 → Iceberg migration (this ADR)
```

**Consequences:**
- Parquet migration must complete before Iceberg migration begins
- No schema changes required between phases
- Blocked by: Phase 1 closure + Parquet migration

**Corrected Implementation Sequence:**

-- Step 1: Export DuckDB → Parquet
COPY (SELECT * FROM knmi_raw) 
TO 'bronze/knmi_20260311.parquet';

COPY (SELECT * FROM zigbee_raw) 
TO 'bronze/zigbee_20260311.parquet';

-- Step 2: Create Iceberg from Parquet
CREATE TABLE iceberg_data.bronze_knmi
USING iceberg
LOCATION '/mnt/data/sentinel-pi/data/iceberg/bronze_knmi'
FROM read_parquet('bronze/knmi_*.parquet');

-- Step 3: Future writes → Iceberg directly
INSERT INTO iceberg_data.bronze_knmi VALUES (...);

---

## [ADR-016] Orchestrator Selection Strategy

**Status:** Accepted — Planned Phase 2
**Date:** 2026-03-09

**Context:**
Cron is current orchestration. As pipeline complexity grows —
retry logic, dependency management, observability — cron becomes
insufficient. Pi resource constraints limit orchestrator choice.
Dutch market requires Airflow knowledge for €140k+ roles.

**Decision:**
```
Phase 2 (Pi)    → Prefect  — lightweight, Python-first, ~120MB RAM
Phase 3 (Cloud) → Airflow  — enterprise standard, Dutch market standard
```

Prefect used specifically to:
- Learn orchestration concepts (flows, retries, scheduling)
- Mirror Airflow mental model (Prefect flows ≈ Airflow DAGs)
- Replace cron without overloading Pi

**Rationale:**
- Prefect runs efficiently on constrained hardware
- Airflow required in 80-85% of Dutch Data/AI PM roles
- Prefect → Airflow transition mirrors real-world edge → enterprise path
- Modular functions already built are Prefect-task ready — no rewrite

**Migration Path:**
```
Current cron job          → Prefect Flow
read/validate/write funcs → Prefect Tasks
cron schedule             → Prefect deployment schedule
```

**Consequences:**
- Phase 2 Docker brings Prefect — replaces cron entirely
- Phase 3 Airflow transition requires no code rewrite
- Blocked by: Phase 2 Docker

---

## [ADR-017] KNMI Cron Frequency Increased to 10-Minute Intervals

**Status:** Accepted / Implemented
**Date:** 2026-03-09

**Context:**
Gold DQ threshold required knmi_reading_count >= 5 per hourly window.
KNMI publishes 6 files per hour — one every 10 minutes, 2 stations each.
Hourly cron captured only 1 file = 2 rows per hour.
Result: All 1226 Gold rows flagged invalid with knmi_low_count.

**Root Cause:**
```
KNMI publishes: :00, :10, :20, :30, :40, :50 (6 files/hour)
Old cron:       :00 only (1 file/hour)
Rows captured:  2 per hour (1 file × 2 stations)
Rows expected:  12 per hour (6 files × 2 stations)
```

**Decision:**
Increase cron frequency from hourly to every 10 minutes:
```bash
# Old
0 * * * * cd /mnt/data/sentinel-pi && python3 src/ingest_data.py

# New
*/10 * * * * cd /mnt/data/sentinel-pi && python3 src/ingest_data.py
```

**Rationale:**
- Fixes root cause — captures all 6 KNMI files per hour
- 12 rows per hour satisfies updated DQ threshold
- Platform purpose requires high granularity for ML correlation
- Cron stability proven over 4 days — safe to increase frequency
- Parquet predicate pushdown handles increased Bronze volume efficiently

**Consequences:**
- 6x more Bronze KNMI rows per hour
- Zigbee collection also runs every 10 minutes — 6 collections per hour
- Gold validity expected to restore as new data accumulates
- Existing invalid Gold rows preserved as historical record of data gap
- Risk: Pipeline runtime ~6 mins, cron interval 10 mins — monitor for overlap
- Mitigation: Add cron lock mechanism (flock) — backlog item

---

## [ADR-018] Gold DQ Thresholds — Strict Governance at Aggregation Layer

**Status:** Accepted / Implemented
**Date:** 2026-03-09

**Context:**
Gold DQ thresholds were set during initial schema design before actual
data volumes were known. After increasing cron to 10-minute intervals —
expected readings per hourly Gold window changed significantly.

**Previous Thresholds:**
```
knmi_reading_count   < 5  → invalid
zigbee_reading_count < 2  → invalid
```

**Updated Thresholds:**
```
knmi_reading_count   < 10 → invalid  (83% of 12 expected)
zigbee_reading_count < 45 → invalid  (94% of 48 expected)
```

**Rationale:**
Stricter thresholds applied as data matures toward Gold layer.

For Zigbee specifically:
> "IoT devices are built for reliability. If they cannot meet the
> threshold — identify the cause rather than forgive the gap."

Bronze accepts everything.
Silver validates ranges.
Gold enforces strict completeness.

Each layer applies tighter governance than the previous.
This is the correct medallion architecture philosophy.

**Calculation:**
```
KNMI:   12 expected/hour × 83% = 10 minimum
Zigbee: 48 expected/hour × 94% = 45 minimum
        (4 rooms × 2 records × 6 windows = 48)
```

**Consequences:**
- Gold valid rows will increase as 10-minute data accumulates
- High invalidity rate initially — expected, not a bug
- DQ flags preserved for AI anomaly detection (future Phi3 analysis)
- Thresholds reviewed again after 2 weeks of stable 10-minute data

---

## [ADR-019] Capability Framework for Sentinel-Pi Product Roadmap

**Status:** Accepted
**Date:** 2026-03-09

**Context:**
Platform was being described as a technical project. Career and arch
coaches aligned on reframing as a product with capability layers —
consistent with how AI/data product roadmaps are structured at
enterprise scale.

**Decision:**
Adopt four-capability product framework:

| Capability | User Outcome | Status |
|------------|-------------|--------|
| 1. Sensing | Reliable home measurements | ✅ Live — Phase 1 |
| 2. Prediction | Forecast temp/air quality | 🔄 Phase 2-3 |
| 3. Optimization | Auto energy savings | ⏳ Phase 3 |
| 4. Explanation | Natural language insights | ⏳ Phase 4 |

**Rationale:**
- Product capability thinking is how TPM roles structure roadmaps
- Each capability maps to a platform phase — traceable delivery
- Hiring managers read capability roadmaps — not architecture diagrams
- Sentinel-Pi story becomes: "I built Capability 1. Capability 2 is next."

**Architecture Mapping:**
```
Capability 1 → Bronze + Silver + Gold (current)
Capability 2 → ML models on Gold features
Capability 3 → Decision engine + Home Assistant actuators
Capability 4 → Phi3/Ollama + Streamlit dashboard
```

**Consequences:**
- All future ADRs reference which capability they advance
- Daily capability log maintained in docs/capability_log.md
- LinkedIn and interview narrative structured around capabilities
- Not just "I built a pipeline" — "I delivered Capability 1 sensing platform"


## [ADR-020] Privacy & EU Compliance Strategy

**Status:** Accepted — Backlog (Blocked by Phase 1 closure)
**Date:** 2026-03-10

**Context:**
Dutch Data/AI PM roles require demonstrated understanding of GDPR,
EU AI Act, and PII governance in production data platforms.
Current Bronze data is weather + IoT sensors — zero PII risk today.
GDPR-by-design narrative needed for interviews before implementation.

**Decision:**
Implement GDPR-by-design in two stages:

Stage 1 — Immediate (narrative only):
- Data classification documented per layer
- GDPR principles mapped to architecture
- No code changes required

Stage 2 — Phase 2 implementation:
- `pii_guard.py` — PII screening Bronze→Silver
- Retention cleanup job (bronze_raw: 30 days)
- data_classification column in Iceberg metadata

**Data Classification (Implemented Now):**

| Layer | Classification | Rationale |
|-------|---------------|-----------|
| bronze/ | INTERNAL | Raw sensor data, timestamps |
| silver/ | INTERNAL | Validated, granular records |
| gold/ | PUBLIC | Aggregated, anonymised |
| ops/ | INTERNAL | Audit trail |
| logs/ | INTERNAL | 30-day retention |

**GDPR 7 Principles Mapping:**

| Principle | Sentinel Implementation |
|-----------|------------------------|
| Lawfulness | Documented legal basis per table |
| Purpose Limitation | Table-level purpose docs in ADR |
| Data Minimisation | PII screening (Phase 2) |
| Accuracy | Gold DQ thresholds enforced |
| Storage Limitation | 30-day raw retention (Phase 2) |
| Integrity | ACID writes + file permissions |
| Accountability | ADRs + full pipeline logging |

**Rationale:**
- Current data has zero PII — implementation not urgent
- Narrative ready for interviews immediately
- Stage 2 implementation deferred to Phase 2 without risk

**Interview Answer:**
> "Sentinel implements GDPR-by-design — data classified as
> INTERNAL/PUBLIC per layer, purpose documented in ADRs,
> DQ thresholds enforce accuracy, full audit trail in ops.db.
> PII screening and retention policies planned for Phase 2."

**Consequences:**
- pii_guard.py implementation → Phase 2 backlog
- Data classification documented — zero overhead
- Blocked by: Phase 1 closure

---

## [ADR-021] Percentage-Based DQ Completeness for Gold Layer

**Status:** Accepted / Implemented
**Date:** 2026-03-10

**Context:**
Gold DQ thresholds were hardcoded record counts:
```
knmi_reading_count   < 10 → invalid
zigbee_reading_count < 45 → invalid
```

Problems identified:
1. Brittle — every pipeline frequency change requires manual threshold update
2. Not streaming-ready — record counts meaningless in continuous streams
3. Assumes fixed expected counts — wrong assumption

**Decision:**
Replace hardcoded counts with runtime completeness percentage:

```python
knmi_completeness   = knmi_valid_count / knmi_total_count
zigbee_completeness = zigbee_valid_count / zigbee_total_count

if knmi_completeness < KNMI_COMPLETENESS_MIN:
    flags.append("knmi_low_completeness")
if zigbee_completeness < ZIGBEE_COMPLETENESS_MIN:
    flags.append("zigbee_low_completeness")
```

Config thresholds (only constants needed):
```python
KNMI_COMPLETENESS_MIN   = 0.84  # 84% of hourly records valid
ZIGBEE_COMPLETENESS_MIN = 0.94  # 94% of hourly records valid
```

**Rationale:**
> "IoT devices are built for reliability. If they cannot meet
> the threshold — identify the cause rather than forgive the gap."

- Self-calibrating — adapts to any collection frequency
- Streaming-ready — percentage works regardless of volume
- No hardcoded expected counts — eliminates brittle assumptions
- Only thresholds in config — one place to update

**Consequences:**
- Gold DQ valid rows: 1418 (100% valid) after implementation
- Threshold review after 2 weeks stable data
- Phase 3 streaming: time-based completeness windows replace percentage

---

## [ADR-022] Read-Only Connection Strategy for Non-Write Operations

**Status:** Accepted / Implemented
**Date:** 2026-03-10

**Context:**
DuckDB single-writer lock causes concurrency issues. At 10-minute cron
intervals with ~6-minute pipeline runtime — only 4-minute safe query
window per cycle. AI script and manual queries blocked during pipeline
runs. Identified as real risk before AI log summarization deployment.

**Decision:**
Introduce `connect_to_db_readonly()` in `db_utils.py`:

```python
def connect_to_db_readonly(db_path: str):
    """
    Read-only connection — safe during pipeline runs.
    Use for: AI scripts, manual queries, reporting.
    Never use for: Bronze/Silver/Gold writes.
    """
    return duckdb.connect(db_path, read_only=True)
```

**Usage Rule:**
```
connect_to_db()          → pipeline writes only
connect_to_db_readonly() → AI scripts, queries, reporting
```

**Rationale:**
- Read-only connections do not block on write locks
- AI script reads Gold only — minimal conflict window
- Simple fix — no architecture changes required
- Formal connection pooling deferred to Docker Phase 2

**Consequences:**
- All AI scripts must use `connect_to_db_readonly()`
- scratch.py updated to use read-only connections
- Docker Phase 2 supersedes with proper connection pooling
- Added to `PI_INFRASTRUCTURE_CONSTRAINTS.md`

---

## [ADR-023] Gold Clean Slate Policy

**Status:** Accepted / Implemented
**Date:** 2026-03-10

**Context:**
Gold layer accumulated 1410 invalid rows due to incorrect processing
logic — partial hour aggregation and hardcoded record count thresholds.
Decision required: fix in place or rebuild clean.

**Decision:**
Drop and rebuild Gold when processing logic changes.

> "Gold should always be clean — this was incorrect processing,
> not bad data."

**Rationale:**
- Bad data → stays in Silver, flagged, never dropped
- Incorrect processing → fix the logic, rebuild Gold clean
- Gold is the analytics layer — ML and AI consume it directly
- Corrupted Gold = corrupted model training

**Rebuild Procedure:**
```bash
# 1. Drop Gold table
con.execute('DROP TABLE IF EXISTS gold_weather')

# 2. Reset Gold watermark
con.execute("DELETE FROM watermarks WHERE source = 'gold_weather'")

# 3. Recreate schema
python3 src/create_silver_tables.py

# 4. Fix processing logic

# 5. Rerun pipeline — Gold rebuilds from Silver
```

**Consequences:**
- Gold rebuild is safe — Silver always preserved
- Historical gap documented in ADR — not hidden
- Rebuild procedure documented for future use
- Gold watermark reset required on every rebuild

## [ADR-024] Observability and Platform Metrics Strategy

**Status:** Accepted — Partially Implemented
**Date:** 2026-03-11

**Context:**
Pipeline runs every 10 minutes. Silent failures, degraded 
data quality, and sensor dropouts are not visible without 
structured observability. Current logging captures 
per-run summaries but no cross-run trend analysis.

**Decision:**
Track operational metrics per pipeline run:

| Metric | Source | Purpose |
|--------|--------|---------|
| pipeline_runtime | logs | Detect slowdowns |
| dq_valid_percentage | ops.db | Quality trends |
| rows_ingested | ops.db | Volume anomalies |
| cron_delay | logs | Scheduling drift |
| sensor_coverage | Silver | Room dropout detection |

Expose metrics through three channels:
1. AI summaries — Phi3 daily log report (Phase 1)
2. Log analysis — structured cron.log (current)
3. Dashboard — Streamlit (Phase 4)

**Rationale:**
- Observability ensures reliability of Capability 1 — Sensing
- Early detection of platform degradation before Gold is affected
- pipeline_runs table in ops.db is the foundation
- AI summary is the first consumer of these metrics

**Implementation Phases:**
```
Phase 1 → AI log summarization reads cron.log ← tomorrow
Phase 2 → pipeline_runs table populated per run
Phase 3 → Prefect built-in observability
Phase 4 → Streamlit dashboard
```

**Consequences:**
- pipeline_runs table moves up backlog priority
- AI summary must include DQ percentage and row counts
- Sensor coverage metric requires Silver query per run