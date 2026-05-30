"""Shared utilities for Atlas Lambda extractors."""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Iterator

import boto3
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
secrets = boto3.client("secretsmanager")


def get_secret(secret_name: str) -> dict[str, Any]:
    response = secrets.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


def paginate_rest_api(
    base_url: str,
    headers: dict[str, str],
    params: dict[str, Any] | None = None,
    page_param: str = "page",
    results_key: str = "results",
    max_pages: int = 1000,
) -> Iterator[dict[str, Any]]:
    """Generic REST paginator supporting offset/page patterns."""
    params = dict(params or {})
    page = 1
    while page <= max_pages:
        params[page_param] = page
        resp = requests.get(base_url, headers=headers, params=params, timeout=60)
        resp.raise_for_status()
        payload = resp.json()
        records = payload.get(results_key, payload if isinstance(payload, list) else [])
        if not records:
            break
        yield from records
        if not payload.get("has_next", len(records) > 0 and page < max_pages):
            if len(records) < params.get("limit", 100):
                break
        page += 1


def write_parquet_to_s3(
    records: list[dict[str, Any]],
    bucket: str,
    prefix: str,
    filename: str = "data.parquet",
) -> str:
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    from io import BytesIO

    df = pd.DataFrame(records)
    table = pa.Table.from_pandas(df)
    buf = BytesIO()
    pq.write_table(table, buf)
    key = f"{prefix.rstrip('/')}/{filename}"
    s3.put_object(Bucket=bucket, Key=key, Body=buf.getvalue())
    logger.info("Wrote s3://%s/%s (%d rows)", bucket, key, len(df))
    return key


def write_success_marker(bucket: str, prefix: str) -> None:
    s3.put_object(Bucket=bucket, Key=f"{prefix.rstrip('/')}/_SUCCESS", Body=b"")


def date_range(start: str, end: str) -> list[str]:
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    days = []
    while s <= e:
        days.append(s.strftime("%Y-%m-%d"))
        s += timedelta(days=1)
    return days
