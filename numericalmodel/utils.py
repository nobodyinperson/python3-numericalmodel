#!/usr/bin/env python3
# system modules
import logging
import warnings
import inspect
import re
import datetime
import copy

# internal modules

# external modules
import numpy as np
from scipy.spatial import cKDTree


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

def utcnow():
    """ Return the current utc unix timestamp
    """
    ts = (datetime.datetime.utcnow() - datetime.datetime(1970,1,1)
        ).total_seconds()
    return ts

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
    def _full_variable_path(cls,var):
        """ Get the full string of a variable
        Args:
            var (variable): The variable to get the full string from
        Returns:
            class_str (str): The full usable variable string including the
                module 
        """
        if inspect.ismethod(var): # is a method
            string = "{module}.{cls}.{name}".format(
                name=var.__name__,cls=var.__self__.__class__.__name__,
                module=var.__module__)
        else:
            string = "{module}.{name}".format(
                name=var.__name__,module=var.__module__)
        return(string)

    def __repr__(self):
        """ python representation of this object
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


class LeftInterpolator(ReprObject, LoggerObject):
    """ Left-sided Interpolator for 1d data
    """
    def __init__(self, x = None, y = None, copy = False):
        """ class constructor
        Args:
            x (numeric): x values. Will be reshaped to (x.size,1).
            y (numeric): y values. Will be reshaped to (y.size,1).
            copy [Optional(bool)]: take shallow copies of x and y? 
                Defaults to False.
        """
        # set properties
        self.copy = copy
        if x is None: self.x = self._default_x
        else:         self.x = x
        if y is None: self.y = self._default_y
        else:         self.y = y

    @property
    def x(self):
        try:                   self._x
        except AttributeError: self._x = np.array([]).reshape(0,1)
        return self._x

    @x.setter
    def x(self, value):
        assert is_numeric(value), "x has to be numeric"

        if self.copy: value = copy.copy(value) # copy if desired

        value = np.asarray(value) # convert to array
        value.shape = (value.size, 1) # reshape

        self._x = value # set internal attribute
        self.kdtree = cKDTree(data = value) # refresh kdtree

    @property
    def _default_x(self):
        return np.array([np.nan])

    @property
    def y(self):
        try:                   self._y
        except AttributeError: self._y = self._default_y
        return self._y

    @y.setter
    def y(self, value):
        assert is_numeric(value), "y has to be numeric"

        if self.copy: value = copy.copy(value) # copy if desired

        value = np.asarray(value) # convert to array
        value.shape = (value.size, 1) # reshape
        self._y = value # set internal attribute

    @property
    def _default_y(self):
        return np.array([np.nan])
    
    @property
    def copy(self):
        try:                   self._copy
        except AttributeError: self._copy = False
        return self._copy

    @copy.setter
    def copy(self, value):
        self._copy = bool(value)

    @property
    def kdtree(self):
        try:                   self._kdtree
        except AttributeError: self._kdtree = cKDTree(data = self.x)
        return self._kdtree

    @kdtree.setter
    def kdtree(self, newkdtree):
        assert isinstance(newkdtree, cKDTree), "kdtree has to be cKDTree"
        assert (newkdtree.n,newkdtree.m) == self.x.shape, \
            "kdtree m and n do not match x shape"
        self._kdtree = newkdtree

    ###############
    ### Methods ###
    ###############
    def __call__(self, xnew, copy = False):
        """ When called, return the values LEFT of the given xnew values.
        Args:
            xnew (numeric): the x values to get the interpolated values from
            copy [Optional(bool)]: Initially copy the xnew shallowly? Default
            to False.  
        Returns:
            np.array of values
        """
        assert self.x.size == self.y.size, "x and y are not of same size"
        assert is_numeric(xnew), "xnew has to be numeric"

        if copy: t = copy.copy(xnew) # copy if desired
        else:    t = xnew # keep

        t = np.asarray(t) # convert to np.array
        origshape = t.shape # save original shape
        t.shape = (t.size,1) # reshape

        self.logger.debug("query for x:\n{}".format(t))

        dist, ind = self.kdtree.query( x = t, k = 2 ) # query two neighbors
        self.logger.debug("indices of 2 nearest neighbors:\n{}".format(ind))
        self.logger.debug("distances to 2 nearest neighbors:\n{}".format(dist))

        # inf_dist = np.where(np.invert(np.isfinite(dist)))
        # ind[inf_dist] -= 1

        self.logger.debug("x:\n{}".format(self.x))

        two_nearest_x = self.x[ind] # the x values of the 2 nearest neighbors
        # two_nearest_x.shape = ind.shape # get rid of redundant dimension
        self.logger.debug("x values of 2 nearest neighbors:\n{}".format(
            two_nearest_x))
        self.logger.debug("minima of x values of 2 nearest" 
            "neighbors:\n{}".format(two_nearest_x.min(axis=1)))
        left_neighbors_x_minpos = two_nearest_x.argmin(axis=1)
        self.logger.debug("positions of minima of x values of 2 nearest" 
            "neighbors:\n{}".format(left_neighbors_x_minpos))

        # TODO: This is still inefficient
        # There has to be a way to select different elements from every row
        # than to create a huge array with duplications and then only take
        # the diagonal elements...
        # np.choose could be a possibility...
        left_neighbors_ind = ind.take( 
            left_neighbors_x_minpos, axis = 1).diagonal()

        self.logger.debug("indices of LEFT nearest neighbors:\n{}".format(
            left_neighbors_ind))

        left_y = self.y[left_neighbors_ind]
        self.logger.debug("values of LEFT nearest neighbors:\n{}".format(
            left_y))

        left_y.shape = origshape # reshape back

        return left_y
