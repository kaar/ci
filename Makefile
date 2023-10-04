PROJECT_NAME := ci
VENV := .venv
SRC := $(LIBRARY_NAME)
BIN := $(VENV)/bin

.venv/bin/activate:
	@echo "Virtual environment does not exist. Creating one..."
	python -m venv .venv

venv: $(VENV)/bin/activate
	@$(VENV)/bin/pip install --upgrade -q \
		pip \
		build \
		ruff \
		black \
		isort \
		mypy \
	$(BIN)/pip install .

lint: venv
	$(BIN)/ruff $(SRC)
	$(BIN)/black --check $(SRC)
	$(BIN)/isort --check $(SRC)
.PHONY: lint

test: venv
.PHONY: test

build: clean
	python -m pip install --upgrade build
	python -m build
.PHONY: build

upload: build
	python -m pip install --upgrade twine
	python -m twine upload dist/* --verbose
.PHONY: upload

pipx-uninstall:
	pipx uninstall $(PROJECT_NAME)
.PHONY: pipx-uninstall

pipx-install:
	pipx install --editable .
.PHONY: pipx-install

release: clean lint test build
	git tag | grep -q "^v$(VERSION)$$" || (echo "Tag v$(VERSION) does not exist"; exit 1)
	gh release create v$(VERSION) dist/* --generate-notes
.PHONY: release

clean:
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .venv
.PHONY: clean
