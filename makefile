PYTHON: python3

MAIN: parsing.py

PIP: pip


install: 
	pip install -r requirements.txt

run:
	$(PYTHON) $(MAIN)

debug:
	$(PYTHON) -m pdb $(MAIN)

clean:
	rm -f  __pycache__ .mypy_cache

lint:
	flake8 .
	mypy . \
	--warn-return-any
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict


.PHONY: install run debug clean lint lint-strict