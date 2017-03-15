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
import numpy as np
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
                "\n{}".format(cls,repr(obj)))
            self.assertEqual(
                repr(eval(repr(obj))), # evaluated __repr__
                # should equal
                repr(obj) # __repr__ itself
                )

class InterfaceValueTest(BasicTest):
    """ Tests for the InterfaceValue class
    """
    def setUp(self):
        self.rg = np.linspace(0,9,10)
        self.interfacevalue = numericalmodel.interfaces.InterfaceValue( 
            values = self.rg, times  = self.rg,
            )
        self.logger.debug("InterfaceValue instance: {}".format(
            repr(self.interfacevalue)))
        
    @testname("__call__ with single value")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_call_single_value(self):
        for t in self.rg:
            self.logger.debug("InterfaceValue.__call__({}) should be {}".format(
                repr(t+0.5),t))
            self.assertEqual(self.interfacevalue(t+0.5),t)

    @testname("__call__ with array as argument")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_call_array_argument(self):
        for n in range(self.rg.size):
            t = self.rg[:n+1]
            self.logger.debug("InterfaceValue.__call__({}) should be {}".format(
                repr(t+0.5),t))
            self.assertTrue(np.allclose(self.interfacevalue(t+0.5),t))
        

def run():
    # run the tests
    logger.info("=== TESTS ===")
    unittest.main(exit=False,module=__name__)
    logger.info("=== END OF TESTS ===")
