# HR Business Requirements

## Business Objectives

1. Workforce planning with accurate headcount and org structure
2. Track attrition and hiring funnel for People Ops
3. Support finance headcount-to-revenue ratios
4. Protect sensitive employee PII with strict access controls

## KPIs

| KPI | Definition | Grain | Source | Target |
|-----|------------|-------|--------|--------|
| **Headcount** | Active employees (FTE + contractors per policy) | Month × Dept | Workday | Finance reconcile |
| **Attrition Rate** | Voluntary terminations ÷ avg headcount | Month × Dept | Workday | < industry benchmark |
| **Time-to-Hire** | Days from req open to offer accept | Requisition | Workday | < 45 days |
| **Open Reqs** | Count of unfilled approved requisitions | Snapshot weekly | Workday | Planning input |
| **Span of Control** | Direct reports per manager | Manager | Workday | 5–8 target |

## Data Contracts

### `mart_hr__monthly_headcount`

```yaml
grain: employee_id, snapshot_month  # SCD Type 2 employee dim
columns:
  - employee_id: string  # hashed in analyst views
  - department: string
  - cost_center: string
  - employment_status: string
  - fte: decimal(4,2)
  - is_active: boolean
pii_columns: [employee_id, email, salary_usd]
access: hr_analyst, finance_exec only
sla: T+1 09:00 ET
```

## Acceptance Criteria

- [ ] Headcount matches Workday HCM report on close date
- [ ] PII masked by default; RLS by department for HRBP role
- [ ] Termination reason coded and auditable
- [ ] No employee names in non-HR marts
- [ ] GDPR: employee data retention policy enforced (7 years)
