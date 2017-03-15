#!/usr/bin/env python3
# system modules
import logging
import collections
import inspect

# internal modules
from . import utils

# external modules
import numpy as np

class InterfaceValue(utils.LoggerObject,utils.ReprObject):
    """ Base class for model interface values
    """
    def __init__(self,
        name = None,
        id = None,
        unit = None,
        time_function = None,
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
        self.times = np.append(self.times, self.time_function())
        self.values = np.append(self.values, val)

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

    @property
    def _default_values(self):
        return np.array([]) # empty array

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
        self._times = newtimes

    @property
    def _default_times(self):
        return np.array([]) # empty array

    def __call__(self, times = None):
        """ When called, return the value, optionally at a specific time
        Args:
            times [Optional(numeric)]: The times to obtain data from
        """
        assert self.times.size, "no values recorded yet"
        if times is None: # no time given
            times = self.time_function() # use current time
        assert utils.is_numeric(times), "times have to be numeric"
        times = np.asarray(times) # convert to numpy array

        res = np.array([]) # start with empty resulting array

        for t in times.flatten(): # inefficient loop over array, I know...
            diff = t - self.times # difference
            # self.logger.debug("given times {} minus recorded times" 
            #     " {}: {}".format(t,self.times,diff))
            diff = np.ma.masked_less(diff, 0) # drop negative differences
            # self.logger.debug("negative differences dropped: {}".format(diff))
            assert not diff.mask.all(), ("time '{t}' is too early. " 
                "Earliest time is '{early}'").format(t=t,early=self.times.min())
            indices = np.ma.where(diff == diff.min()) # indices of "left" time
            # self.logger.debug("indices of left-time: {}".format(indices))
            val = self.values[indices] # get the corresponding value
            # self.logger.debug("corresponding value: {}".format(val))
            res = np.append(res, val) # append to resulting array
            # self.logger.debug("appended res: {}".format(res))
        
        return res.reshape(times.shape) # reshape back

    def __str__(self):
        """ Stringification: summary
        """
        if self.values.size: value = self.value
        else:                value = "?"
        string = (
        " \"{name}\" \n"
        "--- {id} [{unit}] ---\n"
        "currently: {value} [{unit}]\n"
        "{nr} total recorded values"
        ).format(id=self.id,unit=self.unit,
        name=self.name,value=value,nr=self.values.size)
        return string
        


class SetOfInterfaceValues(collections.MutableMapping,utils.ReprObject):
    """ Base class for sets of interface values
    """
    def __init__(self, elements = [], value_type = InterfaceValue):
        self.store = dict() # empty dict

        # set properties
        self.value_type = value_type
        self.elements = elements

    ##################
    ### Properties ###
    ##################
    @property
    def elements(self):
        """ return the list of values
        """
        return [self.store[x] for x in sorted(self.store)]

    @elements.setter
    def elements(self, newelements):
        """ Set new values via a list
        """
        assert isinstance(newelements, collections.Iterable), (
            "elements have to be list")
        # re-set the dict and fill it with new data
        tmp = dict() # temporary empty dict
        for i in range(len(newelements)):
            elem = newelements[i]
            assert issubclass(elem.__class__, self.value_type), \
                ("new element nr. {i} is no object of subclass " 
                 "of {vtype} but of class {cls}").format(
                i=i,vtype=self.value_type,cls=elem.__class__)
            assert not elem.id in tmp.keys(), \
                "id '{}' present multiple times".format(elem.id)
            tmp.update({elem.id:elem}) # add to temporary dict

        self.store = tmp.copy() # set internal dict

    @property
    def value_type(self):
        try:                   self._value_type
        except AttributeError: self._value_type = InterfaceValue # default
        return self._value_type

    @value_type.setter
    def value_type(self, newtype):
        assert inspect.isclass(newtype), \
            "value_type has to be a class"
        assert issubclass(newtype, InterfaceValue), \
            "value_type has to be subclass of InterfaceValue"
        self._value_type = newtype

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
    def add_element(self, newelement):
        tmp = self.elements.copy()
        tmp.append(newelement)
        self.elements = tmp

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        assert issubclass(value.__class__, self.value_type), (
            "new value has to be of type {}").format(self.value_type)
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __str__(self):
        """ Stringification: summary
        """
        string = "\n\n".join(str(x) for x in self.elements)
        if string:
            return string
        else:
            return "none"

    def __call__(self,id):
        """ When called, return the InterfaceValue's VALUE
        """
        return self[id].value


class ForcingValue(InterfaceValue):
    """ Class for forcing values
    """
    @property
    def _default_id(self):
        return "unnamed_forcing_value"

    @property
    def _default_name(self):
        return "unnamed forcing value"

class Parameter(InterfaceValue):
    """ Class for parameters
    """
    @property
    def _default_id(self):
        return "unnamed_parameter"

    @property
    def _default_name(self):
        return "unnamed parameter"

class StateVariable(InterfaceValue):
    """ Class for state variables
    """
    @property
    def _default_id(self):
        return "unnamed_state_variable"

    @property
    def _default_name(self):
        return "unnamed state variable"


class SetOfParameters(SetOfInterfaceValues):
    """ Class for a set of parameters
    """
    def __init__(self,parameters = []):
        SetOfInterfaceValues.__init__( self,
            value_type = Parameter, # only parameter belong here
            elements = parameters,  # these parameters
            )

    @property
    def parameters(self):
        return self.elements

    @parameters.setter
    def parameters(self, newparameters):
        self.elements = newparameters
        

class SetOfForcingValues(SetOfInterfaceValues):
    """ Class for a set of forcing values
    """
    def __init__(self,forcingvalues = []):
        SetOfInterfaceValues.__init__( self,
            value_type = ForcingValue, # only parameter belong here
            elements = forcingvalues,  # these forcingvalues
            )

    @property
    def forcingvalues(self):
        return self.elements

    @forcingvalues.setter
    def forcingvalues(self, newforcingvalues):
        self.elements = newforcingvalues
        
class SetOfStateVariables(SetOfInterfaceValues):
    """ Class for a set of state variables
    """
    def __init__(self,statevariables = []):
        SetOfInterfaceValues.__init__( self,
            value_type = StateVariable, # only parameter belong here
            elements = statevariables,  # these variables
            )

    @property
    def statevariables(self):
        return self.elements

    @statevariables.setter
    def statevariables(self, newstatevariables):
        self.elements = newstatevariables
