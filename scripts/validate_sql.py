"""Basic SQL file syntax validation using sqlglot.

Note: sqlglot does not fully support Snowflake governance DDL (masking policies,
row access policies). Those files are skipped and should be validated when
executed in Snowflake.
"""

import sys
from pathlib import Path

import sqlglot

# Files with Snowflake-specific DDL that sqlglot cannot parse
SKIP_FILES = {
    "masking_rls_audit.sql",
}

# Skip any file containing these constructs (alternative to filename list)
SKIP_IF_CONTAINS = (
    "ROW ACCESS POLICY",
    "CREATE OR REPLACE MASKING POLICY",
    "CREATE MASKING POLICY",
)

dialect = "snowflake" if "snowflake" in sys.argv[1] else "bigquery"
root = Path(__file__).parent.parent / sys.argv[1]

errors = []
validated = 0
skipped = []

for sql_file in sorted(root.rglob("*.sql")):
    content = sql_file.read_text(encoding="utf-8")

    if sql_file.name in SKIP_FILES or any(s in content for s in SKIP_IF_CONTAINS):
        skipped.append(sql_file.relative_to(root))
        continue

    try:
        sqlglot.parse(content, read=dialect)
        validated += 1
    except Exception as e:
        errors.append(f"{sql_file}: {e}")

if skipped:
    print(f"Skipped {len(skipped)} file(s) (Snowflake policy DDL not supported by sqlglot):")
    for path in skipped:
        print(f"  - {path}")

if errors:
    for err in errors:
        print(err)
    sys.exit(1)

print(f"Validated {validated} SQL file(s)")
