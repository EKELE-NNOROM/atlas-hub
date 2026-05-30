"""
Monthly backfill DAG — parameterized date range for reprocessing.
Usage: trigger with conf {"start_date": "2024-01-01", "end_date": "2024-01-31", "source": "partner_crm"}
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.models.param import Param
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.lambda_function import LambdaInvokeFunctionOperator

from atlas_utils import DEFAULT_ARGS

ENV = "{{ var.value.get('ATLAS_ENV', 'prod') }}"


def validate_backfill_params(**context):
    params = context["params"]
    start = datetime.strptime(params["start_date"], "%Y-%m-%d")
    end = datetime.strptime(params["end_date"], "%Y-%m-%d")
    if end < start:
        raise ValueError("end_date must be >= start_date")
    if (end - start).days > 90:
        raise ValueError("Backfill range limited to 90 days per run")


with DAG(
    dag_id="monthly_backfill",
    default_args={**DEFAULT_ARGS, "retries": 0},
    description="Parameterized historical backfill for custom sources",
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["backfill"],
    params={
        "start_date": Param("2024-01-01", type="string"),
        "end_date": Param("2024-01-31", type="string"),
        "source": Param("partner_crm", type="string"),
    },
) as dag:

    validate = PythonOperator(
        task_id="validate_params",
        python_callable=validate_backfill_params,
    )

    backfill_extract = LambdaInvokeFunctionOperator(
        task_id="backfill_lambda",
        function_name=f"atlas-partner-extract-{ENV}",
        payload={
            "source": "{{ params.source }}",
            "start_date": "{{ params.start_date }}",
            "end_date": "{{ params.end_date }}",
            "backfill": True,
            "s3_bucket": f"atlas-landing-{ENV}",
        },
    )

    validate >> backfill_extract
