"""Snowflake loader helper — validates S3 landing and returns COPY SQL metadata."""

import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3 = boto3.client("s3")


def handler(event, context):
    bucket = event["s3_bucket"]
    prefix = event["s3_prefix"]
    env = os.environ.get("ENVIRONMENT", "dev")

    resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=10)
    keys = [o["Key"] for o in resp.get("Contents", []) if o["Key"].endswith(".parquet")]

    if not keys:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "No parquet files found", "prefix": prefix}),
        }

    table = event.get("target_table", "PARTNER_CRM")
    copy_sql = f"""
        COPY INTO RAW_{env.upper()}.S3_LANDING.{table}
        FROM @RAW_{env.upper()}.S3_LANDING.ATLAS_LANDING_STAGE/{prefix}
        FILE_FORMAT = (TYPE = PARQUET)
        MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;
    """

    return {
        "statusCode": 200,
        "body": json.dumps({
            "files_found": len(keys),
            "copy_sql": copy_sql.strip(),
            "keys": keys[:5],
        }),
    }
