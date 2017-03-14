#!/usr/bin/env python3
# system modules
import logging
import warnings
import inspect
import re

# internal modules

# external modules


######################
### util functions ###
######################
def is_numeric(x):
    """ Check if a given value is numeric, i.e. whether numeric operations can
    be done with it.  
    Args:
        x (any): the input value
    Returns:
        bool: True if the value is numeric, False otherwise
    """
    attrs = ['__add__', '__sub__', '__mul__', '__truediv__', '__pow__']
    return all(hasattr(x, attr) for attr in attrs)

####################
### util classes ###
####################
class LoggerObject(object):
    """ Simple base class that provides a 'logger' property
    """
    def __init__(self, logger = logging.getLogger(__name__)):
        """ class constructor
        Args:
            logger (logging.Logger): the logger to use
        """
        # set logger
        self.logger = logger

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


class ReprObject(object):
    """ Simple base class that defines a __repr__ method based on its __init__
        arguments and properties that are named equally.
    """
    @classmethod
    def _full_string_of_class(clss,cls):
        """ Get the full string of a class
        Args:
            cls (class): The class to get the full string from
        Returns:
            class_str (str): The full usable class string including the module
        """
        assert inspect.isclass(cls), "cls needs to be class"
        string = "{module}.{name}".format(
            name=cls.__name__,module=cls.__module__)
        return(string)

    def __repr__(self):
        """ python representation of this object
        """
        indent = "    "
        # the current "full" classname
        classname = self._full_string_of_class(self.__class__)

        # get a dict of {'argname':'property value'} from init arguments
        init_arg_names = inspect.getfullargspec(self.__init__).args
        init_args = {} # start with empty dict
        for arg in init_arg_names:
            if arg == "self": continue
            try:
                attr = getattr(self,arg) # get the attribute
                if inspect.isclass(attr): # if it is a class
                    # convert to Python-like class string
                    string = self._full_string_of_class(attr)
                else: # not a class
                    string = repr(attr) # just the repr of the attribute

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


