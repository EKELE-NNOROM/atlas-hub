"""
Partner CRM REST API extractor.
Triggered by Airflow or EventBridge; lands parquet in S3.
"""

import json
import logging
import os
from datetime import datetime

from atlas_lambda_utils import (
    get_secret,
    paginate_rest_api,
    write_parquet_to_s3,
    write_success_marker,
    date_range,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    env = os.environ.get("ENVIRONMENT", "dev")
    secret = get_secret(f"atlas/partner-crm/{env}")

    source = event.get("source", "partner_crm")
    bucket = event.get("s3_bucket", f"atlas-landing-{env}")
    backfill = event.get("backfill", False)

    if backfill:
        dates = date_range(event["start_date"], event["end_date"])
    else:
        dates = [event.get("extract_date", datetime.utcnow().strftime("%Y-%m-%d"))]

    total_rows = 0
    for extract_date in dates:
        prefix = event.get("s3_prefix", f"{source}/dt={extract_date}/")
        records = list(
            paginate_rest_api(
                base_url=f"{secret['base_url']}/api/v1/accounts",
                headers={"Authorization": f"Bearer {secret['api_key']}"},
                params={"updated_since": extract_date, "limit": 500},
                results_key="data",
            )
        )
        for r in records:
            r["_extract_date"] = extract_date
            r["_loaded_at"] = datetime.utcnow().isoformat()

        if records:
            write_parquet_to_s3(records, bucket, prefix)
            total_rows += len(records)
        write_success_marker(bucket, prefix)

    return {
        "statusCode": 200,
        "body": json.dumps({"rows": total_rows, "dates": dates}),
    }
