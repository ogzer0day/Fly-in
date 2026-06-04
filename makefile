PYTHON = python3

MAIN = main.py

PIP = pip


install:
	pip install -r requirements.txt

run:
	$(PYTHON) $(MAIN) $(ARGS)

debug:
	$(PYTHON) -m pdb $(MAIN)

clean:
	rm -rf __pycache__ .mypy_cache

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict


.PHONY: install run debug clean lint lint-strict