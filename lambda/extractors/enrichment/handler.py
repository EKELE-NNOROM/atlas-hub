"""External enrichment service — augments account records with firmographics."""

import json
import logging
import os
from datetime import datetime

import requests

from atlas_lambda_utils import get_secret, write_parquet_to_s3, write_success_marker

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    env = os.environ.get("ENVIRONMENT", "dev")
    secret = get_secret(f"atlas/enrichment/{env}")
    bucket = event.get("s3_bucket", f"atlas-landing-{env}")
    extract_date = event.get("extract_date", datetime.utcnow().strftime("%Y-%m-%d"))
    prefix = f"enrichment/dt={extract_date}/"

    account_ids = event.get("account_ids", [])
    if not account_ids:
        # Batch mode: read from event payload or default sample
        account_ids = event.get("batch_account_ids", [])

    enriched = []
    for account_id in account_ids:
        resp = requests.get(
            f"{secret['base_url']}/v1/companies/{account_id}",
            headers={"X-Api-Key": secret["api_key"]},
            timeout=30,
        )
        if resp.status_code == 404:
            continue
        resp.raise_for_status()
        data = resp.json()
        enriched.append({
            "account_id": account_id,
            "employee_count_band": data.get("employee_count_band"),
            "industry_code": data.get("industry", {}).get("code"),
            "tech_stack": data.get("technologies", []),
            "_extract_date": extract_date,
            "_loaded_at": datetime.utcnow().isoformat(),
        })

    if enriched:
        write_parquet_to_s3(enriched, bucket, prefix)
    write_success_marker(bucket, prefix)

    return {"statusCode": 200, "body": json.dumps({"enriched_count": len(enriched)})}
