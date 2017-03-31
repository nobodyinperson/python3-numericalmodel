#!/usr/bin/env python3
# system modules
import unittest
import logging

# import authentication module
from numericalmodel.equations import *
from numericalmodel.numericalschemes import *
from numericalmodel.interfaces import *

# import test data
from .test_data import *
from .test_flow import *

# external modules
import numpy as np

# skip everything
SKIPALL = False # by default, don't skip everything

class NumericalSchemeWithConstantLinearDecayEquationTest(BasicTest):
    """ Class for numerical scheme tests with constant linear decay equation
    """
    def setUp(self):
        a = Parameter(id="a",name="linear factor",
            values = np.array([1]),
            times = np.array([0])
            )
        F = ForcingValue(id="F",name="independent addend",
            values = np.array([5]),
            times = np.array([0])
            )
        T = StateVariable(id="T",name="variable", 
            values = np.array([20]),
            times = np.array([0]),
            )
        equation = LinearDecayEquation( 
            variable = T,
            input = SetOfInterfaceValues( elements = [a,F] )
            )

        self.equation = equation
        self.timesteps = np.linspace(0,10,5)

    @testname("euler explicit scheme")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_euler_explicit(self):
        inp = self.equation.input
        v = self.equation.variable
        scheme = EulerExplicit( equation = self.equation, )
        for ts in self.timesteps:
            expected = ts * ( - inp("a") * v()  + inp("F") )
            res = scheme.step( timestep = ts, tendency = True )
            self.assertTrue( np.allclose( res, expected ) )

    @testname("euler implicit scheme")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_euler_implicit(self):
        inp = self.equation.input
        v = self.equation.variable
        scheme = EulerImplicit( equation = self.equation, )
        for ts in self.timesteps:
            lin = self.equation.linear_factor()
            ind = self.equation.independent_addend()
            expected = (ind*ts + v())/(1-lin*ts) - v()
            self.logger.debug("expected: {}".format(expected))
            res = scheme.step( timestep = ts, tendency = True )
            self.logger.debug("result: {}".format(res))
            self.assertTrue( np.allclose( res, expected ) )

        
        
class NumericalSchemeWithVariableLinearDecayEquationTest(BasicTest):
    """ Class for numerical scheme tests with time-dependent linear decay 
        equation
    """
    def setUp(self):
        n = 10
        times = np.linspace(0,n*10,n)
        a = Parameter(id="a",name="linear factor",
            values = 2 * np.sin(np.linspace(0,np.pi,n)),
            times = times
            )
        F = ForcingValue(id="F",name="independent addend",
            values = 5 * np.cos(np.linspace(0,np.pi,n)),
            times = times
            )
        T = StateVariable(id="T",name="variable", 
            values = np.array([20]),
            times = np.array([0]),
            )
        equation = LinearDecayEquation( 
            variable = T,
            input = SetOfInterfaceValues( elements = [a,F] )
            )

        self.times = times
        self.equation = equation

    # TODO



def run():
    # run the tests
    logger.info("=== NUMERICAL SCHEMES TESTS ===")
    unittest.main(exit=False,module=__name__)
    logger.info("=== END OF NUMERICAL SCHEMES TESTS ===")
