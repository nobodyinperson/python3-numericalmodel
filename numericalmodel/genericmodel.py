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
            name = None,
            version = None,
            description = None,
            long_description = None,
            authors = None,
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
        if name is None: self.name = self._default_name
        else:            self.name = name
        if version is None: self.version = self._default_version
        else:               self.version = version
        if description is None: self.description = self._default_description
        else:                   self.description = description
        if long_description is None: 
            self.long_description = self._default_long_description
        else:
            self.long_description = long_description
        if authors is None: self.authors = self._default_authors
        else:               self.authors = authors

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
    def _default_name(self):
        """ Default name if none was given
        """
        return "generic model"

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
    def _default_description(self):
        """ Default description if none was given
        """
        return "a generic model"

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
    def _default_long_description(self):
        """ Default long_description if none was given
        """
        return "This is a generic model."

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
    def _default_version(self):
        """ Default version if none was given
        """
        return "0.0.1"

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

    @property
    def _default_authors(self):
        """ Default authors if none was given
        """
        return "anonymous"

    def __str__(self):
        """ Stringification: summary
        """
        if isinstance(self.authors,dict):
            author_str = "\n".join("{task}: {name}".format(
                task=task,name=name) for task,name in self.authors.items())
        elif isinstance(self.authors,list):
            author_str = "\n".join(self.authors)
        elif isinstance(self.authors,str):
            author_str = self.authors
        else:
            author_str = "?"

        string = (
            "###\n"
            "### \"{name}\" \n"
            "### - {description} -\n"
            "###  version {version}\n"
            "###\n\n"
            "by:\n"
            "{authors}\n\n"

            "{description}\n"
            "--------------------------------------------------------------\n"
            "{long_description}\n\n"
            ).format( 
            name = self.name,
            version = self.version,
            description = self.description,
            long_description = self.long_description,
            authors = author_str,
            )
        return string




