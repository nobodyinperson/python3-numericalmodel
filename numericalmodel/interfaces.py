#!/usr/bin/env python3
# system modules
import logging
import collections
import inspect

# internal modules
from . import utils

# external modules
import numpy as np
import scipy.interpolate

class InterfaceValue(utils.LoggerObject,utils.ReprObject):
    """ Base class for model interface values
    """
    def __init__(self,
        name = None,
        id = None,
        unit = None,
        time_function = None,
        interpolation = None,
        values = None,
        times = None,
        ):
        """ Class constructor
        Args:
            name (str): value name
            id (str): unique id
            values (1d np.array): all values this InterfaceValue had in 
                chronological order
            times (1d np.array): the corresponding times to values
            unit (str): physical unit of value
            interpolation (str): interpolation kind. See
                scipy.interpolate.interp1d for documentation. Defaults to 
                "zero".
            time_function (callable): function that returns the model time as 
                utc unix timestamp
        """
        # set properties
        if time_function is None:  
            self.time_function = self._default_time_function
        else:             self.time_function = time_function
        if name is None:  self.name = self._default_name
        else:             self.name = name
        if unit is None:  self.unit = self._default_unit
        else:             self.unit = unit
        if id is None:    self.id = self._default_id
        else:             self.id = id
        if values is None:self.values = self._default_values
        else:             self.values = values
        if times is None: self.times = self._default_times
        else:             self.times = times
        if interpolation is None: 
            self.interpolation = self._default_interpolation
        else:             self.interpolation = interpolation


    ##################
    ### Properties ###
    ##################
    @property
    def time_function(self):
        try:                   self._time_function # already defined?
        except AttributeError: self._time_function = self._default_time_function
        return self._time_function # return

    @time_function.setter
    def time_function(self,newtime_function):
        assert hasattr(newtime_function,'__call__'), \
            "time_function has to be callable"
        self._time_function = newtime_function 

    @property
    def _default_time_function(self):
        """ Default time_function if none was given. Subclasses should
        overrtime_functione this.  
        """
        return utils.utcnow

    @property
    def id(self):
        try:                   self._id # already defined?
        except AttributeError: self._id = self._default_id # default
        return self._id # return

    @id.setter
    def id(self,newid):
        assert isinstance(newid,str), "id has to be str"
        self._id = newid 

    @property
    def _default_id(self):
        """ Default id if none was given. Subclasses should override this.
        """
        return "unnamed_variable"

    @property
    def unit(self):
        try:                   self._unit # already defined?
        except AttributeError: self._unit = self._default_unit # default
        return self._unit # return

    @unit.setter
    def unit(self,newunit):
        assert isinstance(newunit,str), "unit has to be str"
        self._unit = newunit 

    @property
    def _default_unit(self):
        """ Default unit if none was given. Subclasses should override this.
        """
        return "1"

    @property
    def name(self):
        try:                   self._name # already defined?
        except AttributeError: self._name = self._default_name # default
        return self._name # return

    @name.setter
    def name(self,newname):
        assert isinstance(newname,str), "name has to be str"
        self._name = newname 

    @property
    def _default_name(self):
        """ Default name if none was given. Subclasses should override this.
        """
        return "unnamed value"

    @property
    def value(self):
        return self() # call us

    @value.setter
    def value(self,newvalue):
        assert utils.is_numeric(newvalue), "value has to be numeric"
        val = np.asarray(newvalue) # convert to numpy array
        assert val.size == 1, "value has to be of size one"
        # append to log
        t = self.next_time # the next time
        ind = self.times == t # indices where this next time is already present
        if np.any(ind): # time already there?
            self.values[ind] = val # replace value
            # self.logger.debug("time {t} already there, " 
            #     "overwriting value to {val}".format(t=t,val=val))
        else: # new time
            self.times = np.append(self.times, t)
            self.values = np.append(self.values, val)
            # self.logger.debug("time {t} not yet there, " 
            #     "appending value {val}".format(t=t,val=val))

    @property
    def values(self):
        """ All values this InterfaceValue has ever had in chronological order
        """
        try:                   self._values # already defined?
        except AttributeError: self._values = self._default_times # default
        return self._values # return

    @values.setter
    def values(self,newvalues):
        assert isinstance(newvalues,np.ndarray), "values have to be np.array"
        assert newvalues.size == np.prod(newvalues.shape), \
            "values have to be one-dimensional" 
        self._values = newvalues
        # reset intepolator
        self.interpolator = None

    @property
    def _default_values(self):
        return np.array([]) # empty array

    @property
    def next_time(self):
        """ The next time to use when value is set. Defaults to the value of
        time_function if no next_time was set.
        """
        try:                   next_time = self._next_time
        except AttributeError: next_time = self.time_function()
        if self.times.size:
            assert next_time >= self.times.max(), \
                "next_time has to be later than current time"
        return next_time

    @next_time.setter
    def next_time(self, newtime):
        if newtime is None: # if set to none
            if hasattr(self, "_next_time"): del self._next_time # delete attribute
        else: # set to something else
            assert utils.is_numeric(newtime), "next_time has to be numeric"
            assert np.asarray(newtime).size == 1, \
                "next_time has to be one value"
            if self.times.size:
                assert newtime >= self.times.max(), \
                    "next_time has to be later than current time"
            self._next_time = newtime

    @property
    def time(self):
        return self.times[-1]

    @property
    def times(self):
        """ All times this InterfaceValue has ever been changed in chronological
        order 
        """
        try:                   self._times # already defined?
        except AttributeError: self._times = self._default_times # default
        return self._times # return

    @times.setter
    def times(self,newtimes):
        assert isinstance(newtimes,np.ndarray), "times have to be np.array"
        assert newtimes.size == np.prod(newtimes.shape), \
            "times have to be one-dimensional" 
        assert np.all(np.diff(newtimes)>0), "times must be strictly increasing"
        self._times = newtimes
        # reset intepolator
        self.interpolator = None

    @property
    def _default_times(self):
        return np.array([]) # empty array

    @property
    def interpolation(self):
        try:                   self._interpolation # already defined?
        except AttributeError: self._interpolation = self._default_interpolation
        return self._interpolation # return

    @interpolation.setter
    def interpolation(self,newinterpolation):
        assert isinstance(newinterpolation,str), "interpolation has to be str"
        if newinterpolation != self.interpolation: # really new value
            if hasattr(self, "_interpolator"):
                del self._interpolator # reset interpolator
        self._interpolation = newinterpolation 

    @property
    def _default_interpolation(self):
        """ Default interpolation if none was given. Subclasses may override
        this.
        """
        return "zero"

    @property
    def interpolator(self):
        try: self._interpolator # try to access internal attribute
        except AttributeError: # doesn't exist
            self._interpolator = scipy.interpolate.interp1d( 
                x = self.times, # the times
                y = self.values, # the values
                assume_sorted = True, # times are already sorted
                copy = False, # don't copy
                kind = self.interpolation, # interpolation kind
                bounds_error = False, # don't escalate on outside values
                fill_value = (self.values[self.times.argmin()],
                              self.values[self.times.argmax()]), # fill 
                )
        return self._interpolator

    @interpolator.setter
    def interpolator(self, value):
        if value is None: # reset the interpolator
            if hasattr(self, "_interpolator"): del self._interpolator
            return
        assert hasattr(value, "__call__"), "interpolator needs to be callable"
        self._interpolator = value

    def __call__(self, times = None):
        """ When called, return the value, optionally at a specific time
        Args:
            times [Optional(numeric)]: The times to obtain data from
        """
        assert self.times.size, "{}: no values recorded yet".format(self.name)
        if times is None:
            # no time given or only one value there
            return self.values[-1]
        assert utils.is_numeric(times), "times have to be numeric"
        times = np.asarray(times) # convert to numpy array
        if self.times.size == 1: 
            return np.ones_like(times) * self.values[-1]

        if self.interpolation == "zero":
            # "zero" interoplation returns the left neighbour on the last value?
            # not the last value itselt? Strange...
            # If we request this specific time, we want to have it!
            return self.interpolator(times+1e-10) # return
        else:
            return self.interpolator(times) # return

    def __str__(self):
        """ Stringification: summary
        """
        if self.values.size: value = self.value
        else:                value = "?"
        string = (
        " \"{name}\" \n"
        "--- {id} [{unit}] ---\n"
        "currently: {value} [{unit}]\n"
        "interpolation: {interp} \n"
        "{nr} total recorded values"
        ).format(id=self.id,unit=self.unit,interp=self.interpolation,
        name=self.name,value=value,nr=self.values.size)
        return string
        
####################################
### Subclasses of InterfaceValue ###
####################################
class ForcingValue(InterfaceValue):
    """ Class for forcing values
    """
    @property
    def _default_id(self):
        return "unnamed_forcing_value"

    @property
    def _default_name(self):
        return "unnamed forcing value"

    @property
    def _default_interpolation(self):
        return "linear"

class Parameter(InterfaceValue):
    """ Class for parameters
    """
    @property
    def _default_id(self):
        return "unnamed_parameter"

    @property
    def _default_name(self):
        return "unnamed parameter"

    @property
    def _default_interpolation(self):
        return "linear"

class StateVariable(InterfaceValue):
    """ Class for state variables
    """
    @property
    def _default_id(self):
        return "unnamed_state_variable"

    @property
    def _default_name(self):
        return "unnamed state variable"

    @property
    def _default_interpolation(self):
        return "zero" # TODO not better "nearest"?


###############################
### Sets of InterfaceValues ###
###############################
class SetOfInterfaceValues(utils.SetOfObjects):
    """ Base class for sets of interface values
    """
    def __init__(self, elements = []):
        """ class constructor
        Args:
            values (list of value_type-instances): the list of values
        """
        utils.SetOfObjects.__init__(self, # call SetOfObjects constructor
            elements = elements, 
            element_type = InterfaceValue # only InterfaceValue is allowed
            )

    @property
    def time_function(self):
        return [e.time_function for e in self.elements]

    @time_function.setter
    def time_function(self, newfunc):
        assert hasattr(newfunc, '__call__'), "time_function has to be callable"
        for e in self.elements: # set every element's time_function
            e.time_function = newfunc

    ###############
    ### Methods ###
    ###############
    def _object_to_key(self, obj):
        """ key transformation function. 
        Args:
            obj (object): the element
        Returns:
            key (str): the unique key for this object. The InterfaceValue's id
                is used.
        """
        return obj.id
        
    def __call__(self,id):
        """ When called, return the InterfaceValue's VALUE
        """
        return self[id].value


class SetOfParameters(SetOfInterfaceValues):
    """ Class for a set of parameters
    """
    def __init__(self,elements = []):
        utils.SetOfObjects.__init__( self,
            elements = elements,  # these parameters
            element_type = Parameter, # only parameter belong here
            )

class SetOfForcingValues(SetOfInterfaceValues):
    """ Class for a set of forcing values
    """
    def __init__(self,elements = []):
        utils.SetOfObjects.__init__( self,
            elements = elements,  # these values
            element_type = ForcingValue, # only forcingvalues belong here
            )
        
class SetOfStateVariables(SetOfInterfaceValues):
    """ Class for a set of state variables
    """
    def __init__(self,elements = []):
        utils.SetOfObjects.__init__( self,
            elements = elements,  # these variables
            element_type = StateVariable, # only statevariables belong here
            )
