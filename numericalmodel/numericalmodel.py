#!/usr/bin/env python3
# system modules
import logging
import datetime
import textwrap

# internal modules
from .genericmodel import GenericModel
from . import interfaces
from . import numericalschemes
from . import utils

# external modules
import numpy as np

class NumericalModel(GenericModel):
    """ 
    Class for numerical models

    Args:
        name (str, optional): the model name
        version (str, optional): the model version
        description (str, optional): a short model description
        long_description (str, optional): an extended model description
        authors (str, list or dict, optional): model authors.
            str: name of single author
            list: list of author names
            dict: dict of {'task': ['name1','name1']} pairs
        initial_time (float): initial model time (UTC unix timestamp)
        parameters (SetOfParameters, optional): model parameters
        forcing (SetOfForcingValues, optional): model forcing
        variables (SetOfStateVariables, optional): model state variables
        numericalschemes (SetOfNumericalSchemes, optional): model schemes with
            equation
    """
    def __init__(self,
            name = None,
            version = None,
            description = None,
            long_description = None,
            authors = None,
            initial_time = None,
            parameters = None,
            forcing = None,
            variables = None,
            numericalschemes = None,
            ):
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
        if numericalschemes is None: 
            self.numericalschemes = self._default_numericalschemes
        else:                 self.numericalschemes = numericalschemes

    ##################
    ### Properties ###
    ##################
    @property
    def initial_time(self):
        """ 
        The initial model time
        
        :type: :any:`float`
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
        """ 
        Default initial model time if none was given
        
        :type: :any:`float`
        """
        return utils.utcnow()

    @property
    def _default_name(self):
        """ 
        Default name if none was given
        
        :type: :any:`str`
        """
        return "numerical model"

    @property
    def _default_description(self):
        """ 
        Default description if none was given
        
        :type: :any:`str`
        """
        return "a numerical model"

    @property
    def _default_long_description(self):
        """ 
        Default long_description if none was given
        
        :type: :any:`str`
        """
        return "This is a numerical model."

    @property
    def parameters(self):
        """ 
        The model parameters
        
        :type: :any:`SetOfParameters`
        """
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
        """ 
        Default parameters if none were given
        
        :type: :any:`SetOfParameters`
        """
        return interfaces.SetOfParameters()

    @property
    def forcing(self):
        """ 
        The model forcing

        :type: :any:`SetOfForcingValues`
        """
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
        """ 
        Default forcing if none was given

        :type: :any:`SetOfForcingValues`
        """
        return interfaces.SetOfForcingValues()

    @property
    def variables(self):
        """ 
        The model variables

        :type: :any:`SetOfStateVariables`
        """
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
        """ 
        Default variables if none were given

        :type: :any:`SetOfStateVariables`
        """
        return interfaces.SetOfStateVariables()

    @property
    def numericalschemes(self):
        """ 
        The model numerical schemes

        :type: :any:`str`
        """
        try:                   self._numericalschemes # already defined?
        except AttributeError: self._numericalschemes = self._default_numericalschemes
        return self._numericalschemes # return

    @numericalschemes.setter
    def numericalschemes(self,newnumericalschemes):
        assert isinstance(newnumericalschemes, 
            numericalschemes.SetOfNumericalSchemes),\
            "numericalschemes has to be instance of SetOfNumericalSchemes"
        self._numericalschemes = newnumericalschemes

    @property
    def _default_numericalschemes(self):
        """ 
        Default numerical schemes if none were given
        
        :type: :any:`SetOfNumericalSchemes`
        """
        return numericalschemes.SetOfNumericalSchemes()


    @property
    def model_time(self):
        """
        The current model time

        :type: :any:`float`
        """
        try:                   self._model_time # already defined?
        except AttributeError: self._model_time = self.initial_time # default
        return float(self._model_time) # return

    @model_time.setter
    def model_time(self, newtime):
        assert utils.is_numeric(newtime), "model_time has to be numeric"
        assert np.array(newtime).size == 1, "model_time has to be one value"
        self._model_time = float(newtime)

    ###############
    ### Methods ###
    ###############
    def get_model_time(self):
        """ 
        The current model time

        Returns:
            float: current model time
        """
        return self.model_time

    def integrate(self, final_time):
        """ Integrate the model until final_time

        Args:
            final_time (float): time to integrate until
        """
        self.logger.info("start integration")
        self.numericalschemes.integrate( 
            start_time = self.model_time,
            final_time = final_time,
            )
        self.logger.info("end of integration")

    def __str__(self):
        """ 
        Stringification

        Returns:
            str : a summary
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

            ###############
            ### Schemes ###
            ###############

            {schemes}

            """
            ).strip().format(
            initialtime = self.initial_time,
            gm_string = gm_string,
            parameters = self.parameters,
            variables = self.variables,
            forcing = self.forcing,
            schemes = self.numericalschemes, 
            )

        return string
