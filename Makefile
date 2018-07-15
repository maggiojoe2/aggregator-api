.PHONY: all

all: requirements

.PHONY: requirements
requirements:
	@echo "Updating requirements.txt"
	pip3 install -r requirements.txt
	pip3 freeze > requirements.txt