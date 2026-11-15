.PHONY: generate load test

generate:
	.venv/bin/python scripts/generate_data.py

load:
	.venv/bin/python -m scripts.load_data

test:
	.venv/bin/pytest -q
