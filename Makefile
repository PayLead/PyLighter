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

source:
	python setup.py sdist

build:
	python setup.py bdist_wheel

.PHONY: source build

test:
	pytest

test-quality: flake8 check-manifest isort 

test-all:
	tox -e py

test-all-envs:
	tox

.PHONY: test test-quality test-all test-all-envs

flake8:
	flake8 $(PACKAGE)
	flake8 $(TEST_DIR)

check-manifest:
	check-manifest

isort:
	isort --check --diff $(PACKAGE)
	isort --check --diff $(TEST_DIR)

.PHONY: flake8 check-manifest isort
