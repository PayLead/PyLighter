PACKAGE=pylighter
TEST_DIR=test

default:

clean:
	find . -type f -name '*.pyc' -delete
	find . -type f -path '*/__pycache__/*' -delete
	find . -type d -empty -delete

install:
	pip install -e

install-dev:
	pip install -e ".[dev]"

upgrade:
	pip install --upgrade pip setuptools

release:
	fullrelease

.PHONY: default clean install install-dev upgrade release 

testall:
	tox

test:
	pytest

.PHONY: test testall

lint: flake8 check-manifest

flake8:
	flake8 $(PACKAGE)
	flake8 $(TEST_DIR)

check-manifest:
	check-manifest

.PHONY: lint flake8 isort check-manifest
