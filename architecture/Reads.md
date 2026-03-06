**PROBLEM**: Current DuckDB tables → enterprise Parquet files
**WHY**: True immutability + schema evolution + zero-rewrite migration

**Phase 1** :
duckdb> COPY knmi_raw TO 'bronze/knmi/year=2026/month=03/day=05/' (FORMAT PARQUET)

**Phase 2**: Direct-to-file cron (skip tables entirely)
bronze/zigbee/year=2026/month=03/day=05/zigbee_bath001.parquet

**Success**: SELECT * FROM 'bronze/knmi/*.parquet' works identically
