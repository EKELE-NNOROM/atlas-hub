# Data Platform Onboarding

Welcome to Atlas Hub. This guide gets you productive in your first week.

## Day 1: Access

1. Request Okta groups: `atlas-analyst` or domain-specific (`atlas-finance`, etc.)
2. Snowflake SSO login → verify role assignment
3. Clone repo: `git clone https://github.com/company/atlas-hub.git`
4. Join Slack: `#data-platform`, `#data-help`

## Day 2: Environment Setup

```bash
# Python 3.11+
cd atlas-hub/dbt
cp profiles.yml.example ~/.dbt/profiles.yml
# Configure Snowflake SSO user

dbt deps
dbt debug
dbt run --select staging.salesforce --target dev
```

## Day 3: Understand the Platform

| Read | Purpose |
|------|---------|
| [Architecture](../../architecture/README.md) | End-to-end flow |
| [Data Modeling](../../architecture/data-modeling.md) | Layer conventions |
| [Business Requirements](../../business-requirements/README.md) | KPI definitions |
| [Governance](../../governance/README.md) | PII and access rules |

## Day 4: Development Workflow

1. Branch from `main`: `feature/DATA-123-add-metric`
2. Make dbt changes + tests + schema YAML docs
3. Open PR → dbt CI runs automatically
4. Get review from code owner (see CODEOWNERS)
5. Merge → deploy-prod workflow runs for approved paths

## Naming Conventions

- Staging: `stg_{source}__{entity}`
- Intermediate: `int_{concept}`
- Marts: `mart_{domain}__{entity}`
- One model per file; CTEs preferred over nested subqueries

## Getting Help

- Metric definition questions → `#data-help` or semantic layer docs
- Pipeline failures → check [runbooks](runbooks/)
- Access issues → `#it-help` + data platform ticket

## Key Contacts

| Area | Team | Slack |
|------|------|-------|
| Platform | Data Engineering | `#data-platform` |
| Finance KPIs | Analytics Engineering | `#data-finance` |
| ML models | ML Engineering | `#ml-platform` |
