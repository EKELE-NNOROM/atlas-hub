"""Atlas Hub Semantic Metrics API.

This module implements the **consumption layer** for enterprise KPIs. It is *not*
the dbt Semantic Layer runtime (MetricFlow). Metric *definitions* live in dbt;
this service *serves* time-series values over HTTP.

Architecture
------------
The platform splits semantic concerns into two layers:

1. **Definition (dbt)** — ``dbt/models/semantic/``
   - SQL models (``semantic__revenue_kpis``, etc.) project marts into metric-ready tables.
   - ``_semantic_models.yml`` declares ``semantic_models``, ``measures``, and ``metrics``
     (ARR, MRR, CAC, ROAS, …) for ``dbt parse`` / MetricFlow compatibility.
   - Derived metrics (e.g. ``cac``, ``gross_margin_pct``) exist in YAML but are **not**
     exposed by this API yet.

2. **Serving (this file)** — ``semantic-layer/api/main.py``
   - FastAPI app that returns JSON time series for approved metrics.
   - **Does not** call MetricFlow or dbt at request time.
   - **Snowflake mode:** runs hand-authored SQL in ``METRIC_QUERIES`` against tables
     built by dbt (``ANALYTICS_{env}.SEMANTIC.*``).
   - **Mock mode:** returns static samples from ``MOCK_METRICS`` (no warehouse).

Data flow (production)::

    Sources → dbt marts → semantic__* models → Snowflake tables
                                                    ↓
                              GET /metrics/{name} ← METRIC_QUERIES (this API)

Endpoints
---------
- ``GET /health`` — Liveness; reports ``mock`` vs ``snowflake`` mode.
- ``GET /metrics`` — Lists metric names the caller's JWT scopes may access.
- ``GET /metrics/{metric_name}?grain=month`` — Time series for one metric.

Configuration
-------------
Environment variables use prefix ``ATLAS_`` (see ``Settings``). Common local setup::

    ATLAS_MOCK_DATA=true
    ATLAS_DISABLE_AUTH=true

Docker maps these from ``.env`` (see repo root ``.env.example``). Native Windows::

    .\\scripts\\run-metrics-api-local.ps1

Snowflake connectivity requires ``ATLAS_SNOWFLAKE_ACCOUNT`` plus password or
``ATLAS_SNOWFLAKE_PRIVATE_KEY_PATH``. The connector uses role ``ATLAS_API_SERVICE``
(see ``snowflake/rbac/roles_grants.sql``).

Security
--------
When auth is enabled, clients send ``Authorization: Bearer <JWT>``. Tokens must
include claims ``sub``, ``exp``, and ``scopes`` (list of strings). ``METRIC_SCOPES``
maps each metric to allowed scopes (``finance``, ``sales``, ``product``, etc.).

Known limitations
-----------------
- ``grain`` query parameter is accepted but **not applied** to SQL (reserved for future use).
- API exposes 7 metrics; dbt YAML defines additional metrics not yet wired here.
- ``win_rate`` queries ``MART_SALES__WIN_RATE`` directly, not a semantic model table.

Further reading
---------------
- ADR: ``docs/production-readiness/adrs/006-semantic-layer-api.md``
- dbt semantic YAML: ``dbt/models/semantic/_semantic_models.yml``
- Docker / mock runbook: ``docs/docker/README.md``
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import snowflake.connector
from fastapi import Depends, FastAPI, HTTPException, Query, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

#: Snowflake SQL templates keyed by metric name exposed on ``GET /metrics/{name}``.
#:
#: Each query must return two columns: ``period`` (date/time bucket) and ``value`` (numeric).
#: The placeholder ``{env}`` is replaced at runtime with ``settings.environment.upper()``
#: (e.g. ``DEV`` → database ``ANALYTICS_DEV``).
#:
#: Tables are materialized by dbt models under ``dbt/models/semantic/`` except
#: ``win_rate``, which reads ``MART_SALES__WIN_RATE`` directly.
#:
#: Metrics defined only in ``_semantic_models.yml`` (CAC, ROAS, gross_margin_pct, …)
#: are intentionally omitted until corresponding queries are added here.
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

#: Static time-series returned when ``Settings.mock_data`` is ``True``.
#:
#: Shape matches Snowflake query output after normalization in ``fetch_metric_data``:
#: each row has ``period`` (ISO date string), ``value`` (float), and ``currency`` (always ``USD``).
#: Used for local demos without Fivetran, dbt build, or Snowflake credentials.
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

#: Authorization map from metric name → JWT scope names allowed to read that metric.
#:
#: A user may access a metric if **any** scope in their JWT ``scopes`` list appears in the
#: metric's allowed list. ``executive`` and ``admin`` scopes are included on most metrics
#: so leadership and platform admins can query cross-domain KPIs.
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
    """Application configuration loaded from environment variables.

    All fields are populated from env vars prefixed with ``ATLAS_`` (case-insensitive).
    Docker Compose and ``.env`` set these for local development.

    Attributes:
        snowflake_account: Snowflake account identifier (e.g. ``xy12345.us-east-1``).
            Required for live queries; omit or leave empty only in mock mode.
        snowflake_user: Snowflake login user. Defaults to service user ``SVC_METRICS_API_PROD``.
        snowflake_password: Password auth (dev only). Mutually preferred after key-pair in prod.
        snowflake_private_key_path: Path to PEM private key for key-pair authentication.
        snowflake_warehouse: Warehouse used for metric queries (e.g. ``WH_BI_DEV``).
        environment: Logical env name (``dev``, ``staging``, ``prod``). Drives ``ANALYTICS_{ENV}``
            database substitution in ``METRIC_QUERIES``.
        jwt_secret: HMAC secret for validating JWTs when auth is enabled.
        mock_data: If ``True``, skip Snowflake and serve ``MOCK_METRICS`` (``ATLAS_MOCK_DATA``).
        disable_auth: If ``True``, ``verify_token`` returns a synthetic admin principal
            (``ATLAS_DISABLE_AUTH``).
    """

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


#: Process-wide settings singleton; read by helpers and route handlers.
settings = Settings()

#: FastAPI security scheme for optional Bearer JWT in the ``Authorization`` header.
#: ``auto_error=False`` allows ``verify_token`` to return 401 with a clear message
#: instead of FastAPI's default 403 when the header is missing.
security = HTTPBearer(auto_error=False)


class MetricResponse(BaseModel):
    """JSON body for ``GET /metrics/{metric_name}``.

    Attributes:
        metric: Canonical metric slug (e.g. ``arr``, ``mrr``).
        grain: Requested time grain from query param (metadata only today; SQL ignores it).
        data: List of points, each with ``period``, ``value``, and ``currency``.
        metadata: Provenance including ``source`` (``mock`` | ``snowflake``), ``generated_at``,
            ``requested_by`` (JWT ``sub``), and ``definition_version``.
    """

    metric: str
    grain: str
    data: list[dict[str, Any]]
    metadata: dict[str, Any]


class HealthResponse(BaseModel):
    """JSON body for ``GET /health``.

    Attributes:
        status: Always ``ok`` when the process is running.
        environment: Copy of ``settings.environment``.
        mode: ``mock`` if ``settings.mock_data`` else ``snowflake``.
    """

    status: str
    environment: str
    mode: str


def get_snowflake_connection() -> snowflake.connector.SnowflakeConnection:
    """Open a new Snowflake connection using ``settings``.

    Uses role ``ATLAS_API_SERVICE`` (must be granted to ``settings.snowflake_user``).
    Prefers key-pair auth when ``snowflake_private_key_path`` is set; otherwise password.

    Returns:
        An open ``snowflake.connector`` connection. Caller must close it.

    Raises:
        HTTPException: 503 if account or credentials are missing/invalid.
    """
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
    """FastAPI dependency: authenticate the request and return JWT claims.

    When ``settings.disable_auth`` is true (local mock), returns a synthetic user with
    all scopes so every metric is reachable without a token.

    Args:
        credentials: Bearer token extracted by ``HTTPBearer``, or ``None`` if absent.

    Returns:
        Decoded JWT payload dict. Expected keys: ``sub`` (user id), ``scopes`` (list[str]),
        and ``exp`` (expiry) when auth is enabled.

    Raises:
        HTTPException: 401 if auth is required and the header/token is missing or invalid.
    """
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
    """Enforce that ``user`` may read ``metric`` per ``METRIC_SCOPES``.

    Args:
        metric: Metric slug from the URL path.
        user: JWT payload from ``verify_token``; uses ``user["scopes"]``.

    Raises:
        HTTPException: 403 if no scope overlap between user and metric.
    """
    allowed = METRIC_SCOPES.get(metric, [])
    user_scopes = user.get("scopes", [])
    if not any(s in user_scopes for s in allowed):
        raise HTTPException(status_code=403, detail=f"Insufficient scope for metric: {metric}")


def fetch_metric_data(metric_name: str) -> list[dict[str, Any]]:
    """Load time-series rows for a single metric.

    Dispatches to ``MOCK_METRICS`` or Snowflake based on ``settings.mock_data``.
    Snowflake results are normalized to the same dict shape as mock rows.

    Args:
        metric_name: Key present in ``METRIC_QUERIES`` / ``MOCK_METRICS``.

    Returns:
        List of ``{"period": str, "value": float, "currency": "USD"}`` dicts.
        Empty list if mock mode and the metric has no mock data.

    Raises:
        KeyError: Not raised; callers should validate ``metric_name`` before calling.
        Propagates Snowflake/driver errors if the warehouse query fails.
    """
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
    """FastAPI lifespan hook (startup/shutdown).

    Currently a no-op placeholder. Use for connection pools, cache warm-up, or
    graceful shutdown of background tasks if added later.

    Args:
        app: The FastAPI application instance.

    Yields:
        Control to the running application between startup and shutdown.
    """
    yield


#: Root ASGI application. Served by uvicorn (Docker or ``run-metrics-api-local.ps1``).
app = FastAPI(
    title="Atlas Hub Metrics API",
    version="1.0.0",
    description="Semantic layer REST API for enterprise KPIs",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness and configuration probe for load balancers and Docker healthchecks.

    Returns:
        ``HealthResponse`` with ``status="ok"`` and current ``mode``/``environment``.
    """
    mode = "mock" if settings.mock_data else "snowflake"
    return HealthResponse(status="ok", environment=settings.environment, mode=mode)


@app.get("/metrics/{metric_name}", response_model=MetricResponse)
async def get_metric(
    metric_name: str,
    grain: str = Query("month", enum=["day", "week", "month", "quarter"]),
    user: dict = Depends(verify_token),
) -> MetricResponse:
    """Return a time series for one KPI.

    Args:
        metric_name: Slug matching a key in ``METRIC_QUERIES`` (e.g. ``arr``).
        grain: Desired aggregation grain (reserved; not yet applied to SQL).
        user: Injected JWT claims from ``verify_token``.

    Returns:
        ``MetricResponse`` with data points and metadata.

    Raises:
        HTTPException: 404 unknown metric; 403 insufficient scope; 401/503 via dependencies.
    """
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
async def list_metrics(user: dict = Depends(verify_token)) -> dict[str, list[str]]:
    """List metric names the authenticated principal is allowed to query.

    Filters ``METRIC_SCOPES`` keys by overlap with ``user["scopes"]``.

    Args:
        user: Injected JWT claims from ``verify_token``.

    Returns:
        ``{"metrics": ["arr", "mrr", ...]}`` sorted implicitly by dict iteration order.
    """
    scopes = user.get("scopes", [])
    available = [
        m for m, required in METRIC_SCOPES.items()
        if any(s in scopes for s in required)
    ]
    return {"metrics": available}
