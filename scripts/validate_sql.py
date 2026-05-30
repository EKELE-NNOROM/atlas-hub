"""Basic SQL file syntax validation using sqlglot."""

import sys
from pathlib import Path

import sqlglot

dialect = "snowflake" if "snowflake" in sys.argv[1] else "bigquery"
root = Path(__file__).parent.parent / sys.argv[1]

errors = []
for sql_file in root.rglob("*.sql"):
    try:
        sqlglot.parse(sql_file.read_text(), read=dialect)
    except Exception as e:
        errors.append(f"{sql_file}: {e}")

if errors:
    for err in errors:
        print(err)
    sys.exit(1)

print(f"Validated {len(list(root.rglob('*.sql')))} SQL files")
