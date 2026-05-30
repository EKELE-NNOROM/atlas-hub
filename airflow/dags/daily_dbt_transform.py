"""
Daily dbt transformation DAG.
Triggers full build after ingestion completes; enforces Tier 1 SLA.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.task_group import TaskGroup

from atlas_utils import DEFAULT_ARGS, TIER1_SLA

ENV = "{{ var.value.get('ATLAS_ENV', 'prod') }}"

with DAG(
    dag_id="daily_dbt_transform",
    default_args=DEFAULT_ARGS,
    description="dbt build: staging → marts → semantic",
    schedule_interval="0 4 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["dbt", "tier1"],
    sla=TIER1_SLA,
) as dag:

    wait_ingestion = ExternalTaskSensor(
        task_id="wait_daily_ingestion",
        external_dag_id="daily_ingestion",
        external_task_id="end",
        timeout=7200,
        mode="reschedule",
        poke_interval=300,
    )

    with TaskGroup("dbt_layers") as dbt_layers:
        dbt_staging = BashOperator(
            task_id="dbt_staging",
            bash_command=f"cd /usr/local/airflow/dags/dbt && dbt run --select staging.* --target {ENV}",
        )
        dbt_intermediate = BashOperator(
            task_id="dbt_intermediate",
            bash_command=f"cd /usr/local/airflow/dags/dbt && dbt run --select intermediate.* --target {ENV}",
        )
        dbt_marts = BashOperator(
            task_id="dbt_marts",
            bash_command=f"cd /usr/local/airflow/dags/dbt && dbt run --select marts.* --target {ENV}",
        )
        dbt_semantic = BashOperator(
            task_id="dbt_semantic",
            bash_command=f"cd /usr/local/airflow/dags/dbt && dbt run --select semantic.* --target {ENV}",
        )
        dbt_test = BashOperator(
            task_id="dbt_test",
            bash_command=f"cd /usr/local/airflow/dags/dbt && dbt test --select marts.* semantic.* --target {ENV}",
        )
        dbt_staging >> dbt_intermediate >> dbt_marts >> dbt_semantic >> dbt_test

    trigger_ml = TriggerDagRunOperator(
        task_id="trigger_weekly_ml_if_sunday",
        trigger_dag_id="weekly_ml_scoring",
        conf={"run_date": "{{ ds }}"},
        wait_for_completion=False,
    )

    sla_met = EmptyOperator(task_id="tier1_sla_complete")

    wait_ingestion >> dbt_layers >> sla_met >> trigger_ml
