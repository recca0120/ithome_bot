.PHONY: help install install-dev test test-unit test-integration test-e2e coverage lint format clean

help:
	@echo "Available commands:"
	@echo "  make install        - Install production dependencies"
	@echo "  make install-dev    - Install development dependencies"
	@echo "  make test          - Run all tests"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-e2e      - Run end-to-end tests only"
	@echo "  make coverage      - Run tests with coverage report"
	@echo "  make lint          - Run code linting"
	@echo "  make format        - Format code with black and isort"
	@echo "  make clean         - Remove cache and temporary files"

install:
	pip install -r requirements.txt

install-dev: install
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest

test-unit:
	pytest -m unit tests/unit/

test-integration:
	pytest -m integration tests/integration/

test-e2e:
	pytest -m e2e tests/e2e/

coverage:
	pytest --cov=src --cov-report=html --cov-report=term

lint:
	flake8 src tests
	mypy src
	black --check src tests
	isort --check-only src tests

format:
	black src tests
	isort src tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name htmlcov -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete