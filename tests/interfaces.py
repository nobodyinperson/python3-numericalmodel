#!/usr/bin/env python3
# system modules
import unittest
import logging
import time

# import authentication module
from numericalmodel.interfaces import *

# import test data
from .test_data import *
from .test_flow import *

# external modules
import numpy as np

# skip everything
SKIPALL = False # by default, don't skip everything

class InterfaceValueTest(BasicTest):
    """ Base class for InterfaceValue tests
    """
    
class InterfaceValueConstructionTest(InterfaceValueTest):
    """ Test for the construction and handling of the InterfaceValue class
    """
    @testname("empty constructor")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_empty_constructor(self):
        val = InterfaceValue() # empty constructor
        self.assertTrue( np.allclose( val.values, EMPTY_ARRAY ) )
        self.assertTrue( np.allclose( val.times, EMPTY_ARRAY ) )

class InterfaceValueInteractiveChangeTest(InterfaceValueTest):
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
        ta = 0
        tf = lambda: ta # a simple time_function
        val.time_function = tf # set time_function
        rg = range(5)
        for i in rg:
            ta = i
            self.logger.debug("tf() (should be {}): {}".format(i,tf()))
            v = lambda t: t + 1
            # time from time function
            val.next_time = None
            self.logger.debug("next_time after setting to None: {}".format(
                val.next_time))
            val.value = v(ta)
            self.logger.debug("val: {}".format(repr(val)))
            self.assertEqual( val.value, v(ta) )
            self.assertEqual( val.time, ta )
            self.assertTrue( 
                np.allclose( val.values, np.linspace(1,ta+1,2*ta+1) ) )
            self.assertTrue( 
                np.allclose( val.times, np.linspace(0,ta,2*ta+1) ) )
            # time from next_time
            val.next_time = ta + 0.5
            self.logger.debug("ta:{}".format(ta))
            self.logger.debug("v(ta+0.5):{}".format(v(ta+0.5)))
            val.value = v(ta + 0.5)
            self.logger.debug("values:{}".format(val.values))
            self.assertEqual( val.value , v(ta + 0.5) )
            self.assertEqual( val.time , ta + 0.5 )

    @testname("remembrance=0 test")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_remembrance_zero(self):
        val = self.val
        val.remembrance = 0
        for i in range(10):
            val.value = i
        self.assertEqual( val.values, np.array([9]) )

    @testname("remembrance test")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_remembrance(self):
        NOW = time.time()
        def time_func(): return time.time() - NOW
        ts = 0.1
        val = self.val
        val.time_function = time_func
        val.remembrance = ts
        for i in range(2):
            val.value = i
            # print(repr(val))
            time.sleep( ts * 0.2 ) # wait short time
            val.value = i + 1
            # print(repr(val))
            time.sleep( ts * 0.2 ) # wait short time
            val.value = i + 2
            # print(repr(val))
            self.assertTrue( np.allclose(val.values, np.array([i,i+1,i+2]) ))
            time.sleep( ts * 0.7  ) # wait that long that the first value is old
            val.value = i + 3
            # print(repr(val))
            self.assertTrue( np.allclose(val.values, np.array([i+1,i+2,i+3]) ))
            time.sleep( ts * 1.5 ) # wait very long


        

class InterfaceValueInterpolationTest(InterfaceValueTest):
    """ Tests for the InterfaceValue class' interpolation
    """
    def setUp(self):
        self.rg = np.linspace(0,9,10)
        self.val = InterfaceValue( 
            values = self.rg, times  = self.rg,
            )
        
    @testname("zero interpolation")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_zero_interpolation(self):
        val = self.val
        val.interpolation = "zero" # left-neighbour interpolation
        # test inside range interpolation
        for n in range(self.rg.size-1):
            t = self.rg[:n+1]
            tw = t 
            self.logger.debug("val({})={} should be {}".format(tw,val(tw),t))
            self.assertTrue(np.allclose(val(tw),t))
            tw = t+0.5
            self.logger.debug("val({}) should be {}".format(val(tw),t+1))
            self.assertTrue(np.allclose(val(tw),t))
        # test last value
        self.assertEqual( val( val.time ), val() )
        # test outside range interpolation
        self.assertEqual(val(self.rg.min()-1),self.rg.min())
        self.assertEqual(val(self.rg.max()+1),self.rg.max())

    @testname("nearest interpolation")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_nearest_interpolation(self):
        val = self.val
        val.interpolation = "nearest" # nearest-neighbour interpolation
        # test inside range interpolation
        for n in range(self.rg.size-1):
            t = self.rg[:n+1]
            tw = t 
            self.logger.debug("val({})={} should be {}".format(tw,val(tw),t))
            self.assertTrue(np.allclose(val(tw),t))
            tw = t + 0.499999999
            self.logger.debug("val({})={} should be {}".format(tw,val(tw),t))
            self.assertTrue(np.allclose(val(tw),t))
            tw = t + 0.500001
            self.logger.debug("val({})={} should be {}".format(tw,val(tw),t+1))
            self.assertTrue(np.allclose(val(tw),t+1))
        # test last value
        self.assertEqual( val( val.time ), val() )
        # test outside range interpolation
        self.assertEqual(val(self.rg.min()-1),self.rg.min())
        self.assertEqual(val(self.rg.max()+1),self.rg.max())

    @testname("linear interpolation")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_linear_interpolation(self):
        val = self.val
        val.interpolation = "linear" # linear interpolation
        # test inside range interpolation
        for n in range(self.rg.size-1):
            t = self.rg[:n+1]
            tw = t 
            self.logger.debug("val({})={} should be {}".format(tw,val(tw),t))
            self.assertTrue(np.allclose(val(tw),t))
            tw = t+0.5
            self.logger.debug("val({}) should be {}".format(val(tw),tw))
            self.assertTrue(np.allclose(val(tw),tw))
        # test last value
        self.assertEqual( val( val.time ), val() )
        # test outside range interpolation
        self.assertEqual(val(self.rg.min()-1),self.rg.min())
        self.assertEqual(val(self.rg.max()+1),self.rg.max())

def run():
    # run the tests
    logger.info("=== INTERFACES TESTS ===")
    unittest.main(exit=False,module=__name__)
    logger.info("=== END OF INTERFACES TESTS ===")
