
# Knowledge Morsels
KM-01 — Data Product Canvas — fully populated with Gold layer. 
Problem, users, KPIs, sources, SLAs, governance, architecture, open questions. 
Saved as docs/products/gold_canvas.md.

KM-02 — Lakehouse Maturity Model — Sentinel-Pi positioned across all four stages with a maturity score:
Stage 1 (Raw Lake)      100% ✅
Stage 2 (Governed Lake)  70% 🔄
Stage 3 (Lakehouse)      35% ⏳
Stage 4 (Platform)       20% ⏳

KM-03: Enterprise Orchestration Standards
Core idea: Enterprises govern via platform templates
           not custom orchestration code.
Databricks → Jobs API JSON + Unity Catalog
Snowflake  → CREATE TASK + Dynamic Tables
Sentinel   → proves architecture, Phase 3 = configuration only
Interview  → "Custom code = learning. Templates = production."
File:      docs/knowledge/KM-03-orchestration-standards.md


KM-04: Dutch AI Governance
- NEA (Nationale Enquête Arbeidsomstandigheden) surveys
  → Dutch labor market AI exposure data
- EU AI Act localization → Dutch implementation specifics
- 44% junior task automation → oversight role shift
- Why it matters: hiring managers at ING/Adyen/Booking
  expect TPM candidates to speak to Dutch regulatory context
- Interview answer needed:
  "How does EU AI Act affect your platform decisions?"
Action: Research NEA surveys + EU AI Act Article 9-15
        Map to Sentinel-Pi governance decisions
        Add to ADR-020 GDPR section
Priority: High — before first interview

KM-05: Prompt Engineering for TPM Roles
- Hybrid human-AI workflows
- Lleverage and similar Dutch AI tooling
- Prompt design patterns for data platform use cases
- Why it matters: Dutch recruitment flags this
  specifically for PMs leading localized AI
Action: Hands-on practice with:
  1. Chain-of-thought prompting
  2. Few-shot examples
  3. Structured output prompting (JSON mode)
  Map to Sentinel-Pi AI summary prompt design
Priority: High — directly applicable to ai_summary.py

KM-SODA-01: NaN handling across tools
- SQL:        temp = temp (self-comparison)
- Soda Core:  isnan(temp) (explicit function)  
- DuckDB:     isnan(temp) OR temp != temp
- dbt:        {{ not is_nan("temp") }}
- Rule: always verify NaN syntax per tool —
  never assume SQL standard applies