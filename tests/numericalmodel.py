#!/usr/bin/env python3
# system modules
import unittest

# import authentication module
from numericalmodel.numericalmodel import *
from numericalmodel.numericalschemes import *
from numericalmodel.interfaces import *

# import test data
from .test_data import *
from .test_flow import *

# skip everything
SKIPALL = False # by default, don't skip everything

class NumericalModelLinearDecayEquationRunTest(BasicTest):
    def setUp(self):
        # create a model
        model = NumericalModel()
        model.initial_time = 0

        # define values
        temperature = StateVariable( 
            id = "T", name = "temperature", unit = "K"  )
        parameter = Parameter( 
            id = "a", name = "linear parameter", unit = "1/s"  )
        forcing = ForcingValue( 
            id = "F", name = "forcing parameter", unit = "K/s" )

        # add the values to the model
        model.variables  = SetOfStateVariables( [ temperature  ]  )
        model.parameters = SetOfParameters(     [ parameter  ]    )
        model.forcing    = SetOfForcingValues(  [ forcing  ]      )

        # set initial values
        model.variables["T"].value  = 20 + 273.15
        model.parameters["a"].value = 0.1
        model.forcing["F"].value    = 28

        # create an equation object
        decay_equation = LinearDecayEquation(
            variable = temperature,
            input = SetOfInterfaceValues( [parameter, forcing] ),
            )

        # create a numerical scheme
        implicit_scheme = EulerImplicit(
            equation = decay_equation
            )

        # add the numerical scheme to the model
        model.numericalschemes = SetOfNumericalSchemes( [ implicit_scheme ] )

        self.model = model

    @testname("linear decay equation convergence test")
    @unittest.skipIf(SKIPALL,"skipping all tests")
    def test_convergence(self):
        model = self.model
        # integrate the model
        model.integrate( final_time = model.model_time + 100 )
        # numerical and analytical solution
        numerical_solution = model.variables["T"].value
        analytical_solution = \
            model.forcing["F"].value / model.parameters["a"].value
        # check if solution converges to analytical solution
        self.assertTrue(np.allclose( numerical_solution, analytical_solution ))



def run():
    # run the tests
    logger.info("=== NUMERICAL MODEL TESTS ===")
    unittest.main(exit=False,module=__name__)
    logger.info("=== END OF NUMERICAL MODEL TESTS ===")
