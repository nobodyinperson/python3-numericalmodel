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
from numpy import * 

# skip everything
SKIPALL = False # by default, don't skip everything

class ReprObjectTest(BasicTest):
    """ Tests for the __repr__ method of all ReprObject subclasses
    """
    def setUp(self):
        self.reprobject_subclasses = all_subclasses(
            numericalmodel.utils.ReprObject)
        self.logger.debug("subclasses of ReprObject found:\n{}".format(
            self.reprobject_subclasses))

    @testname("__repr__ of any ReprObject subclass object with empty " 
        "constructor is exact representation")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_repr_empty_constructor(self):
        for cls in self.reprobject_subclasses:
            self.logger.debug("testing __repr__ representativity of " 
                "class {}".format(cls))
            obj = cls() # object created with empty constructor
            self.logger.debug("object of class {} with empty constructor:" 
                "\n{}".format(cls,obj))
            self.assertEqual(
                repr(eval(repr(obj))), # evaluated __repr__
                # should equal
                repr(obj) # __repr__ itself
                )

def run():
    # run the tests
    logger.info("=== TESTS ===")
    unittest.main(exit=False,module=__name__)
    logger.info("=== END OF TESTS ===")
