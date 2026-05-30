"""
Weekly ML scoring on Databricks — churn, segmentation, forecast.
Runs after dbt marts are fresh (Sunday or triggered).
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from airflow.sensors.external_task import ExternalTaskSensor

from atlas_utils import DEFAULT_ARGS

ENV = "{{ var.value.get('ATLAS_ENV', 'prod') }}"

with DAG(
    dag_id="weekly_ml_scoring",
    default_args={**DEFAULT_ARGS, "retries": 1},
    description="Databricks ML: segmentation, churn, forecast → Snowflake",
    schedule_interval="0 5 * * 0",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["ml", "databricks"],
) as dag:

    wait_dbt = ExternalTaskSensor(
        task_id="wait_dbt_marts",
        external_dag_id="daily_dbt_transform",
        external_task_id="dbt_layers.dbt_marts",
        timeout=14400,
        mode="reschedule",
    )

    run_segmentation = DatabricksRunNowOperator(
        task_id="customer_segmentation",
        databricks_conn_id="databricks_default",
        job_id="{{ var.value.get('DBX_JOB_SEGMENTATION') }}",
        json={"job_parameters": {"env": ENV, "run_date": "{{ ds }}"}},
    )

    run_churn = DatabricksRunNowOperator(
        task_id="churn_scoring",
        databricks_conn_id="databricks_default",
        job_id="{{ var.value.get('DBX_JOB_CHURN') }}",
    )

    run_forecast = DatabricksRunNowOperator(
        task_id="revenue_forecast",
        databricks_conn_id="databricks_default",
        job_id="{{ var.value.get('DBX_JOB_FORECAST') }}",
    )

    wait_dbt >> run_segmentation >> run_churn >> run_forecast
