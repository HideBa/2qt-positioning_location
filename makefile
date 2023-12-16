
PACKAGE_DIR = "."

.PHONY: install
install:
	poetry install

.PHONY: update
update:
	poetry update

.PHONY: lint
lint:
	poetry run flake8 $(PACKAGE_DIR)/**/*.py


.PHONY: format
format:
	poetry run black $(PACKAGE_DIR)/**/*.py

.PHONY: sort
sort:
	poetry run isort $(PACKAGE_DIR)/**/*.py

.PHONY: note
note:
	poetry run jupyter lab
