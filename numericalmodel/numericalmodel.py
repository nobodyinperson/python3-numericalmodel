#!/usr/bin/env python3
# system modules
import logging
import datetime
import textwrap

# internal modules
from .genericmodel import GenericModel
from . import interfaces
from . import equations
from . import utils

# external modules
import numpy as np

class NumericalModel(GenericModel):
    """ Class for numerical models
    """
    def __init__(self,
            name = None,
            version = None,
            description = None,
            long_description = None,
            authors = None,
            initial_time = None,
            timestep = None,
            parameters = None,
            forcing = None,
            variables = None,
            equations = None,
            ):
        """ Class constructor
        Args:
            name (str): the model name
            version (str): the model version
            description (str): a short model description
            long_description (str): an extended model description
            authors (str, list or dict): model authors.
                str: name of single author
                list: list of author names
                dict: dict of {'task': ['name1','name1']} pairs
            initial_time (float): initial model time (UTC unix timestamp)
            timestep (float): timestep
            parameters (SetOfParameters): model parameters
            forcing (SetOfForcingValues): model forcing
            variables (SetOfStateVariables): model state variables
            equations (SetOfEquations): model equations
        """

        # GenericModel constructor
        GenericModel.__init__(self,
            name = name,
            version = version,
            description = description,
            long_description = long_description,
            authors = authors,
            )

        self.logger = logging.getLogger(__name__) # logger

        # set properties
        if initial_time is None: self.initial_time = self._default_initial_time
        else:                    self.initial_time = initial_time
        if parameters is None: self.parameters = self._default_parameters
        else:                  self.parameters = parameters
        if forcing is None: self.forcing = self._default_forcing
        else:               self.forcing = forcing
        if variables is None: self.variables = self._default_variables
        else:                 self.variables = variables
        if equations is None: self.equations = self._default_equations
        else:                 self.equations = equations

    ##################
    ### Properties ###
    ##################
    @property
    def initial_time(self):
        """ Default name if none was given
        """
        try:                   self._initial_time
        except AttributeError: self._initial_time = self._default_initial_time
        return self._initial_time

    @initial_time.setter
    def initial_time(self,newtime):
        assert utils.is_numeric(newtime), "initial_time has to be numeric"
        assert np.array(newtime).size == 1, "initial_time has to be one value"
        self._initial_time = newtime

    @property
    def _default_initial_time(self):
        return utils.utcnow()

    @property
    def _default_name(self):
        """ Default name if none was given
        """
        return "numerical model"

    @property
    def _default_description(self):
        """ Default description if none was given
        """
        return "a numerical model"

    @property
    def _default_long_description(self):
        """ Default long_description if none was given
        """
        return "This is a numerical model."

    @property
    def timestep(self):
        try:                   self._timestep # already defined?
        except AttributeError: self._timestep = self._default_timestep
        return self._timestep # return

    @timestep.setter
    def timestep(self,newtimestep):
        assert utils.is_numeric(newtimestep), "timestep has to be numeric"
        assert np.asarray(newtimestep).size == 1, "timestep has to be one value"
        self._timestep = newtimestep

    @property
    def _default_timestep(self):
        """ Default timestep if none were given
        """
        return 1

    @property
    def parameters(self):
        try:                   self._parameters # already defined?
        except AttributeError: self._parameters = self._default_parameters
        return self._parameters # return

    @parameters.setter
    def parameters(self,newparameters):
        assert issubclass(newparameters.__class__, interfaces.SetOfParameters),\
            "parameters has to be object of subclass of SetOfParameters"
        self._parameters = newparameters
        self._parameters.time_function = self.get_model_time # set time function

    @property
    def _default_parameters(self):
        """ Default parameters if none were given
        """
        return interfaces.SetOfParameters()

    @property
    def forcing(self):
        try:                   self._forcing # already defined?
        except AttributeError: self._forcing = self._default_parameters
        return self._forcing # return

    @forcing.setter
    def forcing(self,newforcing):
        assert issubclass(newforcing.__class__, interfaces.SetOfForcingValues),\
            "forcing has to be object of subclass of SetOfForcingValues"
        self._forcing = newforcing
        self._forcing.time_function = self.get_model_time # set time function

    @property
    def _default_forcing(self):
        """ Default forcing if none was given
        """
        return interfaces.SetOfForcingValues()

    @property
    def variables(self):
        try:                   self._variables # already defined?
        except AttributeError: # default
            self._variables = interfaces.SetOfStateVariables() 
        return self._variables # return

    @variables.setter
    def variables(self,newvariables):
        assert issubclass(newvariables.__class__, 
            interfaces.SetOfStateVariables), \
            "variables has to be object of subclass of SetOfStateVariables"
        self._variables = newvariables
        self._variables.time_function = self.get_model_time # set time function

    @property
    def _default_variables(self):
        """ Default variables if none were given
        """
        return interfaces.SetOfStateVariables()

    @property
    def equations(self):
        try:                   self._equations # already defined?
        except AttributeError: self._equations = self._default_equations
        return self._equations # return

    @equations.setter
    def equations(self,newequations):
        assert issubclass(newequations.__class__, equations.SetOfEquations),\
            "equations has to be object of subclass of SetOfequations"
        self._equations = newequations
        self._equations.time_function = self.get_model_time # set time function

    @property
    def _default_equations(self):
        """ Default equations if none were given
        """
        return equations.SetOfEquations()


    @property
    def model_time(self):
        try:                   self._model_time # already defined?
        except AttributeError: self._model_time = self.initial_time # default
        return self._model_time # return

    @model_time.setter
    def model_time(self, newtime):
        assert utils.is_numeric(newtime), "model_time has to be numeric"
        assert np.array(newtime).size == 1, "model_time has to be one value"
        self._model_time = newtime

    ###############
    ### Methods ###
    ###############
    def get_model_time(self):
        """ The current model time
        """
        return self.model_time

    def integrate(self, final_time):
        """ Integrate the model until final_time
        Args:
            final_time (float): time to integrate until
        """
        self.logger.debug("start integration")
        while self.model_time < final_time:
            self.logger.debug("current model time {} is smaller than " 
                "final time {}".format(self.model_time, final_time))
            time_left = final_time - self.model_time
            if time_left > self.timestep: # another maximum timestep fits
                timestep = self.timestep
            else: # fill the gap with small timestep
                timestep = time_left
            # self.logger.debug("timestep left: {}".format(timestep))
            self.model_time = self.model_time + timestep
            for equation in self.equations.equations:
                # self.logger.debug("integrate equation {}".format(
                #     equation.description))
                equation.integrate(final_time = self.model_time + timestep)
        self.logger.debug("end of integration")

    def __str__(self):
        """ Stringification: summary
        """
        # GenericModel stringificator
        gm_string = GenericModel.__str__(self)

        string = textwrap.dedent(
            """
            {gm_string}
            
            ##################
            ### Model data ###
            ##################

            initial time: {initialtime}
            timestep : {timestep}

            #################
            ### Variables ###
            #################

            {variables}

            ##################
            ### Parameters ###
            ##################

            {parameters}

            ###############
            ### Forcing ###
            ###############

            {forcing}

            #################
            ### Equations ###
            #################

            {equations}

            """
            ).strip().format(
            initialtime = self.initial_time,
            timestep = self.timestep,
            gm_string = gm_string,
            parameters = self.parameters,
            variables = self.variables,
            forcing = self.forcing,
            equations = self.equations, 
            )

        return string
