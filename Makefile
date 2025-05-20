.PHONY: all clean lint format check test build install_dev install tool

install_dev:
	uv sync --dev

install:
	uv sync

tool:
	uv tool install . --reinstall

clean:
	rm -rf dist
	rm -rf .ruff_cache
	rm -rf .pytest_cache

lint:
	uv run ruff check . --fix
	uv run ty check src/

format:
	uv run ruff format .

check: lint format

test:
	uv run pytest

build: clean check
	uv build
