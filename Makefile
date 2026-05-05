## MD INDUSTRIES
## Developer: M.DHANESVARAN
## Portable Python Subset Compiler

PYTHON ?= python

all:
	$(PYTHON) -m pyportcc test/sample.py output/sample.c

test:
	$(PYTHON) scripts/test_portable.py

clean:
	rm -rf bin build __pycache__ output/*.c output/*.o output/*.obj output/*.exe output/*.out output/runtime_output.txt

.PHONY: all test clean
