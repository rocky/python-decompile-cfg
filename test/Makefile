check=PHONY \
      2.3 \
      clean \
      dist distclean \
      check-bytecode-3 \
      check-bytecode-3-short \
      code-fragments \
      grammar-coverage-3.8 \
      nosetests \
      rmChangeLog clean_pyc \
      test test-unit test-functional

GIT2CL ?= git2cl
PYTHON ?= python

PYTHON_VERSION = $(shell $(PYTHON) -V 2>&1 | cut -d ' ' -f 2 | cut -d'.' -f1,2 | head -1)
NATIVE_CHECK = check-$(PYTHON_VERSION)

# Set COMPILE='--compile' to force compilation before check
COMPILE ?=
COVER_DIR=../tmp/grammar-cover

#: Phony target to handle pyston-2.3.x
2.3:

#: Run short tests
check-short:
	@$(PYTHON) -V && PYTHON_VERSION=`$(PYTHON) -V 2>&1 | cut -d ' ' -f 2 | cut -d'.' -f1,2 | head -1`; \
	$(MAKE) check-bytecode-$${PYTHON_VERSION}

#: Run all tests
check:
	$(PYTHON) -V && PYTHON_VERSION=`$(PYTHON) -V 2>&1 | cut -d ' ' -f 2 | cut -d'.' -f1,2 | head -1`; \
	$(MAKE) check-$(PYTHON_VERSION)

#: Run working tests from Python 3.8
check-3.8 check-3.9 check-3.10: check-bytecode

#	$(PYTHON) test_pythonlib.py --bytecode-3.8 --run --verify-run
#	$(PYTHON) test_pythonlib.py --bytecode-3.8 --syntax-verify $(COMPILE)

#: Check deparsing bytecode 3.x only
check-bytecode-3: \
   check-bytecode-3.8 \
   check-bytecode-3.9 \
   check-bytecode-3.10
# check-bytecode-3:
# 	$(PYTHON) test_pythonlib.py \
# 	--bytecode-3.8

#: Check deparsing 3.8 bytecode
check-bytecode-3.8: \
    check-bytecode-3.8-lambda \
    check-bytecode-3.8-generator \
    check-bytecode-3.8-set-comprehension \
    check-bytecode-3.8-dict-comprehension

#: Check deparsing 3.9 bytecode
check-bytecode-3.9: \
    check-bytecode-3.9-lambda \
    check-bytecode-3.9-generator \
    check-bytecode-3.9-set-comprehension \
    check-bytecode-3.9-dict-comprehension

#: Check deparsing 3.10 bytecode
check-bytecode-3.10: \
    check-bytecode-3.10-lambda \
    check-bytecode-3.10-generator \
    check-bytecode-3.10-set-comprehension \
    check-bytecode-3.10-dict-comprehension

# check-bytecode-3.10:
# 	$(PYTHON) test_pythonlib.py \
# 	--bytecode-3.10


check-bytecode-3.8-dict-comprehension:
	$(PYTHON) test_pythonlib.py --bytecode-3.8 --dict-comprehension

check-bytecode-3.9-dict-comprehension:
	$(PYTHON) test_pythonlib.py --bytecode-3.9 --dict-comprehension

check-bytecode-3.10-dict-comprehension:
	$(PYTHON) test_pythonlib.py --bytecode-3.10 --dict-comprehension

#: Check deparsing bytecode 3.9 only
check-bytecode-3.9-lambda:
# check-bytecode-3.9:
# 	$(PYTHON) test_pythonlib.py \
# 	--bytecode-3.9

check-bytecode-3-lambda:
	$(PYTHON) test_pythonlib.py \
	--bytecode-3.8 --lambda \
	--bytecode-3.9 --lambda \
	--bytecode-3.10 --lambda

check-bytecode-3.8-lambda:
	$(PYTHON) test_pythonlib.py --bytecode-3.8 --lambda

check-bytecode-3.9-lambda:
	$(PYTHON) test_pythonlib.py --bytecode-3.9 --lambda

check-bytecode-3.10-lambda:
	$(PYTHON) test_pythonlib.py \
	--bytecode-3.10 --lambda

check-bytecode-3-generator:
	$(PYTHON) test_pythonlib.py \
	--bytecode-3.8 --generator \
	--bytecode-3.9 --generator \
	--bytecode-3.10 --lambda

check-bytecode-3.8-generator:
	$(PYTHON) test_pythonlib.py --bytecode-3.8 --generator

check-bytecode-3.9-generator:
	$(PYTHON) test_pythonlib.py --bytecode-3.9 --generator

check-bytecode-3.10-generator:
	$(PYTHON) test_pythonlib.py --bytecode-3.10 --generator

check-bytecode-3.8-set-comprehension:
	$(PYTHON) test_pythonlib.py \
	--bytecode-3.8 --set-comprehension

check-bytecode-3.9-set-comprehension:
	$(PYTHON) test_pythonlib.py \
	--bytecode-3.9 --set-comprehension

check-bytecode-3.10-set-comprehension:
	$(PYTHON) test_pythonlib.py \
	--bytecode-3.10 --set-comprehension

check-bytecode-3-dict-comprehension:
	$(PYTHON) test_pythonlib.py \
	--bytecode-3.8 --dict-comprehension \
	--bytecode-3.9 --dict-comprehension \
	--bytecode-3.10 --dict-comprehension

check-bytecode-3-list-comprehension:
	$(PYTHON) test_pythonlib.py \
	--bytecode-3.8 --list-comprehension

check-bytecode-3-run:
	$(PYTHON) test_pythonlib.py \
	--bytecode-3.8 --run --verify-run

check-bytecode-3-set-comprehension:
	$(PYTHON) test_pythonlib.py \
	--bytecode-3.8 --set-comprehension

#: Check deparsing bytecode on all Python 3 versions
check-bytecode: check-bytecode-3

check-code-fragments: \
	check-bytecode-3-lambda \
	check-bytecode-3-dict-comprehension \
	check-bytecode-3-generator \
	check-bytecode-3-list-comprehension \
	check-bytecode-3-set-comprehension

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
