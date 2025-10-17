.PHONY: run worker beat migrate upgrade seed test fmt lint

run:
	flask --app wsgi:app run --port 8000

worker:
	celery -A celery_app.celery_app worker -l info

beat:
	celery -A celery_app.celery_app beat -l info

migrate:
	alembic revision --autogenerate -m "auto"

upgrade:
	alembic upgrade head

seed:
	python scripts/seed_parameters.py

test:
	pytest -q

fmt:
	python -m black app tests

lint:
	flake8 app tests