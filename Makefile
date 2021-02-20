PRJ = uns


.PHONY: coverage
coverage:
	pytest --cov=$(PRJ) tests


.PHONY: lint
lint:
	pylama


.PHONY: dist
dist:
	python setup.py sdist


.PHONY: requirements-dev
requirements-dev:
	pip install -r requirements-dev.txt


.PHONY: dev
dev: requirements-dev
	pip install -e .
