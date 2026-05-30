"""Atlas Hub Semantic Metrics API — serves dbt-defined KPIs to internal consumers."""

from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
from typing import Any

import snowflake.connector
from fastapi import Depends, FastAPI, HTTPException, Query, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from pydantic_settings import BaseSettings

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
    snowflake_account: str
    snowflake_user: str = "SVC_METRICS_API_PROD"
    snowflake_private_key_path: str
    snowflake_warehouse: str = "WH_BI_PROD"
    environment: str = "prod"
    jwt_secret: str  # Validate tokens from internal IdP

    class Config:
        env_prefix = "ATLAS_"


settings = Settings()
security = HTTPBearer()


class MetricResponse(BaseModel):
    metric: str
    grain: str
    data: list[dict[str, Any]]
    metadata: dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    environment: str


def get_snowflake_connection():
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
    return snowflake.connector.connect(
        account=settings.snowflake_account,
        user=settings.snowflake_user,
        private_key=pkb,
        warehouse=settings.snowflake_warehouse,
        role="ATLAS_API_SERVICE",
    )


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Validate JWT from Okta/Auth0; decode scopes for RBAC."""
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
    return HealthResponse(status="ok", environment=settings.environment)


@app.get("/metrics/{metric_name}", response_model=MetricResponse)
async def get_metric(
    metric_name: str,
    grain: str = Query("month", enum=["day", "week", "month", "quarter"]),
    user: dict = Depends(verify_token),
):
    if metric_name not in METRIC_QUERIES:
        raise HTTPException(status_code=404, detail=f"Unknown metric: {metric_name}")

    require_scope(metric_name, user)

    sql = METRIC_QUERIES[metric_name].format(env=settings.environment.upper())
    conn = get_snowflake_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        data = [{"period": str(r[0]), "value": float(r[1]), "currency": "USD"} for r in rows]
    finally:
        conn.close()

    return MetricResponse(
        metric=metric_name,
        grain=grain,
        data=data,
        metadata={
            "definition_version": "1.0.0",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "requested_by": user.get("sub"),
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
