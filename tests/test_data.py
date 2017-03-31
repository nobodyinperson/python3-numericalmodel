#!/usr/bin/env python3
# internal modules
import numericalmodel

# external modules
import numpy as np

EMPTY_ARRAY = np.array([])

class LinearDecayEquation(numericalmodel.equations.PrognosticEquation):
    """
    Class for the linear decay equation
    """
    def linear_factor(self, time = None ):
        # take the "a" parameter from the input, interpolate it to the given
        # "time" and return the negative value
        return - self.input["a"](time)

    def independent_addend(self, time = None ):
        # take the "F" forcing parameter from the input, interpolate it to
        # the given "time" and return it
        return self.input["F"](time)

    def nonlinear_addend(self, *args, **kwargs):
        return 0 # nonlinear addend is always zero (LINEAR decay equation)

