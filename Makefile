.PHONY: install install-dev test format lint clean uninstall

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

format:
	black src tests

lint:
	black --check src tests

test: install-dev format lint
	pytest

uninstall:
	pip uninstall -y yt-crawl

clean: uninstall
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache .mypy_cache __pycache__ src/**/__pycache__ tests/**/__pycache__
