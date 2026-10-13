.PHONY: check format

format:
	ruff format .
	ruff check --fix .

check:
	ruff check .
	ruff format --check .
	mypy src
	pytest