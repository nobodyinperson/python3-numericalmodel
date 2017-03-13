#!/usr/bin/env make -f

SETUP.PY = ./setup.py

.PHONY: all
all: build

.PHONY: build
build: 
	$(SETUP.PY) build

.PHONY: clean
clean:

.PHONY: distclean
distclean: clean
	rm -rf *.egg-info
	rm -rf build
	rm -rf $$(find -type d -iname '__pycache__')
	rm -f $$(find -type f -iname '*.pyc')

.PHONY: setup-test
setup-test:
	$(SETUP.PY) test
	
.PHONY: test
test:
	python3 -c 'import tests;tests.runall(verbose=False)'

.PHONY: testverbose
testverbose:
	python3 -c 'import tests;tests.runall(verbose=True)'
