-- BigQuery: Product event analytics (GCP-native workloads)
-- Dataset: atlas_events_{env}

CREATE SCHEMA IF NOT EXISTS `atlas-analytics-prod.atlas_events_prod`
OPTIONS (
  description = 'High-volume product usage events',
  location = 'us-central1'
);

-- Raw events from GA4 export + SDK streaming
CREATE TABLE IF NOT EXISTS `atlas-analytics-prod.atlas_events_prod.events`
(
  event_id STRING NOT NULL,
  event_timestamp TIMESTAMP NOT NULL,
  event_name STRING NOT NULL,
  user_id STRING,
  account_id STRING,
  session_id STRING,
  platform STRING,
  app_version STRING,
  geo_country STRING,
  event_params JSON,
  user_properties JSON,
  _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(event_timestamp)
CLUSTER BY event_name, account_id
OPTIONS (
  description = 'Product usage events — partition prune by date',
  require_partition_filter = TRUE
);

-- Daily engagement aggregate (exported to S3 → Snowflake)
CREATE OR REPLACE TABLE `atlas-analytics-prod.atlas_events_prod.daily_engagement`
PARTITION BY activity_date AS
SELECT
  DATE(event_timestamp) AS activity_date,
  account_id,
  COUNT(DISTINCT user_id) AS dau,
  COUNT(*) AS event_count,
  COUNT(DISTINCT session_id) AS sessions,
  ARRAY_AGG(DISTINCT event_name IGNORE NULLS) AS features_used
FROM `atlas-analytics-prod.atlas_events_prod.events`
WHERE DATE(event_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  AND account_id IS NOT NULL
  AND event_name NOT IN ('session_start', 'first_open')
GROUP BY 1, 2;

-- Feature adoption: event-level analysis at scale
CREATE OR REPLACE VIEW `atlas-analytics-prod.atlas_events_prod.feature_adoption_daily` AS
SELECT
  DATE(event_timestamp) AS activity_date,
  event_name AS feature_name,
  COUNT(DISTINCT user_id) AS feature_users,
  COUNT(DISTINCT account_id) AS accounts_using
FROM `atlas-analytics-prod.atlas_events_prod.events`
WHERE DATE(event_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY 1, 2;

-- Cross-cloud: scheduled export to GCS then S3 for Snowflake
-- Run via Airflow BigQueryInsertJobOperator + transfer service
