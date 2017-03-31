#!/usr/bin/env python3
# system modules
import logging
import warnings
import inspect
import re
import datetime
import collections

# internal modules

# external modules
import numpy as np


######################
### util functions ###
######################
def is_numeric(x):
    """ 
    Check if a given value is numeric, i.e. whether numeric operations can be
    done with it.  

    Args:
        x (any): the input value

    Returns:
        bool: ``True`` if the value is numeric, ``False`` otherwise
    """
    attrs = ['__add__', '__sub__', '__mul__', '__truediv__', '__pow__']
    return all(hasattr(x, attr) for attr in attrs)

def utcnow():
    """ 
    Get the current utc unix timestamp, i.e. the utc seconds since 01.01.1970.

    Returns:
        float : the current utc unix timestamp in seconds
    """
    ts = (datetime.datetime.utcnow() - datetime.datetime(1970,1,1)
        ).total_seconds()
    return ts

####################
### util classes ###
####################
class LoggerObject(object):
    """ 
    Simple base class that provides a 'logger' property

    Args:
        logger (logging.Logger): the logger to use
    """
    def __init__(self, logger = logging.getLogger(__name__)):
        # set logger
        self.logger = logger

    ##################
    ### Properties ###
    ##################
    @property
    def logger(self):
        """ 
        the :any:`logging.Logger` used for logging. Defaults to
        ``logging.getLogger(__name__)``.
        """
        try: # try to return the internal property
            return self._logger 
        except AttributeError: # didn't work
            name = self.__class__.__name__
            module = self.__class__.__module__
            string = "{module}.{name}".format(name=name,module=module)
            return logging.getLogger(string) # return default logger
    
    @logger.setter
    def logger(self, logger):
        assert isinstance(logger, logging.Logger), \
            "logger property has to be a logging.Logger"
        self._logger = logger


class ReprObject(object):
    """ 
    Simple base class that defines a :any:`__repr__` method based on an object's 
    ``__init__`` arguments and properties that are named equally. Subclasses of
    :any:`ReprObject` should thus make sure to have properties that are named
    equally as their ``__init__`` arguments.
    """
    @classmethod
    def _full_variable_path(cls,var):
        """ Get the full string of a variable

        Args:
            var (any): The variable to get the full string from

        Returns:
            str : The full usable variable string including the module 
        """
        if inspect.ismethod(var): # is a method
            string = "{module}.{cls}.{name}".format(
                name=var.__name__,cls=var.__self__.__class__.__name__,
                module=var.__module__)
        else:
            name = var.__name__
            module = var.__module__
            if module == "builtins":
                string = name
            else:
                string = "{module}.{name}".format(name=name,module=module)
        return(string)

    def __repr__(self):
        """ 
        Python representation of this object

        Returns:
            str : a Python representation of this object based on its
            ``__init__`` arguments and corresponding properties.
        """
        indent = "    "
        # the current "full" classname
        classname = self._full_variable_path(self.__class__)

        # get a dict of {'argname':'property value'} from init arguments
        init_arg_names = inspect.getfullargspec(self.__init__).args
        init_args = {} # start with empty dict
        for arg in init_arg_names:
            if arg == "self": continue # TODO hard-coded 'self' is bad
            try:
                attr = getattr(self,arg) # get the attribute
                try:
                    string = self._full_variable_path(attr)
                except:
                    string = repr(attr)

                # indent the arguments
                init_args[arg] = re.sub( 
                    string = string,
                    pattern = "\n",
                    repl = "\n" + indent,
                    )
            except AttributeError: # no such attribute
                warnstr = ("class {cls} has no property or attribute " 
                    "'{arg}' like the argument in its __init__. Cannot include " 
                    "argument '{arg}' into __repr__.").format(
                    cls=classname,arg=arg)
                warnings.warn(warnstr)

        # create "arg = {arg}" string list for reprformat
        args_kv = []
        for arg in init_args.keys():
            args_kv.append(indent + "{arg} = {{{arg}}}".format(arg=arg))

        # create the format string
        if args_kv: # if there are arguments
            reprformatstr = "\n".join([
                "{____classname}(", ",\n".join(args_kv), indent+")", ])
        else: # no arguments
            reprformatstr = "{____classname}()"
            

        # add classname to format args
        reprformatargs = init_args.copy()
        reprformatargs.update({"____classname":classname})

        reprstring = (reprformatstr).format(**reprformatargs)
        return reprstring


class SetOfObjects(ReprObject, LoggerObject, collections.MutableMapping):
    """ 
    Base class for sets of objects
    """
    def __init__(self, elements = [], element_type = object):
        self.store = dict() # empty dict

        # set properties
        self.element_type = element_type
        self.elements = elements

    ##################
    ### Properties ###
    ##################
    @property
    def elements(self):
        """ 
        return the list of values
        
        :getter:
            get the list of values
        :setter:
            set the list of values. Make sure, every element in the list is an
            instance of (a subclass of) :any:`element_type`.
        :type: :any:`list`
        """
        return [self.store[x] for x in sorted(self.store)]

    @elements.setter
    def elements(self, newelements):
        assert isinstance(newelements, collections.Iterable), (
            "elements have to be list")
        # re-set the dict and fill it with new data
        tmp = dict() # temporary empty dict
        for i in range(len(newelements)):
            elem = newelements[i]
            assert isinstance(elem, self.element_type), \
                ("new element nr. {i} is instance of <{cls}> " 
                 "which is not subclass of <{vtype}>.").format( i=i,
                vtype=self.element_type.__name__,
                cls=elem.__class__.__name__,)
            key = self._object_to_key(elem) # get the key
            assert not key in tmp, \
                "element '{}' present multiple times".format(key)
            tmp.update({key:elem}) # add to temporary dict

        self.store = tmp.copy() # set internal dict

    @property
    def element_type(self):
        """ 
        The base type the elements in the set should have
        """
        try:                   self._element_type
        except AttributeError: self._element_type = object # default
        return self._element_type

    @element_type.setter
    def element_type(self, newtype):
        assert inspect.isclass(newtype), "element_type has to be a class"
        self._element_type = newtype

    ###############
    ### Methods ###
    ###############
    def _object_to_key(self, obj):
        """ key transformation function. Subclasses should override this.

        Args:
            obj (object): object

        Returns:
            str : the unique key for this object. Defaults to ``repr(obj)``
        """
        return repr(obj) # by default, return the object's repr 

    def add_element(self, newelement):
        """ 
        Add an element to the set

        Args:
            newelement (object of type :any:`element_type`): the new element
        """
        tmp = self.elements.copy() # TODO does this destroy references?
        tmp.append(newelement)
        self.elements = tmp

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        assert issubclass(value.__class__, self.element_type), (
            "new value has to be of type {}").format(self.element_type)
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __str__(self): # pragma: no cover
        """ 
        Stringification

        Returns:
            str : a summary
        """
        string = "\n\n".join(str(x) for x in self.elements)
        if string:
            return string
        else:
            return "none"

