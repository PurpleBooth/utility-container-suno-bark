PHONY: fmt
fmt:
	poetry run python -m ruff check . --fix
	poetry run python -m isort .
	poetry run python -m black .

PHONY: lint
lint:
	poetry run python -m ruff check .
	poetry run python -m isort . --check
	poetry run python -m black . --check
	poetry run python -m mypy .

PHONY: test
test:
	poetry run python -m pytest tests