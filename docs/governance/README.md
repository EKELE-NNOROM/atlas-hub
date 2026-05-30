# Atlas Hub Data Governance Framework

## Principles

1. **Single definition of truth** — KPIs defined once in dbt Semantic Layer
2. **Privacy by design** — PII tagged, masked, and access-logged by default
3. **Lineage transparency** — Every Tier 1 metric traceable to source column
4. **Least privilege** — Domain RBAC + row-level policies where required
5. **Auditability** — SOX controls on finance pipelines; immutable audit logs

## PII Handling

| Classification | Examples | Controls |
|----------------|----------|----------|
| PII | email, phone, employee_id | Masking policies, HR-only roles |
| Financial | revenue, salary | Finance role, SOX change control |
| Internal | account_name, dept | Analyst role |
| Public | aggregated KPIs | API with auth |

### Tagging

All columns tagged in Snowflake via post-dbt SQL scripts:

```sql
ALTER TABLE ... MODIFY COLUMN email SET TAG GOVERNANCE_PROD.AUDIT.CLASSIFICATION = 'pii';
```

dbt `meta` block mirrors tags:

```yaml
columns:
  - name: email
    meta:
      classification: pii
      retention_days: 2555
```

## GDPR Compliance

| Requirement | Implementation |
|-------------|----------------|
| Lawful basis | Documented in data catalog per source |
| Right to access | DSAR workflow via Legal ticketing |
| Right to erasure | `governance/runbooks/dsar-deletion.sql` |
| Data minimization | PII not propagated to marts unless required |
| Cross-border | Snowflake region = US; BQ = us-central1; DPA with vendors |

## SOX Controls

- Production dbt deploys require 2 approvals (GitHub branch protection)
- No direct DDL in prod Snowflake (SQL scripts in `snowflake/` + dbt only)
- Finance mart changes require Finance sign-off label on PR
- Monthly access recertification for ATLAS_FINANCE role

## Lineage

- **dbt docs** — model-level lineage graph
- **OpenLineage** — Airflow → dbt → Snowflake (Marquez backend)
- **Fivetran** — connector-level lineage in dashboard

## Metadata Management

| Tool | Scope |
|------|-------|
| dbt docs | Transform layer definitions |
| Snowflake INFORMATION_SCHEMA | Physical schema |
| Custom `governance.pii_inventory` | PII catalog |
| Atlan/Collibra (optional) | Enterprise catalog integration |

## Access Controls

See `snowflake/rbac/roles_grants.sql` and `snowflake/security/masking_rls_audit.sql`.

## Data Retention

| Layer | Retention |
|-------|-----------|
| RAW | 7 years (S3 lifecycle + Snowflake Time Travel 90d) |
| Marts | Indefinite |
| Audit logs | 7 years |
| BQ events | 90 days hot; archive to GCS 7 years |
