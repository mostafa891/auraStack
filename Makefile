.PHONY: help dev test verify lint migrate install

help:
	@echo "auraStack Development Commands:"
	@echo "  make dev      - Start Django backend & Vite dev servers"
	@echo "  make test     - Run backend pytest test suite"
	@echo "  make verify   - Run full system verification (tests + migrations)"
	@echo "  make lint     - Run Ruff python linter"
	@echo "  make migrate  - Apply database migrations"
	@echo "  make install  - Install Python & Node.js dependencies"

dev:
	python manage.py runserver & npm run dev

test:
	pytest -v

verify:
	python verify_all.py

lint:
	ruff check .

migrate:
	python manage.py makemigrations
	python manage.py migrate

install:
	pip install -r requirements.txt
	npm install
