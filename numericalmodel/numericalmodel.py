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
            name = "unnamed numerical model",
            version = "0.0.1",
            description = "a numerical model",
            long_description = "This is a numerical model.",
            authors = "anonymous",
            parameters = interfaces.SetOfParameters(),
            forcing = interfaces.SetOfForcingValues(),
            variables = interfaces.SetOfStateVariables(),
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
        self.parameters = parameters
        self.forcing = forcing
        self.variables = variables

    ##################
    ### Properties ###
    ##################
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
