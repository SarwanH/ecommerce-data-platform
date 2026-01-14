# Architecture

## Overview
Three-layer medallion architecture: Raw → Staging → Marts

## Tech Stack
- **Ingestion:** Python
- **Storage:** DuckDB (dev) / BigQuery (prod)
- **Transformation:** dbt
- **Orchestration:** Apache Airflow
- **Quality:** Great Expectations

## Data Flow
1. Extract from sources → Raw parquet files
2. Load to warehouse → raw.* tables
3. Transform with dbt → staging.*, marts.*
4. Validate with Great Expectations
5. Serve to consumers

## Decisions
- **DuckDB for dev:** Fast, portable, BigQuery-compatible SQL
- **dbt for transforms:** Version control, testing, documentation
- **Airflow:** Industry standard, matches Cloud Composer