# Legal & Compliance Business Requirements

## Business Objectives

1. GDPR and privacy compliance for customer and employee data
2. SOX controls over financial reporting data pipelines
3. Complete audit trail for data access and transformations
4. Data retention and deletion (right to erasure) workflows

## KPIs (Compliance)

| Control | Requirement | Evidence |
|---------|-------------|----------|
| PII Inventory | 100% tagged columns | Snowflake tags + dbt meta |
| DSAR Response | < 30 calendar days | Ticketing + deletion logs |
| SOX Change Control | All prod changes via CI/CD | GitHub + deployment logs |
| Access Reviews | Quarterly recertification | IAM + Snowflake audit |
| Data Lineage | Source-to-mart for Tier 1 | dbt + OpenLineage |

## Data Contracts

### `governance__pii_inventory`

Automated catalog of PII columns with classification, owner, retention policy.

### `governance__audit_log`

Immutable log of query access to sensitive objects (via Snowflake access history + SIEM).

## Acceptance Criteria

- [ ] All PII columns tagged `classification: pii` in Snowflake
- [ ] Dynamic data masking policies applied to analyst roles
- [ ] DSAR workflow documented with automated deletion in staging/raw where feasible
- [ ] SOX: segregation of duties — developers cannot deploy to prod without approval
- [ ] Legal sign-off on cross-border data transfer (Snowflake region + BQ location)
