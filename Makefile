.PHONY: install lint test format serve docs clean

install:
	poetry install

lint:
	poetry run ruff check src/ tests/
	poetry run mypy src/

format:
	poetry run ruff format src/ tests/
	poetry run ruff check --fix src/ tests/

test:
	poetry run pytest tests/ -v --cov=src --cov-report=term-missing

test-unit:
	poetry run pytest tests/unit/ -v

test-integration:
	poetry run pytest tests/integration/ -v

serve:
	poetry run neuralscope serve

docs:
	poetry run mkdocs serve

docker-up:
	docker compose up -d

docker-down:
	docker compose down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	rm -rf .mypy_cache .ruff_cache dist htmlcov
