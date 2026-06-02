-- Data masking, row access policies, and tagging
-- CI note: excluded from sqlglot validation (Snowflake-specific policy syntax).
-- Run this script directly in Snowflake when credentials are configured.

-- =============================================================================
-- TAGS (Governance)
-- =============================================================================

CREATE TAG IF NOT EXISTS GOVERNANCE_PROD.AUDIT.CLASSIFICATION
  ALLOWED_VALUES 'public', 'internal', 'confidential', 'pii', 'financial';

CREATE TAG IF NOT EXISTS GOVERNANCE_PROD.AUDIT.DATA_DOMAIN
  ALLOWED_VALUES 'finance', 'sales', 'marketing', 'product', 'hr', 'legal';

-- =============================================================================
-- MASKING POLICIES
-- =============================================================================

CREATE OR REPLACE MASKING POLICY GOVERNANCE_PROD.AUDIT.MASK_EMAIL AS (val STRING)
  RETURNS STRING ->
    CASE
      WHEN CURRENT_ROLE() IN ('ATLAS_HR', 'ATLAS_ADMIN', 'ATLAS_ENGINEER') THEN val
      ELSE REGEXP_REPLACE(val, '.+@', '***@')
    END;

CREATE OR REPLACE MASKING POLICY GOVERNANCE_PROD.AUDIT.MASK_PHONE AS (val STRING)
  RETURNS STRING ->
    CASE
      WHEN CURRENT_ROLE() IN ('ATLAS_HR', 'ATLAS_ADMIN') THEN val
      ELSE '***-***-' || RIGHT(val, 4)
    END;

CREATE OR REPLACE MASKING POLICY GOVERNANCE_PROD.AUDIT.MASK_SALARY AS (val NUMBER)
  RETURNS NUMBER ->
    CASE
      WHEN CURRENT_ROLE() IN ('ATLAS_HR', 'ATLAS_FINANCE', 'ATLAS_ADMIN') THEN val
      ELSE NULL
    END;

CREATE OR REPLACE MASKING POLICY GOVERNANCE_PROD.AUDIT.MASK_EMPLOYEE_ID AS (val STRING)
  RETURNS STRING ->
    CASE
      WHEN CURRENT_ROLE() IN ('ATLAS_HR', 'ATLAS_ADMIN') THEN val
      ELSE SHA2(val, 256)
    END;

-- Apply to HR mart columns (run after dbt creates tables)
-- ALTER TABLE ANALYTICS_PROD.MART_HR.EMPLOYEE_DIM MODIFY COLUMN email SET MASKING POLICY GOVERNANCE_PROD.AUDIT.MASK_EMAIL;

-- =============================================================================
-- ROW ACCESS POLICIES — Sales territory
-- =============================================================================

CREATE OR REPLACE ROW ACCESS POLICY GOVERNANCE_PROD.AUDIT.SALES_TERRITORY_RLS AS (territory_id VARCHAR)
  RETURNS BOOLEAN ->
    CURRENT_ROLE() IN ('ATLAS_ADMIN', 'ATLAS_ENGINEER', 'ATLAS_FINANCE')
    OR territory_id IN (
      SELECT territory_id
      FROM ANALYTICS_PROD.MART_SALES.USER_TERRITORY_MAP
      WHERE user_email = CURRENT_USER()
    );

-- =============================================================================
-- AUDIT — Access history export (scheduled task)
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS GOVERNANCE_PROD.AUDIT;

CREATE TABLE IF NOT EXISTS GOVERNANCE_PROD.AUDIT.QUERY_ACCESS_LOG (
  log_id STRING DEFAULT UUID_STRING(),
  query_id STRING,
  user_name STRING,
  role_name STRING,
  warehouse_name STRING,
  query_text STRING,
  database_name STRING,
  schema_name STRING,
  objects_accessed VARIANT,
  query_start_time TIMESTAMP_LTZ,
  loaded_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Task runs daily to capture sensitive object access
CREATE OR REPLACE TASK GOVERNANCE_PROD.AUDIT.TASK_EXPORT_ACCESS_HISTORY
  WAREHOUSE = WH_ETL_PROD
  SCHEDULE = 'USING CRON 0 7 * * * America/New_York'
AS
  INSERT INTO GOVERNANCE_PROD.AUDIT.QUERY_ACCESS_LOG (
    query_id, user_name, role_name, warehouse_name, query_text,
    database_name, schema_name, objects_accessed, query_start_time
  )
  SELECT
    query_id,
    user_name,
    role_name,
    warehouse_name,
    LEFT(query_text, 10000),
    database_name,
    schema_name,
    objects_accessed,
    start_time
  FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY
  WHERE start_time >= DATEADD('day', -1, CURRENT_TIMESTAMP())
    AND objects_accessed IS NOT NULL;

ALTER TASK GOVERNANCE_PROD.AUDIT.TASK_EXPORT_ACCESS_HISTORY RESUME;
