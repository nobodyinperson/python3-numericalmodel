#!/usr/bin/env python3
# system modules
import textwrap

# internal modules
from . import equations
from . import utils

# external modules
import numpy as np


class NumericalScheme(utils.ReprObject,utils.LoggerObject):
    """ Base class for numerical schemes
    """
    def __init__(self, description = None, long_description = None,
        equation = None, max_timestep = None):
        """ Class constructor
        Args:
            description (str): short equation description
            long_description (str): long equation description
            equation (DerivativeEquation): the equation
        """
        if equation is None: self.equation = self._default_equation
        else:                self.equation = equation
        if max_timestep is None: self.max_timestep = self._default_max_timestep
        else:                self.max_timestep = max_timestep
        if description is None: self.description = self._default_description
        else:                   self.description = description
        if long_description is None: 
            self.long_description = self._default_long_description
        else:                   self.long_description = long_description

    ##################
    ### Properties ###
    ##################
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
        return "a numerical scheme"

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
        return "This is a numerical scheme to solve a derivative equation."

    @property
    def max_timestep(self):
        try:                   self._max_timestep
        except AttributeError: 
            self._max_timestep = self._default_max_timestep
        return self._max_timestep

    @max_timestep.setter
    def max_timestep(self, newmax_timestep):
        assert utils.is_numeric(newmax_timestep), \
            "max_timestep has to be numeric"
        assert np.asarray(newmax_timestep).size == 1, \
            "max_timestep has to be of size 1"
        self._max_timestep = float(newmax_timestep)
        
    @property
    def _default_max_timestep(self):
        return 1

    @property
    def equation(self):
        try:                   self._equation
        except AttributeError: self._equation = self._default_equation
        return self._equation

    @equation.setter
    def equation(self, newequation):
        assert isinstance(newequation, equations.DerivativeEquation), \
            "equation has to be instance of subclass of DerivativeEquation"
        self._equation = newequation
        
    @property
    def _default_equation(self):
        return equations.DerivativeEquation()

    ###############
    ### Methods ###
    ###############
    def needed_timesteps(self, timestep):
        """ Given a timestep to integrate from now on, what other timesteps of
        the dependencies are needed?
        Args:
            timestep (single numeric value): the timestep to calculate 
        Returns:
            np.array of needed timesteps
        Note:
            timestep 0 means current time
        """
        assert utils.is_numeric(timestep), "timestep needs to be numeric"
        ts = np.asarray(timestep)
        assert ts.size == 1, "timestep needs to be one single value"
        return self._needed_timesteps_for_integration_step(timestep = ts)

    def _needed_timesteps_for_integration_step(self, timestep = None):
        raise NotImplementedError("Subclasses should override this")

    def integrate_step(self, time = None, timestep = None):
        """ Integrate "timestep" forward and set results in-place
        Args:
            time (single numeric): The time to calculate the step FROM. Defaults
                to the current variable time.
            timestep (single numeric): The timestep to calculate the step.
                Defaults to max_timestep.
        """
        pass

    def step(self, time, timestep):
        """ Integrate one "timtstep" from "time" forward and return value
        Args:
            time (single numeric): The time to calculate the step FROM
            timestep (single numeric): The timestep to calculate the step
        Returns:
            res (np.array): The resulting variable value
        """
        raise NotImplementedError("Subclasses should override this")

    def __str__(self):
        """ Stringification: summary
        """
        string = (
        " \"{description}\" \n"
        "{long_description}\n"
        "maximum timestep: {max_timestep} \n"
        "[numerical scheme for equation:] \n"
        "{equation}\n"
        ).format(description=self.description, 
            equation = textwrap.indent(text=str(self.equation),prefix="> "),
            max_timestep = self.max_timestep,
            variable=self.equation.variable.id,
            long_description = self.long_description)
        return string


class EulerExplicit(NumericalScheme):
    """ Euler-explicit numerical scheme
    """
    def step(self, time, timestep):
        d = self.equation.derivative
        v = self.equation.variable
        res = v(time) + timestep * d(time)
        return res

    def _needed_timesteps_for_integration_step(self, timestep = None):
        return np.array([0]) # only current time needed

class EulerImplicit(NumericalScheme):
    """ Euler-implicit numerical scheme
    """
    def step(self, time = None, timestep = None):
        d = self.equation.derivative
        v = self.equation.variable
        res = v(time) + timestep * d(time)

    def _needed_timesteps_for_integration_step(self, timestep):
        return np.array([0,1]) * timestep # current time and timestep needed

class LeapFrog(NumericalScheme):
    """ Leap-Frog numerical scheme
    """
    def _needed_timesteps_for_integration_step(self, timestep):
        return np.array([-1,0]) * timestep # prev time and current time needed

class RungeKutta4(NumericalScheme):
    """ Runte-Kutta-4 numerical scheme
    """
    def _needed_timesteps_for_integration_step(self, timestep):
        return np.array([0,0.5,1]) * timestep # current time, half and full 
