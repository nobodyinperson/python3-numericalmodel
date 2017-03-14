#!/usr/bin/env python3
# system modules
import logging

# internal modules
from .genericmodel import GenericModel
from . import interfaces

# external modules

class NumericalModel(GenericModel):
    """ Class for numerical models
    """
    def __init__(self,
            name = None,
            version = None,
            description = None,
            long_description = None,
            authors = None,
            parameters = None,
            forcing = None,
            variables = None,
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
            parameters (SetOfParameters): model parameters
            forcing (SetOfForcingValues): model forcing
            variables (SetOfStateVariables): model state variables
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
        if parameters is None: self.parameters = self._default_parameters
        else:                  self.parameters = parameters
        if forcing is None: self.forcing = self._default_forcing
        else:               self.forcing = forcing
        if variables is None: self.variables = self._default_variables
        else:                 self.variables = variables

    ##################
    ### Properties ###
    ##################
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
    def parameters(self):
        try:                   self._parameters # already defined?
        except AttributeError: self._parameters = interfaces.SetOfParameters()
        return self._parameters # return

    @parameters.setter
    def parameters(self,newparameters):
        assert issubclass(newparameters.__class__, interfaces.SetOfParameters),\
            "parameters has to be object of subclass of SetOfParameters"
        self._parameters = newparameters

    @property
    def _default_parameters(self):
        """ Default parameters if none were given
        """
        return interfaces.SetOfParameters()

    @property
    def forcing(self):
        try:                   self._forcing # already defined?
        except AttributeError: self._forcing = interfaces.SetOfForcingValues() 
        return self._forcing # return

    @forcing.setter
    def forcing(self,newforcing):
        assert issubclass(newforcing.__class__, interfaces.SetOfForcingValues),\
            "forcing has to be object of subclass of SetOfForcingValues"
        self._forcing = newforcing

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

    @property
    def _default_variables(self):
        """ Default variables if none were given
        """
        return interfaces.SetOfStateVariables()

    def __str__(self):
        """ Stringification: summary
        """
        # GenericModel stringificator
        gm_string = GenericModel.__str__(self)

        string = (
            "{gm_string}\n\n"
            "#################\n"
            "### Variables ###\n"
            "#################\n\n"
            "{variables}\n\n"
            "##################\n"
            "### Parameters ###\n"
            "##################\n\n"
            "{parameters}\n\n"
            "###############\n"
            "### Forcing ###\n"
            "###############\n\n"
            "{forcing}\n"
            ).format(
            gm_string = gm_string,
            parameters = self.parameters,
            variables = self.variables,
            forcing = self.forcing,
            )

        return string
