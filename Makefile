run:
	python -m picpick

lint:
	black --check .
	flake8
	mypy .

test:
	pytest

build:
	echo 'import picpick.__main__' > executable.py
	pyinstaller -y executable.py --name picpick

clean:
	rm -rf build dist executable.spec picpick.py


.PHONY: build clean run lint test

