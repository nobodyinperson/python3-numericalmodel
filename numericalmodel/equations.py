#!/usr/bin/env python3
# system modules
import collections
import inspect
import copy

# internal modules
from . import interfaces
from . import utils

# external modules
import numpy as np


class Equation(utils.LoggerObject,utils.ReprObject):
    """ Base class for equations
    """
    def __init__(self, variable = None, 
        description = None, long_description = None,
        input = None,
        ):
        """ Class constructor
        Args:
            description (str): short equation description
            long_description (str): long equation description
            variable (InterfaceVariable): the variable obtained by solving the
                equation
            input (SetOfInterfaceValues): set of values needed by the equation
        """
        if variable is None: self.variable = self._default_variable
        else:                self.variable = variable
        if description is None: self.description = self._default_description
        else:                   self.description = description
        if input is None: self.input = self._default_input
        else:                   self.input = input
        if long_description is None: 
            self.long_description = self._default_long_description
        else:                   self.long_description = long_description

    @property
    def variable(self):
        try:                   self._variable
        except AttributeError: self._variable = self._default_variable
        return self._variable

    @variable.setter
    def variable(self, newvar):
        assert isinstance(newvar, interfaces.StateVariable), \
            "variable has to be instance of StateVariable"
        self._variable = newvar
        
    @property
    def _default_variable(self):
        return interfaces.StateVariable()

    @property
    def description(self):
        try:                   self._description
        except AttributeError: self._description = self._default_description
        return self._description

    @description.setter
    def description(self, newdescription):
        assert isinstance(newdescription, str), "description has to be str"
        self._description = newdescription
        
    @property
    def _default_description(self):
        return "an equation"

    @property
    def input(self):
        try:                   self._input
        except AttributeError: self._input = self._default_input
        return self._input

    @input.setter
    def input(self, newinput):
        assert isinstance(newinput, interfaces.SetOfInterfaceValues), \
            "input has to be SetOfInterfaceValues"
        self._input = newinput
        
    @property
    def _default_input(self):
        return interfaces.SetOfInterfaceValues()

    @property
    def long_description(self):
        try:                   self._long_description
        except AttributeError: 
            self._long_description = self._default_long_description
        return self._long_description

    @long_description.setter
    def long_description(self, newlong_description):
        assert isinstance(newlong_description, str), \
            "long_description has to be str"
        self._long_description = newlong_description
        
    @property
    def _default_long_description(self):
        return "This is an equation."

    ###############
    ### Methods ###
    ###############
    def depends_on(self, id):
        """ Check if this equation depends on a given InterfaceValue's id
        Args:
            id (str or InterfaceValue): InterfaceValue or id
        Returns:
            True if 'id' is in self.input, False if otherwise
        """
        try: ident = id.id
        except AttributeError: ident = id
        assert isinstance(ident,str), \
            "id is neither str nor has it an 'id' attribute"
        return ident in self.input.keys()

    def __str__(self):
        """ Stringification: summary
        """
        string = (
        " \"{description}\" \n"
        "----------- {variable} -----------\n"
        "{long_description}"
        ).format(description=self.description, variable=self.variable.id,
            long_description = self.long_description)
        return string
        



class DerivativeEquation(Equation):
    """ Class to represent a derivative equation
    """
    ###############
    ### Methods ###
    ###############
    def linear_factor(self, time = None):
        """ Calculate the derivative's linear factor in front of the variable
        Args:
            times [Optional(single numeric value)]: the time to calculate the 
                derivative. Defaults to the variable's current (last) time.
        """
        raise NotImplementedError("subclasses must override this method")

    def independent_addend(self, time = None):
        """ Calculate the derivative's addend part that is independent of the
        variable.
        Args:
            times [Optional(single numeric value)]: the time to calculate the 
                derivative. Defaults to the variable's current (last) time.
        """
        raise NotImplementedError("subclasses must override this method")

    def nonlinear_addend(self, time = None, variablevalue = None):
        """ Calculate the derivative's addend part that is nonlinearly dependent
        of the variable.
        Args:
            times [Optional(single numeric value)]: the time to calculate the 
                derivative. Defaults to the variable's current (last) time.
            variablevalue [Optional(np.array)]: the variable vaulue to use. 
                Defaults to the value of self.variable at the given time.
        """
        raise NotImplementedError("subclasses must override this method")

    def derivative(self, time = None, variablevalue = None):
        """ Calculate the derivative (right-hand-side) of the equation
        Args:
            times [Optional(single numeric value)]: the time to calculate the 
                derivative. Defaults to the variable's current (last) time.
            variablevalue [Optional(np.array)]: the variable vaulue to use. 
                Defaults to the value of self.variable at the given time.
        Returns:
            the derivatives corresponding to the given time as np.array
        """
        if variablevalue is None: var = self.variable(time)
        else:                     var = variablevalue

        # calculate the derivative parts
        linear_factor = self.linear_factor(time = time)
        independent_addend = self.independent_addend(time = time)
        nonlinear_addend = self.nonlinear_addend(
            time = time, variablevalue = var)
            
        # merge parts
        deriv = linear_factor * var + independent_addend + nonlinear_addend

        return deriv


class PrognosticEquation(DerivativeEquation):
    """ Class to represent prognostic equations
    """
    pass


class DiagnosticEquation(Equation):
    """ Class to represent diagnostic equations
    """
    pass




########################
### Set of Equations ###
########################
class SetOfEquations(utils.SetOfObjects):
    """ Base class for sets of Equations
    """
    def __init__(self, elements = []):
        """ class constructor
        Args:
            elements (list of Equations): the list of Equation instances
        """
        utils.SetOfObjects.__init__(self, # call SetOfObjects constructor
            elements = elements, 
            element_type = Equation, # only Equation is allowed
            )

    ###############
    ### Methods ###
    ###############
    def _object_to_key(self, obj):
        """ key transformation function. 
        Args:
            obj (object): the element
        Returns:
            key (str): the unique key for this object. The variable's id
                is used.
        """
        return obj.variable.id



