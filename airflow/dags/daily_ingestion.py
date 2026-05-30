"""
Daily ingestion DAG: custom API extractions, S3 staging, Snowflake load.
SLA: complete by 03:00 ET to unblock dbt at 04:00.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.lambda_function import LambdaInvokeFunctionOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.sensors.time_delta import TimeDeltaSensor

from atlas_utils import DEFAULT_ARGS, lambda_payload, env_var

ENV = "{{ var.value.get('ATLAS_ENV', 'dev') }}"
LANDING_BUCKET = f"atlas-landing-{ENV}"
EXTRACT_DATE = "{{ ds }}"

with DAG(
    dag_id="daily_ingestion",
    default_args=DEFAULT_ARGS,
    description="Custom API extraction → S3 → Snowflake RAW",
    schedule_interval="0 2 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["ingestion", "tier1"],
    sla=timedelta(hours=3),
) as dag:

    start = EmptyOperator(task_id="start")

    extract_partner = LambdaInvokeFunctionOperator(
        task_id="extract_partner_crm",
        function_name=f"atlas-partner-extract-{ENV}",
        payload=lambda_payload("partner_crm", EXTRACT_DATE),
        aws_conn_id="aws_default",
        invocation_type="RequestResponse",
    )

    extract_enrichment = LambdaInvokeFunctionOperator(
        task_id="extract_enrichment",
        function_name=f"atlas-enrichment-{ENV}",
        payload=lambda_payload("enrichment", EXTRACT_DATE),
        aws_conn_id="aws_default",
    )

    wait_partner_files = S3KeySensor(
        task_id="wait_partner_s3",
        bucket_name=LANDING_BUCKET,
        bucket_key=f"partner_crm/dt={EXTRACT_DATE}/_SUCCESS",
        timeout=3600,
        poke_interval=60,
    )

    load_snowflake = SnowflakeOperator(
        task_id="snowflake_copy_into",
        snowflake_conn_id="snowflake_default",
        sql="""
            COPY INTO RAW_{{ var.value.get('ATLAS_ENV', 'dev') }}.S3_LANDING.PARTNER_CRM
            FROM @RAW_{{ var.value.get('ATLAS_ENV', 'dev') }}.S3_LANDING.ATLAS_LANDING_STAGE/partner_crm/dt={{ ds }}/
            FILE_FORMAT = (TYPE = PARQUET)
            MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
            ON_ERROR = ABORT_STATEMENT;
        """,
        warehouse="WH_ETL_{{ var.value.get('ATLAS_ENV', 'dev') | upper }}",
    )

    fivetran_delay_buffer = TimeDeltaSensor(
        task_id="fivetran_sync_buffer",
        delta=timedelta(minutes=30),
    )

    end = EmptyOperator(task_id="end")

    start >> [extract_partner, extract_enrichment]
    extract_partner >> wait_partner_files >> load_snowflake
    [load_snowflake, extract_enrichment, fivetran_delay_buffer] >> end
