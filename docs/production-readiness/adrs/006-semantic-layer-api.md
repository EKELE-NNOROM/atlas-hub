# ADR-006: Semantic Layer with REST API

## Status
Accepted

## Decision
Define metrics in **dbt Semantic Layer**; expose via **FastAPI** with JWT RBAC for internal apps.

## Alternatives
- Proprietary semantic layer products: license cost, duplicate metric definitions
- Cube.js: additional infra
- Direct Snowflake queries from apps: inconsistent KPI definitions

## Auth Pattern
- Okta/Auth0 JWT with `scopes` claim (finance, sales, product, hr, executive)
- Service account `SVC_METRICS_API_PROD` with ATLAS_API_SERVICE role
- Optional Redis cache (15 min TTL) for high-traffic metrics

## Consumers
- Executive dashboard (`semantic-layer/examples/`)
- Internal PLG application
- Finance close automation scripts
