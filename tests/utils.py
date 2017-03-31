#!/usr/bin/env python3
# system modules
import unittest
import logging

# import authentication module
import numericalmodel
from numericalmodel import utils
from numericalmodel.utils import *

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
        self.reprobject_subclasses = all_subclasses(utils.ReprObject)
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
            try:
                self.assertEqual(
                    repr(eval(repr(obj))), # evaluated __repr__
                    # should equal
                    repr(obj) # __repr__ itself
                    )
            except NameError: # never mind a NameError
                pass

class SetOfObjectsTest(BasicTest):
    """ Base class for tests of the SetOfObjects class
    """
    pass

class object_with_property(object):
    def __init__(self): 
        self.val = ""

class SetOfObjectsConstructorTest(SetOfObjectsTest):
    """ Constructor tests for the SetOfObjects class
    """
    def setUp(self):
        self.primitive_types = [str,int,float]
        self.rg = range(5)

    @testname("primitive types - repr() as key function")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_primitive_types_equality(self):
        for ptype in self.primitive_types:
            # create a set
            elements = [ptype(i) for i in self.rg] # create elements
            setoo = utils.SetOfObjects( # create SetOfObjects
                elements = elements, element_type = ptype)
            # check if elements are EXACTLY the same (reference)
            for element in elements:
                key = setoo._object_to_key(element)
                self.assertEqual( setoo[key], element )
            
    @testname("object as type - reference stays")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_object_reference(self):
        cls = object_with_property
        elements = [cls() for i in self.rg] # create elements
        setoo = utils.SetOfObjects( # create SetOfObjects
            elements = elements, element_type = cls)
        # check if real references are used
        for element in elements:
            key = setoo._object_to_key(element)
            self.assertEqual( setoo[key], element ) # reference is valid
            element.val = "hey" # change property directly
            self.assertEqual( setoo[key].val, element.val ) # property changed
            setoo[key].val = "jo" # change property via SetOfObjects
            self.assertEqual( setoo[key].val, element.val ) # property changed
    

class SetOfObjectsInteractiveTest(SetOfObjectsTest):
    def setUp(self):
        self.set = SetOfObjects() # empty set

    @testname("add_element")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_add_element(self):
        obj = object()
        self.set.add_element( obj )
        self.assertTrue( obj in self.set.elements )

    @testname("setitem")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_setitem(self):
        obj = object()
        self.set["object"] = obj
        self.assertEqual( self.set["object"], obj )
        self.assertTrue( obj in self.set.elements )

    @testname("delitem")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_delitem(self):
        obj = object()
        self.set["object"] = obj
        self.assertTrue( "object" in self.set )
        del self.set["object"]
        self.assertFalse( "object" in self.set )
        
        

def run():
    # run the tests
    logger.info("=== UTILS TESTS ===")
    unittest.main(exit=False,module=__name__)
    logger.info("=== END OF UTILS TESTS ===")
