#!/usr/bin/env make -f

SETUP.PY = ./setup.py
INIT.PY = $(shell find numericalmodel -maxdepth 1 -type f -name '__init__.py')

VERSION = $(shell perl -ne 'if (s/^.*__version__\s*=\s*"(\d+\.\d+.\d+)".*$$/$$1/g){print;exit}' $(INIT.PY))

.PHONY: all
all: wheel

.PHONY: build
build: 
	$(SETUP.PY) build

.PHONY: wheel
wheel:
	$(SETUP.PY) sdist bdist_wheel

.PHONY: upload
upload: wheel tag
	$(SETUP.PY) sdist upload -r pypi

.PHONY: upload-test
upload-test: wheel tag
	$(SETUP.PY) sdist upload -r pypitest

.PHONY: increase-patch
increase-patch: $(INIT.PY)
	perl -pi -e 's/(__version__\s*=\s*")(\d+)\.(\d+).(\d+)(")/$$1.(join ".",$$2,$$3,$$4+1).$$5/ge' $(INIT.PY)

.PHONY: increase-minor
increase-minor: $(INIT.PY)
	perl -pi -e 's/(__version__\s*=\s*")(\d+)\.(\d+).(\d+)(")/$$1.(join ".",$$2,$$3+1,0).$$5/ge' $(INIT.PY)

.PHONY: increase-major
increase-major: $(INIT.PY)
	perl -pi -e 's/(__version__\s*=\s*")(\d+)\.(\d+).(\d+)(")/$$1.(join ".",$$2+1,0,0).$$5/ge' $(INIT.PY)

.PHONY: tag
tag:
	git tag -f v$(VERSION)

.PHONY: setup-test
setup-test:
	$(SETUP.PY) test
	
.PHONY: test
test:
	python3 -c 'import tests;tests.runall(verbose=False)'

.PHONY: testverbose
testverbose:
	python3 -c 'import tests;tests.runall(verbose=True)'

.PHONY: clean
clean:

.PHONY: distclean
distclean: clean
	rm -rf *.egg-info
	rm -rf build
	rm -rf $$(find -type d -iname '__pycache__')
	rm -f $$(find -type f -iname '*.pyc')

