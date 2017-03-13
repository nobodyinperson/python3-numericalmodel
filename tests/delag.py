#!/usr/bin/env python3
# system modules
import unittest
import logging

# import authentication module
import numericalmodel

# import test data
from .test_data import *
from .test_flow import *

# external modules

# skip everything
SKIPALL = False # by default, don't skip everything


def run():
    # run the tests
    logger.info("=== TESTS ===")
    unittest.main(exit=False,module=__name__)
    logger.info("=== END OF TESTS ===")
