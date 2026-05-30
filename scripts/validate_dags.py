"""Validate Airflow DAGs import without syntax errors."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "airflow" / "dags"))
sys.path.insert(0, str(Path(__file__).parent.parent / "airflow" / "plugins"))

from airflow.models import DagBag

dag_folder = Path(__file__).parent.parent / "airflow" / "dags"
dag_bag = DagBag(dag_folder=str(dag_folder), include_examples=False)

if dag_bag.import_errors:
    for filename, error in dag_bag.import_errors.items():
        print(f"DAG import error in {filename}: {error}")
    sys.exit(1)

print(f"Successfully imported {len(dag_bag.dags)} DAGs")
