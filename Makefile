.PHONY: help install update check format lint type-check pre-commit clean

help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies using uv"
	@echo "  check        - Run all checks (format, lint, type-check)"
	@echo "  format       - Format code using ruff"
	@echo "  lint         - Lint code using ruff"
	@echo "  type-check   - Type check code using mypy"
	@echo "  pre-commit   - Run pre-commit on all files"
	@echo "  clean        - Remove temporary files and caches"

install:
	uv sync
	uv run pre-commit install

format:
	uv run ruff format .

lint:
	uv run ruff check . --fix

type-check:
	uv run mypy src

check: format lint type-check

pre-commit:
	uv run pre-commit run --all-files

clean:
	rm -rf .venv
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
