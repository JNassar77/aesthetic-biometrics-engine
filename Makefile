.PHONY: dev docker test lint clean

# Local development
dev:
	uvicorn app.main:app --reload --port 8000

# Docker
docker:
	docker compose up --build

docker-down:
	docker compose down

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=app --cov-report=term-missing

# Utilities
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find . -name "*.pyc" -delete 2>/dev/null; true

freeze:
	pip freeze > requirements.txt
