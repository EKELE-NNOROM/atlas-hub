# Runbook: Airflow DAG Deployment

## Deploy DAGs to MWAA

```bash
# Sync from CI or locally (with AWS creds)
aws s3 sync airflow/dags/ s3://atlas-airflow-prod/dags/ --delete
aws s3 cp airflow/requirements.txt s3://atlas-airflow-prod/requirements.txt

# MWAA picks up changes in ~5 minutes
```

## Rollback

```bash
git checkout HEAD~1 -- airflow/dags/problematic_dag.py
aws s3 cp airflow/dags/problematic_dag.py s3://atlas-airflow-prod/dags/
```

## Validate DAG import

```bash
python scripts/validate_dags.py
```

## Pause DAG during incident

Airflow UI → DAG → Pause, or CLI:
```bash
aws mwaa create-cli-token --name atlas-airflow-prod
# use token to run: dags pause daily_dbt_transform
```
