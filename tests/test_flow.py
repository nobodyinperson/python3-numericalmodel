# -*- coding: utf-8 -*-
# System modules
import os
import logging
import unittest
import json
from functools import wraps

# External modules

# Internal modules
from .test_data import *

# get a logger
logger = logging.getLogger(__name__)


####################################
### all tests should import this ###
####################################

# basic test class with utilities
class BasicTest(unittest.TestCase):
    ##################
    ### Properties ###
    ##################
    @property
    def logger(self):
        """ the logging.Logger used for logging.
        Defaults to logging.getLogger(__name__).
        """
        try: # try to return the internal property
            return self._logger 
        except AttributeError: # didn't work
            return logging.getLogger(__name__) # return default logger
    
    @logger.setter
    def logger(self, logger):
        assert isinstance(logger, logging.Logger), \
            "logger property has to be a logging.Logger"
        self._logger = logger

# test decorator
# decorate every test method with this
# the test name will be printed in INFO context before and after the test
def testname(name="unnamed"):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            logger.info("--- [start] »{}« test ---".format(name))
            res = f(*args, **kwargs)
            logger.info("--- [done ] »{}« test ---".format(name))
            return res
        return wrapped
    return decorator


# read json from a filename
def read_json_from_file(filename):
    """
    read json from a file given then filename
    args:
        filename (str): The path to the file to read
    returns:
        dict, empty dict if error occured during read
    """
    try: # open and read, return result
        with open(filename, "r") as f:
            return json.load(f)
    except: # didn't work, return empty dict
        return {}

# get all subclasses of a given class
def all_subclasses(cls):
    subclasses = set()

    for subclass in cls.__subclasses__():
        subclasses.add(subclass)
        subclasses.update(all_subclasses(subclass))

    return subclasses
