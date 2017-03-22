#!/usr/bin/env python3
# system modules
import unittest
import logging

# import authentication module
from numericalmodel.interfaces import *

# import test data
from .test_data import *
from .test_flow import *

# external modules
import numpy as np

# skip everything
SKIPALL = False # by default, don't skip everything

class InterfaceValueConstructionTest(BasicTest):
    """ Test for the construction and handling of the InterfaceValue class
    """
    @testname("empty constructor")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_empty_constructor(self):
        val = InterfaceValue() # empty constructor
        self.assertTrue( np.allclose( val.values, EMPTY_ARRAY ) )
        self.assertTrue( np.allclose( val.times, EMPTY_ARRAY ) )

class InterfaceValueInteractiveChangeTest(BasicTest):
    """ Test for interactive InterfaceValue manipulation
    """
    def setUp(self):
        self.val = InterfaceValue() # empty InterfaceValue

    @testname("increasing next_time property behaviour")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_increasing_next_time(self):
        val = self.val
        rg = range(10)
        v = lambda i: i + 1
        for i in rg:
            val.next_time = i
            self.assertEqual(val.next_time, i)
            val.value = v(i)
            self.assertEqual( val.value, v(i) )
            self.assertEqual( val.time,  i )
            self.assertTrue( np.allclose( val.values, v(np.array(rg)[:(i+1)] )))
            self.assertTrue( np.allclose( val.times, np.array(rg)[:(i+1)] ) )

    @testname("equal next_time property behaviour")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_equal_next_time(self):
        val = self.val
        t = 1
        v = lambda i: i + 1
        for _ in range(10):
            val.next_time = t
            self.assertEqual(val.next_time, t)
            val.value = v(t)
            self.assertEqual( val.value, v(t) )
            self.assertEqual( val.time,  t )
            self.assertTrue( np.allclose( val.values, v(np.array(t)) ) )
            self.assertTrue( np.allclose( val.times, np.array(t) ) )


    @testname("increasing and equal next_time property behaviour")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_increasing_and_equal_next_time(self):
        val = self.val
        rg = range(5)
        for t in rg:
            for k in rg:
                self.logger.debug("t={t}, k={k}".format(t=t,k=k))
                v = lambda t: t + k
                val.next_time = t
                self.assertEqual(val.next_time, t)
                val.value = v(t)
                self.assertEqual( val.value, v(t) )
                self.assertEqual( val.time,  t )
                self.logger.debug("val:\n{}".format(repr(val)))
                expected_val = np.append(
                    np.linspace(max(rg),max(rg)+t-1,t), v(t))
                self.logger.debug("expected_val: {}".format(expected_val))
                self.assertTrue( np.allclose( val.values, expected_val ))
                self.assertTrue( 
                    np.allclose( val.times, np.array(rg)[:(t+1)] ) )

    @testname("decreasing time should fail")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    @unittest.expectedFailure
    def test_decreasing_next_time_fail(self):
        val = self.val
        val.value = 1
        val.next_time = val.time - 1 # should fail

    @testname("time_function behaviour")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_time_function(self):
        val = self.val
        t = 0
        tf = lambda: t # a simple time_function
        val.time_function = tf # set time_function
        rg = range(5)
        for i in rg:
            t = i
            v = lambda i: i + 1
            val.value = v(i)
            self.assertEqual( val.value, v(i) )
            self.assertEqual( val.time, i )
            self.assertTrue( np.allclose( val.values, v(np.array(rg)[:(i+1)] )))
            self.assertTrue( np.allclose( val.times, np.array(rg)[:(i+1)] ) )

    @testname("time_function and next_time behaviour")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_time_function_and_next_time(self):
        val = self.val
        t = 0
        tf = lambda: t # a simple time_function
        val.time_function = tf # set time_function
        rg = range(5)
        for i in rg:
            t = i
            v = lambda i: i + 1
            val.value = v(i)
            self.assertEqual( val.value, v(i) )
            self.assertEqual( val.time, i )
            self.assertTrue( np.allclose( val.values, v(np.array(rg)[:(i+1)] )))
            self.assertTrue( np.allclose( val.times, np.array(rg)[:(i+1)] ) )
        

class InterfaceValueInterpolationTest(BasicTest):
    """ Tests for the InterfaceValue class' interpolation
    """
    def setUp(self):
        self.rg = np.linspace(0,9,10)
        self.interfacevalue = InterfaceValue( 
            values = self.rg, times  = self.rg,
            )
        
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
    logger.info("=== INTERFACES TESTS ===")
    unittest.main(exit=False,module=__name__)
    logger.info("=== END OF INTERFACES TESTS ===")
