# dbt — Atlas Hub

## CI without Snowflake credentials

Pull requests and pushes to `main` **pass without secrets**. CI runs:

- `dbt deps`
- `dbt parse`
- `dbt compile`
- SQL lint (PRs)

`dbt build` runs only when these GitHub secrets are set:

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
