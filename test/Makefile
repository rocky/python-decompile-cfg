check=PHONY clean dist distclean test test-unit test-functional rmChangeLog clean_pyc nosetests \
      check-bytecode-3 check-bytecode-3-short \
      grammar-coverage-3.8

GIT2CL ?= git2cl
PYTHON ?= python

PYTHON_VERSION = $(shell $(PYTHON) -V 2>&1 | cut -d ' ' -f 2 | cut -d'.' -f1,2 | head -1)
NATIVE_CHECK = check-$(PYTHON_VERSION)

# Set COMPILE='--compile' to force compilation before check
COMPILE ?=
COVER_DIR=../tmp/grammar-cover

# Run short tests
check-short:
	@$(PYTHON) -V && PYTHON_VERSION=`$(PYTHON) -V 2>&1 | cut -d ' ' -f 2 | cut -d'.' -f1,2 | head -1`; \
	$(MAKE) check-bytecode-$${PYTHON_VERSION}

# Run all tests
check:
	$(PYTHON) -V && PYTHON_VERSION=`$(PYTHON) -V 2>&1 | cut -d ' ' -f 2 | cut -d'.' -f1,2 | head -1`; \
	$(MAKE) check-$(PYTHON_VERSION)

#: Run working tests from Python 3.8
check-3.9 check-3.8: check-bytecode

#	$(PYTHON) test_pythonlib.py --bytecode-3.8-run --verify-run
#	$(PYTHON) test_pythonlib.py --bytecode-3.8 --syntax-verify $(COMPILE)

#: Check deparsing bytecode 3.x only
check-bytecode-3:
	$(PYTHON) test_pythonlib.py \
	--bytecode-3.8

check-bytecode-3-lambda:
	$(PYTHON) test_pythonlib.py \
	--bytecode-3.8 --lambda

check-bytecode-3-list-comprehension:
	$(PYTHON) test_pythonlib.py \
	--bytecode-3.8 --list-comprehension

#: Check deparsing bytecode on all Python 2 and Python 3 versions
check-bytecode: check-bytecode-3-lambda check-bytecode-3-list-comprehension check-bytecode-3

#: Get grammar coverage for Python 3.7
grammar-coverage-3.8:
	rm $(COVER_DIR)/spark-grammar-3.7.cover || /bin/true
	SPARK_PARSER_COVERAGE=$(COVER_DIR)/spark-grammar-3.8.cover $(PYTHON) test_pythonlib.py --bytecode-3.8-run --verify-run
	SPARK_PARSER_COVERAGE=$(COVER_DIR)/spark-grammar-3.8.cover $(PYTHON) test_pythonlib.py --bytecode-3.8 --syntax-verify $(COMPILE)
	SPARK_PARSER_COVERAGE=$(COVER_DIR)/spark-grammar-3.8.cover $(PYTHON) test_pyenvlib.py --3.8.0 --max=1000

clean: clean-py-dis clean-dis clean-unverified

clean-dis:
	find . -name '*_dis' -exec rm -v '{}' ';'

clean-unverified:
	find . -name '*_unverified' -exec rm -v '{}' ';'

#: Clean temporary compile/decompile/verify directories in /tmp
clean-py-dis:
	rm -fr /tmp/py-dis-* || true
