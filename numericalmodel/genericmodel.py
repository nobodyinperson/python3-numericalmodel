#!/usr/bin/env python3
# system modules
import logging

# internal modules
from . import utils

# external modules

class GenericModel(utils.LoggerObject,utils.ReprObject):
    """ Base class for models
    """
    def __init__(self,
            name = "unnamed model",
            version = "0.0.1",
            description = "a generic model",
            long_description = "This is a generic model.",
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

        self.logger = logging.getLogger(__name__) # logger 

        # set properties
        self.name = name 
        self.version = version 
        self.description = description 
        self.long_description = long_description
        self.authors = authors 

    ##################
    ### Properties ###
    ##################
    @property
    def name(self):
        try:                   self._name # already defined?
        except AttributeError: self._name = "unnamed model" # default
        return self._name # return

    @name.setter
    def name(self,newname):
        assert isinstance(newname, str), "name has to be str"
        self._name = newname

    @property
    def description(self):
        try:                   self._description # already defined?
        except AttributeError: self._description = "" # default
        return self._description # return

    @description.setter
    def description(self,newdescription):
        assert isinstance(newdescription, str), "description has to be str"
        self._description = newdescription

    @property
    def long_description(self):
        try:                   self._long_description # already defined?
        except AttributeError: self._long_description = "" # default
        return self._long_description # return

    @long_description.setter
    def long_description(self,newlong_description):
        assert isinstance(newlong_description, str), \
            "long_description has to be str"
        self._long_description = newlong_description

    @property
    def version(self):
        try:                   self._version # already defined?
        except AttributeError: self._version = "0.0.1" # default
        return self._version # return

    @version.setter
    def version(self,newversion):
        assert isinstance(newversion, str), "version has to be str"
        self._version = newversion

    @property
    def authors(self):
        try:                   self._authors # already defined?
        except AttributeError: self._authors = "anonymous" # default
        return self._authors # return

    @authors.setter
    def authors(self,newauthors):
        assert isinstance(newauthors, str)  \
            or isinstance(newauthors, list) \
            or isinstance(newauthors, dict) \
               ,"authors has to be str, list or dict"
        self._authors = newauthors



