.PHONY: clean lint format check test build

clean:
	rm -rf dist
	rm -rf .ruff_cache
	rm -rf .pytest_cache
	rm -rf .coverage

lint:
	uv run ruff check . --fix

format:
	uv run ruff format .

check: lint format

test:
	uv run pytest

build:
	uv build
