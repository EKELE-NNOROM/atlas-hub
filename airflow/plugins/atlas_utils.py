"""Shared Airflow utilities for Atlas Hub."""

from datetime import datetime, timedelta
from typing import Any

from airflow.models import Variable

DEFAULT_ARGS = {
    "owner": "data-platform",
    "depends_on_past": False,
    "email": ["data-platform-alerts@company.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
}

TIER1_SLA = timedelta(hours=6)  # 6 AM ET daily completion


def env_var(key: str, default: str | None = None) -> str:
    return Variable.get(key, default_var=default)


def lambda_payload(source: str, extract_date: str) -> dict[str, Any]:
    env = env_var("ATLAS_ENV", "dev")
    return {
        "source": source,
        "extract_date": extract_date,
        "s3_bucket": f"atlas-landing-{env}",
        "s3_prefix": f"{source}/dt={extract_date}/",
    }
