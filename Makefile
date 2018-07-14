.PHONY: all

all: requirements

.PHONY: requirements
requirements:
	@echo "Updating requirements.txt"
	pip install -r requirements.txt
	pip freeze > requirements.txt