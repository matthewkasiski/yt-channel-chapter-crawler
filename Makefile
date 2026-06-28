.PHONY: install install-dev test format lint clean uninstall coverage

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

format:
	black src tests

lint:
	black --check src tests
	ruff check src tests

coverage:
	pytest --cov=src --cov-report=term-missing --cov-fail-under=80

test: install-dev format lint coverage

build:
	pip install build
	python -m build

uninstall:
	pip uninstall -y yt-ccc

clean: uninstall
	rm -rf build dist src/*.egg-info .pytest_cache .ruff_cache .mypy_cache __pycache__ src/**/__pycache__ tests/**/__pycache__ tests/__pycache__ .coverage
