run:
	python -m picpick

lint:
	black --check .
	flake8
	mypy .

test:
	pytest

.PHONY: run lint test

