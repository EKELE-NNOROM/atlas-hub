# Data Flow Diagrams

## Flow 1: SaaS → Snowflake (Fivetran)

```mermaid
sequenceDiagram
    participant SRC as Salesforce
    participant FT as Fivetran
    participant SF as Snowflake RAW
    participant DBT as dbt
    participant MART as MARTS

    SRC->>FT: Incremental sync (every 6h)
    FT->>SF: MERGE into raw tables
    Note over SF: _fivetran_synced timestamp
    DBT->>SF: Read RAW, write STG/INT/MART
    MART->>MART: Freshness tests pass
```

## Flow 2: Custom API → S3 → Snowflake

```mermaid
sequenceDiagram
    participant AF as Airflow
    participant LM as Lambda
    participant API as Partner API
    participant S3 as S3 Landing
    participant SP as Snowpipe
    participant SF as Snowflake RAW

    AF->>LM: Invoke async (payload: date range)
    LM->>API: Paginated REST GET
    API-->>LM: JSON records
    LM->>S3: Write parquet (partitioned by dt=)
    AF->>SP: Trigger pipe load
    SP->>SF: COPY INTO raw.partner_enrichment
```

## Flow 3: Product Events → BigQuery → Snowflake

```mermaid
sequenceDiagram
    participant APP as Product App
    participant GA4 as GA4 / SDK
    participant BQ as BigQuery
    participant AF as Airflow
    participant S3 as S3
    participant SF as Snowflake

    APP->>GA4: Events
    GA4->>BQ: Daily export (native)
    APP->>BQ: Streaming insert (high-value events)
    AF->>BQ: Scheduled aggregate query
    BQ->>S3: Export daily engagement parquet
    AF->>SF: COPY INTO mart_product staging
```

## Flow 4: dbt → Databricks → Snowflake

```mermaid
sequenceDiagram
    participant AF as Airflow
    participant SF as Snowflake MARTS
    participant DBX as Databricks
    participant ML as MLflow

    AF->>SF: dbt build complete sensor
    AF->>DBX: Trigger churn scoring job
    DBX->>SF: Read features from marts
    DBX->>DBX: Train/score (weekly)
    DBX->>ML: Log model version
    DBX->>SF: Write predictions to mart_product.churn_scores
```

## Flow 5: Semantic Metrics → API

```mermaid
sequenceDiagram
    participant APP as Internal App
    participant API as Metrics API
    participant SF as Snowflake SEMANTIC
    participant CACHE as Redis

    APP->>API: GET /metrics/arr?grain=month
    API->>API: Validate JWT + RBAC scope
    API->>CACHE: Check cache key
    alt cache miss
        API->>SF: Query semantic mart / compiled metric SQL
        SF-->>API: Result set
        API->>CACHE: Store TTL 15m
    end
    API-->>APP: JSON metrics response
```

## Daily Batch Schedule (Production)

| Time (ET) | Job |
|-----------|-----|
| 00:00 | Fivetran high-frequency connectors complete window |
| 02:00 | Airflow: custom extractions + S3 loads |
| 03:00 | Snowpipe ingest completion sensor |
| 04:00 | dbt build (staging → marts) |
| 05:00 | Databricks scoring (if ML day) |
| 05:30 | Semantic layer freshness tests |
| 06:00 | Tier 1 SLA deadline — exec datasets ready |
| 06:15 | Observability dashboard green / alert if not |
