FROM ghcr.io/dbt-labs/dbt-snowflake:1.7.4

WORKDIR /usr/app/dbt

# Install project dependencies at build time (project files mounted at runtime)
COPY dbt/packages.yml dbt/dbt_project.yml ./
RUN dbt deps || true

COPY docker/dbt/profiles.docker.yml /root/.dbt/profiles.yml

ENTRYPOINT ["dbt"]
CMD ["--help"]
