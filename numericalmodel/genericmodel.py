#!/usr/bin/env python3
# system modules
import logging

# internal modules
from . import utils

# external modules

class GenericModel(utils.LoggerObject,utils.ReprObject):
    """ 
    Base class for models

    Args:
        name (str, optional): the model name
        version (str, optional): the model version
        description (str): a short model description
        long_description (str): an extended model description
        authors (:any:`str`, :any:`list` or :any:`dict`, optional): 
            the model author(s). One of

            :any:`str`: 
                name of single author
            :any:`list` of :any:`str`: 
                :any:`list` of author names
            :any:`dict`: 
                :any:`dict` of ``{'task': ['name1','name1']}`` pairs
    """
    def __init__(self,
            name = None,
            version = None,
            description = None,
            long_description = None,
            authors = None,
            ):

        self.logger = logging.getLogger(__name__) # logger 

        # set properties
        if not name is None: 
            self.name = name
        if not version is None: 
            self.version = version
        if not description is None: 
            self.description = description
        if not long_description is None: 
            self.long_description = long_description
        if not authors is None: 
            self.authors = authors

    ##################
    ### Properties ###
    ##################
    @property
    def name(self):
        """ 
        The model name

        :type: :any:`str`
        """
        try:                   self._name # already defined?
        except AttributeError: self._name = "unnamed model" # default
        return self._name # return

    @name.setter
    def name(self,newname):
        assert isinstance(newname, str), "name has to be str"
        self._name = newname

    @property
    def _default_name(self):
        """ 
        Default name if none was given

        :type: :any:`str`
        """
        return "generic model"

    @property
    def description(self):
        """ 
        The model description

        :type: :any:`str`
        """
        try:                   self._description # already defined?
        except AttributeError: self._description = "" # default
        return self._description # return

    @description.setter
    def description(self,newdescription):
        assert isinstance(newdescription, str), "description has to be str"
        self._description = newdescription

    @property
    def _default_description(self):
        """ 
        Default description if none was given

        :type: :any:`str`
        """
        return "a generic model"

    @property
    def long_description(self):
        """ 
        Longer model description

        :type: :any:`str`
        """
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
        """ 
        Default long_description if none was given

        :type: :any:`str`
        """
        return "This is a generic model."

    @property
    def version(self):
        """ 
        The model version

        :type: :any:`str`
        """
        try:                   self._version # already defined?
        except AttributeError: self._version = "0.0.1" # default
        return self._version # return

    @version.setter
    def version(self,newversion):
        assert isinstance(newversion, str), "version has to be str"
        self._version = newversion

    @property
    def _default_version(self):
        """ 
        Default version if none was given

        :type: :any:`str`
        """
        return "0.0.1"

    @property
    def authors(self):
        """ 
        The model author(s)

        :any:`str`: 
            name of single author
        :any:`list` of :any:`str`: 
            :any:`list` of author names
        :any:`dict`: 
            :any:`dict` of ``{'task': ['name1','name1']}`` pairs
        """
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
        """ 
        Default authors if none were given

        :type: :any:`str`
        """
        return "anonymous"

    def __str__(self): # pragma: no cover
        """ 
        Stringification

        Returns:
            str : a summary
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




