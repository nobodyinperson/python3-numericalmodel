#!/usr/bin/env python3
# system modules
import unittest

# import authentication module
from numericalmodel.equations import *
from numericalmodel.interfaces import *

# import test data
from .test_data import *
from .test_flow import *

# skip everything
SKIPALL = False # by default, don't skip everything

class LinearDecayEquationTest(BasicTest):
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

    @testname("derivative test")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_derivative(self):
        eq = self.equation
        for T in range(10):
            eq.variable.value = T
            expected = - eq.input("a") * eq.variable() + eq.input("F")
            self.assertTrue( np.allclose(self.equation.derivative(),expected ) )


def run():
    # run the tests
    logger.info("=== EQUATIONS TESTS ===")
    unittest.main(exit=False,module=__name__)
    logger.info("=== END OF EQUATIONS TESTS ===")
