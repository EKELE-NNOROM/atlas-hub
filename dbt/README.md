# dbt — Atlas Hub

## CI without Snowflake credentials

Pull requests and pushes to `main` run **`dbt deps`** and **`dbt parse`** only — no warehouse connection needed.

`dbt compile` / `dbt build` run when these GitHub secrets are set (via **Actions → Deploy (manual)** or if added to the CI workflow):

| Secret | Example |
|--------|---------|
| `SNOWFLAKE_ACCOUNT` | `xy12345.us-east-1` |
| `SNOWFLAKE_USER` | `SVC_DBT_PROD` or CI user |
| `SNOWFLAKE_PRIVATE_KEY` | PEM key contents |

Placeholder profile values (in `profiles.ci.yml`):

| Setting | Placeholder |
|---------|-------------|
| Account | `placeholder.us-east-1` |
| User | `PLACEHOLDER_DBT_USER` |
| Database | `ANALYTICS_DEV` / `ANALYTICS_PROD` |
| Warehouse | `WH_ETL_DEV` / `WH_ETL_PROD` |

## Local development

```bash
cp profiles.yml.example ~/.dbt/profiles.yml
dbt deps && dbt build --target dev
```

Or use Docker: [docs/docker/README.md](../docs/docker/README.md)

## Dev without Fivetran (sample seeds)

Sample CSV seeds live in [`seeds/`](seeds/). They let you materialize marts and semantic models on Snowflake without connectors:

```powershell
cd dbt
dbt deps
dbt build --vars "{use_seeds: true}" --target dev
```

See [seeds/README.md](seeds/README.md) for file list, prerequisites, and verification queries.
