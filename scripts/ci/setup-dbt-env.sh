#!/usr/bin/env bash
# Configure dbt credentials for CI.
# - Without secrets: writes placeholder key + sets snowflake_configured=false
# - With secrets:    writes real key     + sets snowflake_configured=true
set -eu

KEY_PATH="${SNOWFLAKE_PRIVATE_KEY_PATH:-/tmp/snowflake_key.p8}"
OUTPUT="${GITHUB_OUTPUT:-}"

export SNOWFLAKE_ACCOUNT="${SNOWFLAKE_ACCOUNT:-placeholder.us-east-1}"
export SNOWFLAKE_USER="${SNOWFLAKE_USER:-PLACEHOLDER_DBT_USER}"
export SNOWFLAKE_ROLE="${SNOWFLAKE_ROLE:-ATLAS_TRANSFORMER}"
export SNOWFLAKE_PRIVATE_KEY_PATH="$KEY_PATH"

is_real_account=false
if [ "$SNOWFLAKE_ACCOUNT" != "placeholder.us-east-1" ] && [ -n "$SNOWFLAKE_ACCOUNT" ]; then
  is_real_account=true
fi

has_private_key=false
if [ -n "${SNOWFLAKE_PRIVATE_KEY:-}" ] && [ "$SNOWFLAKE_PRIVATE_KEY" != "PLACEHOLDER" ]; then
  has_private_key=true
fi

if [ "$is_real_account" = true ] && [ "$has_private_key" = true ]; then
  printf '%s\n' "$SNOWFLAKE_PRIVATE_KEY" > "$KEY_PATH"
  chmod 600 "$KEY_PATH"
  configured=true
  echo "Snowflake credentials detected — dbt build will run against ${SNOWFLAKE_ACCOUNT}"
else
  cat > "$KEY_PATH" <<'EOF'
-----BEGIN PRIVATE KEY-----
PLACEHOLDER — add SNOWFLAKE_ACCOUNT and SNOWFLAKE_PRIVATE_KEY secrets to deploy
-----END PRIVATE KEY-----
EOF
  chmod 600 "$KEY_PATH"
  configured=false
  echo "::notice title=Placeholder mode::Snowflake secrets not configured. Running dbt validation only (deps/parse/compile). Add SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, and SNOWFLAKE_PRIVATE_KEY secrets to enable dbt build."
fi

if [ -n "$OUTPUT" ]; then
  echo "snowflake_configured=$configured" >> "$OUTPUT"
fi

# Export resolved values for subsequent steps
if [ -n "${GITHUB_ENV:-}" ]; then
  {
    echo "SNOWFLAKE_ACCOUNT=$SNOWFLAKE_ACCOUNT"
    echo "SNOWFLAKE_USER=$SNOWFLAKE_USER"
    echo "SNOWFLAKE_ROLE=$SNOWFLAKE_ROLE"
    echo "SNOWFLAKE_PRIVATE_KEY_PATH=$KEY_PATH"
  } >> "$GITHUB_ENV"
fi
