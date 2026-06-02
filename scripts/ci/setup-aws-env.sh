#!/usr/bin/env bash
# Check whether AWS credentials are available for MWAA deploy.
set -eu

OUTPUT="${GITHUB_OUTPUT:-}"

if [ -n "${AWS_ACCESS_KEY_ID:-}" ] && [ -n "${AWS_SECRET_ACCESS_KEY:-}" ]; then
  configured=true
  echo "AWS credentials detected — Airflow DAG sync will run"
else
  configured=false
  echo "::notice title=Placeholder mode::AWS secrets not configured. Skipping Airflow S3 sync. Add AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to enable deploy."
fi

if [ -n "$OUTPUT" ]; then
  echo "aws_configured=$configured" >> "$OUTPUT"
fi
