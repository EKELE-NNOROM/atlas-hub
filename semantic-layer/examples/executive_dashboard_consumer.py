# Example consumer — Executive dashboard fetches ARR via Metrics API

import os
import requests

API_BASE = os.environ.get("ATLAS_METRICS_API", "https://metrics.internal.company.com")
TOKEN = os.environ.get("ATLAS_API_TOKEN")


def fetch_arr() -> list[dict]:
    resp = requests.get(
        f"{API_BASE}/metrics/arr",
        headers={"Authorization": f"Bearer {TOKEN}"},
        params={"grain": "month"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["data"]


def fetch_pipeline() -> list[dict]:
    resp = requests.get(
        f"{API_BASE}/metrics/pipeline_value",
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["data"]


if __name__ == "__main__":
    arr = fetch_arr()
    print(f"Latest ARR: ${arr[-1]['value']:,.0f}")
