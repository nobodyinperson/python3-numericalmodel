#!/usr/bin/env python3
# system modules

# internal modules
from . import interfaces
from . import utils

# external modules
import numpy as np


class Equation(utils.LoggerObject,utils.ReprObject):
    """ Base class for equations
    """
    pass


class DerivativeEquation(Equation):
    """ Class to represent a derivative equation
    """
    pass


class PrognosticEquation(DerivativeEquation):
    """ Class to represend prognostic equations
    """
    pass


class DiagnosticEquation(Equation):
    """ Class to represent diagnostic equations
    """
    pass

