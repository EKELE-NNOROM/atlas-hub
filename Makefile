.PHONY: up down build logs dbt-build dbt-shell airflow-up token help

help:
	@echo "Atlas Hub Docker commands:"
	@echo "  make up          Start metrics API (mock mode)"
	@echo "  make down        Stop all services"
	@echo "  make build       Rebuild images"
	@echo "  make dbt-build   Run dbt build in container"
	@echo "  make dbt-shell   Interactive dbt shell"
	@echo "  make airflow-up  Start Airflow stack"
	@echo "  make token       Generate dev JWT"

up:
	docker compose up -d --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f metrics-api

dbt-build:
	docker compose --profile tools run --rm dbt build --target docker

dbt-shell:
	docker compose --profile tools run --rm dbt-shell

airflow-up:
	docker compose --profile airflow up -d --build

token:
	python docker/scripts/generate-dev-token.py
