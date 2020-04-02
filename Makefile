run:
	python -m picpick

lint:
	black --check .
	flake8

test:
	pytest

.PHONY: run lint test

