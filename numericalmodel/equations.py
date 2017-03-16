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
    pass


class PrognosticEquation(DerivativeEquation):
    """ Class to represend prognostic equations
    """
    def __init__(self, variable = None, 
        description = None, long_description = None,
        input = None, max_timestep = None,
        ):
        """ Class constructor
        Args:
            description (str): short equation description
            long_description (str): long equation description
            variable (InterfaceVariable): the variable obtained by solving the
                equation
            input (SetOfInterfaceValues): set of values needed by the equation
            max_timestep (numeric value): the maximum timestep in seconds
        """
        # super class constructor
        DerivativeEquation.__init__(self,
            variable = variable, description = description, long_description =
            long_description, input = input)
        
        if max_timestep is None: self.max_timestep = self._default_max_timestep
        else:                    self.max_timestep = max_timestep


    ##################
    ### Properties ###
    ##################
    @property
    def max_timestep(self):
        """ The maximum timesta
        """
        try:                   self._max_timestep # already defined?
        except AttributeError: self._max_timestep = self._default_times # default
        return self._max_timestep # return

    @max_timestep.setter
    def max_timestep(self,newmax_timestep):
        assert utils.is_numeric(newmax_timestep), \
            "max_timestep has to be numeric"
        assert np.asarray(newmax_timestep).size == 1, \
            "max_timestep has to be one single value" 
        self._max_timestep = newmax_timestep

    @property
    def _default_max_timestep(self):
        return 1 # empty array
        

    ###############
    ### Methods ###
    ###############
    def derivative(self, times = None, variable = None):
        """ Calculate the derivative (right-hand-side) of the equation
        Args:
            times [Optional(numeric)]: the times to calculate the derivative.
                Defaults to the current (last) time.
            variable [Optional(StateVariable)]: the variable to use. Defaults to
                self.variable.
        Returns:
            the derivatives corresponding to the given times as np.array
        """
        raise NotImplementedError("subclasses should override this method")

    def runge_kutta(self, timestep = None):
        """ Integrate one step Runge-Kutta and return the value.
        Args:
            timestep (single numeric value): The timestep. Defaults to
                max_timestep
        Returns:
            the value of self.variable after this Runge-Kutta timestep
        """
        if timestep is None: timestep = self.max_timestep # default
        assert utils.is_numeric(timestep), "timestep has to be numeric"
        assert np.asarray(timestep).size == 1, "timestep has to be one value"

        raise NotImplementedError()

        var_tmp = interfaces.StateVariable()
        
        k1 = timestep * self.derivative(variable = var_tmp)

        res = self.variable.value + (k1 + 2*k2 + 2*k3 + k4) / 6
        return res

    def euler(self, timestep = None):
        """ Integrate one step euler-forward and return the value.
        Args:
            timestep (single numeric value): The timestep. Defaults to
                max_timestep
        Returns:
            the value of self.variable after this euler-explicit timestep
        """
        if timestep is None: timestep = self.max_timestep # default
        assert utils.is_numeric(timestep), "timestep has to be numeric"
        assert np.asarray(timestep).size == 1, "timestep has to be one value"

        return self.variable.value + self.derivative() * timestep

    def integrate_step(self, timestep = None):
        """ Integrate one step forward and return - don't set - the value.
        Args:
            timestep (single numeric value): The timestep. Defaults to
                max_timestep
        Returns:
            the value of self.variable after this timestep
        """
        raise NotImplementedError("subclasses should override this method")

    def integrate(self, final_time = None):
        """ Integrate the equation until final_time. Set the variable's value
        in-place.  
        Args:
            final_time (single numeric value): the final time to integrate until
        """
        assert utils.is_numeric(final_time), "final_time has to be numeric"
        assert np.asarray(final_time).size == 1, \
            "final_time has to be a single value"

        orig_time_func = copy.copy(self.variable.time_function) # back up time_func
        # get current time
        int_time_now = orig_time_func() # get current start time

        assert final_time > int_time_now, "I refuse to integrate backwards!"

        def int_time_func(): return int_time_now # local time function
        self.variable.time_function = int_time_func # set local time function

        while int_time_now < final_time: # as long as we have time left
            time_left = final_time - int_time_now
            if time_left > self.max_timestep: # another maximum timestep fits
                timestep = self.max_timestep
            else: # fill the gap with small timestep
                timestep = time_left

            int_time_now += timestep # set new time NOW

            # integrate a step forward
            self.variable.value = self.integrate_step(timestep = timestep)

        self.variable.time_function = orig_time_func # reset to original function

        return True # return success


        


class DiagnosticEquation(Equation):
    """ Class to represent diagnostic equations
    """
    pass


class SetOfEquations(collections.MutableMapping,utils.ReprObject):
    """ Base class for sets of equations
    """
    def __init__(self, equations = [], equation_type = Equation):
        self.store = dict() # empty dict

        # set properties
        self.equation_type = equation_type
        self.equations = equations

    ##################
    ### Properties ###
    ##################
    @property
    def equations(self):
        """ return the list of values
        """
        return [self.store[x] for x in sorted(self.store)]

    @equations.setter
    def equations(self, newequations):
        """ Set new values via a list
        """
        assert isinstance(newequations, collections.Iterable), (
            "equations have to be list")
        # re-set the dict and fill it with new data
        tmp = dict() # temporary empty dict
        for i in range(len(newequations)):
            eq = newequations[i]
            assert issubclass(eq.__class__, self.equation_type), \
                ("new eqent nr. {i} is no object of subclass " 
                 "of {vtype} but of class {cls}").format(
                i=i,vtype=self.equation_type,cls=eq.__class__)
            assert not eq.variable.id in tmp.keys(), \
                "variable '{}' present multiple times".format(eq.variable.id)
            tmp.update({eq.variable.id:eq}) # add to temporary dict

        self.store = tmp.copy() # set internal dict

    @property
    def equation_type(self):
        try:                   self._equation_type
        except AttributeError: self._equation_type = Equation # default
        return self._equation_type

    @equation_type.setter
    def equation_type(self, newtype):
        assert inspect.isclass(newtype), \
            "equation_type has to be a class"
        assert issubclass(newtype, Equation), \
            "equation_type has to be subclass of Equation"
        self._equation_type = newtype

    ###############
    ### Methods ###
    ###############
    def add_element(self, newelement):
        tmp = self.equations.copy()
        tmp.append(newelement)
        self.equations = tmp

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        assert issubclass(value.__class__, self.equation_type), (
            "new value has to be of type {}").format(self.equation_type)
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __str__(self):
        """ Stringification: summary
        """
        string = "\n\n".join(str(x) for x in self.equations)
        if string:
            return string
        else:
            return "none"

