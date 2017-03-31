#!/usr/bin/env python3
# system modules
import unittest
import logging

# import authentication module
from numericalmodel.equations import *
from numericalmodel.numericalschemes import *
from numericalmodel.interfaces import *

# import test data
from .equations import LinearDecayEquationTest
from .test_data import *
from .test_flow import *

# external modules
import numpy as np

# skip everything
SKIPALL = False # by default, don't skip everything

class NumericalSchemeWithConstantLinearDecayEquationTest(
    LinearDecayEquationTest):
    """ Class for numerical scheme tests with constant linear decay equation
    """
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

    @testname("leap-frog scheme")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_leapfrog(self):
        inp = self.equation.input
        v = self.equation.variable
        scheme = LeapFrog( equation = self.equation, )
        for ts in self.timesteps:
            lin = self.equation.linear_factor()
            ind = self.equation.independent_addend()
            expected = 2 * ts * ( - inp("a") * v()  + inp("F") )
            self.logger.debug("expected: {}".format(expected))
            res = scheme.step( timestep = ts, tendency = True )
            self.logger.debug("result: {}".format(res))
            self.assertTrue( np.allclose( res, expected ) )

    @testname("Runge-Kutta-4 scheme")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_rungekutta4(self):
        inp = self.equation.input
        v = self.equation.variable
        scheme = RungeKutta4( equation = self.equation, )
        for ts in self.timesteps:
            lin = self.equation.linear_factor()
            ind = self.equation.independent_addend()
            t = v.time
            cur = v()

            def F(): return lin * cur + ind + nli

            nli = self.equation.nonlinear_addend()
            k1 = ts * F()
            nli = self.equation.nonlinear_addend(variablevalue = cur + k1 / 2)
            k2 = ts * F()
            nli = self.equation.nonlinear_addend(variablevalue = cur + k2 / 2)
            k3 = ts * F()
            nli = self.equation.nonlinear_addend(variablevalue = cur + k3)
            k4 = ts * F()
            tend = ( k1 + 2 * k2 + 2 * k3 + k4 ) / 6

            expected = tend
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
