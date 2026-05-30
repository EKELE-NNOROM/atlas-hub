# Logical Architecture

## Domain-Driven Data Zones

```mermaid
flowchart LR
    subgraph IngestionZone["Ingestion Zone"]
        direction TB
        I1[Connector Management]
        I2[Custom Extractors]
        I3[Event Stream Landing]
    end

    subgraph ProcessingZone["Processing Zone"]
        direction TB
        P1[ELT — dbt]
        P2[Quality Gates]
        P3[ML Feature Store]
    end

    subgraph ServingZone["Serving Zone"]
        direction TB
        S1[Semantic Metrics]
        S2[Domain Marts]
        S3[API Layer]
    end

    subgraph GovernanceZone["Governance Zone"]
        direction TB
        G1[Lineage]
        G2[Access Control]
        G3[Catalog & Tags]
    end

    IngestionZone --> ProcessingZone --> ServingZone
    GovernanceZone -.-> IngestionZone & ProcessingZone & ServingZone
```

## Entity Relationships (Conceptual)

```mermaid
erDiagram
    DIM_ACCOUNT ||--o{ FACT_SUBSCRIPTION : has
    DIM_ACCOUNT ||--o{ FACT_OPPORTUNITY : owns
    DIM_ACCOUNT ||--o{ FACT_USAGE : generates
    DIM_CONTACT ||--o{ FACT_MARKETING_TOUCH : receives
    DIM_EMPLOYEE ||--o{ FACT_HEADCOUNT : counts
    DIM_DATE ||--o{ FACT_REVENUE : spans
    DIM_PRODUCT ||--o{ FACT_SUBSCRIPTION : includes

    DIM_ACCOUNT {
        string account_id PK
        string account_name
        string segment
        string industry
    }

    FACT_REVENUE {
        string account_id FK
        date revenue_month
        decimal mrr_usd
        decimal arr_usd
        decimal recognized_revenue_usd
    }

    FACT_OPPORTUNITY {
        string opportunity_id PK
        string account_id FK
        decimal amount_usd
        string stage
        date close_date
    }
```

## Layer Responsibilities

### Raw Layer
- Preserve source fidelity; no business rules
- Fivetran `_fivetran_*` metadata retained for audit
- S3 external tables for product events pre-BQ export

### Staging Layer
- 1:1 with raw tables where possible
- Standardize timestamps to UTC
- Surrogate keys not yet applied

### Intermediate Layer
- Account 360 spine (Salesforce account as golden key)
- SCD Type 2 for opportunities, employees, subscriptions
- Attribution path building (marketing touches)

### Mart Layer
- Denormalized for API and executive dataset consumption
- Domain-specific: finance, sales, marketing, product, hr
- Pre-computed KPIs where query cost is high

### Semantic Layer
- Versioned metric definitions (ARR, MRR, CAC, etc.)
- Consistent filters (e.g., exclude test accounts)
- Time grains: day, week, month, quarter

## Cross-Cutting Concerns

| Concern | Implementation |
|---------|----------------|
| Identity | `int_account_spine` maps SFDC ↔ Stripe ↔ HubSpot ↔ product |
| Test data exclusion | Global variable `exclude_test_account_ids` |
| Currency | USD normalization in `int_fx_rates` from NetSuite |
| Time | `dim_date` fiscal calendar aligned to Finance |
