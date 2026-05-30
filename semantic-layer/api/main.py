"""Atlas Hub Semantic Metrics API — serves dbt-defined KPIs to internal consumers."""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import snowflake.connector
from fastapi import Depends, FastAPI, HTTPException, Query, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

METRIC_QUERIES: dict[str, str] = {
    "arr": """
        SELECT revenue_month AS period, SUM(arr_usd) AS value
        FROM ANALYTICS_{env}.SEMANTIC.SEMANTIC__REVENUE_KPIS
        GROUP BY 1 ORDER BY 1
    """,
    "mrr": """
        SELECT revenue_month AS period, SUM(mrr_usd) AS value
        FROM ANALYTICS_{env}.SEMANTIC.SEMANTIC__REVENUE_KPIS
        GROUP BY 1 ORDER BY 1
    """,
    "pipeline_value": """
        SELECT snapshot_date AS period, SUM(amount_usd) AS value
        FROM ANALYTICS_{env}.SEMANTIC.SEMANTIC__SALES_KPIS
        GROUP BY 1 ORDER BY 1
    """,
    "win_rate": """
        SELECT fiscal_quarter AS period, win_rate AS value
        FROM ANALYTICS_{env}.MART_SALES.MART_SALES__WIN_RATE
        ORDER BY 1
    """,
    "dau": """
        SELECT activity_date AS period, dau AS value
        FROM ANALYTICS_{env}.SEMANTIC.SEMANTIC__PRODUCT_KPIS
        ORDER BY 1
    """,
    "mau": """
        SELECT activity_date AS period, mau AS value
        FROM ANALYTICS_{env}.SEMANTIC.SEMANTIC__PRODUCT_KPIS
        ORDER BY 1
    """,
    "headcount": """
        SELECT activity_month AS period, headcount AS value
        FROM ANALYTICS_{env}.SEMANTIC.SEMANTIC__HR_KPIS
        ORDER BY 1
    """,
}

MOCK_METRICS: dict[str, list[dict[str, Any]]] = {
    "arr": [
        {"period": "2026-03-01", "value": 11800000.0, "currency": "USD"},
        {"period": "2026-04-01", "value": 12500000.0, "currency": "USD"},
        {"period": "2026-05-01", "value": 13100000.0, "currency": "USD"},
    ],
    "mrr": [
        {"period": "2026-03-01", "value": 983333.33, "currency": "USD"},
        {"period": "2026-04-01", "value": 1041666.67, "currency": "USD"},
        {"period": "2026-05-01", "value": 1091666.67, "currency": "USD"},
    ],
    "pipeline_value": [
        {"period": "2026-05-28", "value": 4200000.0, "currency": "USD"},
        {"period": "2026-05-29", "value": 4350000.0, "currency": "USD"},
        {"period": "2026-05-30", "value": 4500000.0, "currency": "USD"},
    ],
    "win_rate": [
        {"period": "2026-01-01", "value": 0.26, "currency": "USD"},
        {"period": "2026-04-01", "value": 0.28, "currency": "USD"},
    ],
    "dau": [
        {"period": "2026-05-28", "value": 8420.0, "currency": "USD"},
        {"period": "2026-05-29", "value": 8610.0, "currency": "USD"},
        {"period": "2026-05-30", "value": 8780.0, "currency": "USD"},
    ],
    "mau": [
        {"period": "2026-05-28", "value": 42100.0, "currency": "USD"},
        {"period": "2026-05-29", "value": 42350.0, "currency": "USD"},
        {"period": "2026-05-30", "value": 42600.0, "currency": "USD"},
    ],
    "headcount": [
        {"period": "2026-03-01", "value": 142.0, "currency": "USD"},
        {"period": "2026-04-01", "value": 148.0, "currency": "USD"},
        {"period": "2026-05-01", "value": 155.0, "currency": "USD"},
    ],
}

METRIC_SCOPES: dict[str, list[str]] = {
    "arr": ["finance", "executive", "admin"],
    "mrr": ["finance", "executive", "admin"],
    "pipeline_value": ["sales", "executive", "admin"],
    "win_rate": ["sales", "executive", "admin"],
    "dau": ["product", "executive", "admin"],
    "mau": ["product", "executive", "admin"],
    "headcount": ["hr", "executive", "admin"],
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ATLAS_")

    snowflake_account: str | None = None
    snowflake_user: str = "SVC_METRICS_API_PROD"
    snowflake_password: str | None = None
    snowflake_private_key_path: str | None = None
    snowflake_warehouse: str = "WH_BI_DEV"
    environment: str = "dev"
    jwt_secret: str = "local-dev-secret-change-me"
    mock_data: bool = False
    disable_auth: bool = False


settings = Settings()
security = HTTPBearer(auto_error=False)


class MetricResponse(BaseModel):
    metric: str
    grain: str
    data: list[dict[str, Any]]
    metadata: dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    environment: str
    mode: str


def get_snowflake_connection():
    if not settings.snowflake_account:
        raise HTTPException(status_code=503, detail="Snowflake not configured")

    connect_kwargs: dict[str, Any] = {
        "account": settings.snowflake_account,
        "user": settings.snowflake_user,
        "warehouse": settings.snowflake_warehouse,
        "role": "ATLAS_API_SERVICE",
    }

    if settings.snowflake_private_key_path:
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import serialization

        with open(settings.snowflake_private_key_path, "rb") as key_file:
            pkey = serialization.load_pem_private_key(
                key_file.read(), password=None, backend=default_backend()
            )
        pkb = pkey.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        connect_kwargs["private_key"] = pkb
    elif settings.snowflake_password:
        connect_kwargs["password"] = settings.snowflake_password
    else:
        raise HTTPException(status_code=503, detail="Snowflake credentials not configured")

    return snowflake.connector.connect(**connect_kwargs)


def verify_token(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
) -> dict:
    if settings.disable_auth:
        return {
            "sub": "dev@local",
            "scopes": ["admin", "finance", "sales", "product", "hr", "executive"],
        }

    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization header required")

    import jwt

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=["HS256"],
            options={"require": ["exp", "sub", "scopes"]},
        )
        return payload
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


def require_scope(metric: str, user: dict) -> None:
    allowed = METRIC_SCOPES.get(metric, [])
    user_scopes = user.get("scopes", [])
    if not any(s in user_scopes for s in allowed):
        raise HTTPException(status_code=403, detail=f"Insufficient scope for metric: {metric}")


def fetch_metric_data(metric_name: str) -> list[dict[str, Any]]:
    if settings.mock_data:
        return MOCK_METRICS.get(metric_name, [])

    sql = METRIC_QUERIES[metric_name].format(env=settings.environment.upper())
    conn = get_snowflake_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return [{"period": str(r[0]), "value": float(r[1]), "currency": "USD"} for r in rows]
    finally:
        conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Atlas Hub Metrics API",
    version="1.0.0",
    description="Semantic layer REST API for enterprise KPIs",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
async def health():
    mode = "mock" if settings.mock_data else "snowflake"
    return HealthResponse(status="ok", environment=settings.environment, mode=mode)


@app.get("/metrics/{metric_name}", response_model=MetricResponse)
async def get_metric(
    metric_name: str,
    grain: str = Query("month", enum=["day", "week", "month", "quarter"]),
    user: dict = Depends(verify_token),
):
    if metric_name not in METRIC_QUERIES:
        raise HTTPException(status_code=404, detail=f"Unknown metric: {metric_name}")

    require_scope(metric_name, user)
    data = fetch_metric_data(metric_name)

    return MetricResponse(
        metric=metric_name,
        grain=grain,
        data=data,
        metadata={
            "definition_version": "1.0.0",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "requested_by": user.get("sub"),
            "source": "mock" if settings.mock_data else "snowflake",
        },
    )


@app.get("/metrics")
async def list_metrics(user: dict = Depends(verify_token)):
    scopes = user.get("scopes", [])
    available = [
        m for m, required in METRIC_SCOPES.items()
        if any(s in scopes for s in required)
    ]
    return {"metrics": available}
