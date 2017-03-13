#!/usr/bin/env python3
# system modules
import logging

# internal modules
from .genericmodel import GenericModel

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

    ##################
    ### Properties ###
    ##################
    @property
    def parameters(self):
        try:                   self._parameters # already defined?
        except AttributeError: self._parameters = "" # default
        return self._parameters # return

    @parameters.setter
    def parameters(self,newparameters):
        assert isinstance(newparameters, str), "parameters has to be str"
        self._parameters = newparameters
