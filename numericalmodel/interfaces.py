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
    """ 
    Base class for model interface values

    Args:
        name (str, optional): value name
        id (str, optional): unique id
        values (1d :any:`numpy.ndarray`, optional): all values this
            InterfaceValue had in chronological order
        times (1d :any:`numpy.ndarray`, optional): the corresponding times to
            values 
        unit (str,optional): physical unit of value
        bounds (list, optional): lower and upper value bounds
        interpolation (str, optional): interpolation kind. See
            :any:`scipy.interpolate.interp1d` for documentation. Defaults to 
            "zero".
        time_function (callable, optional): function that returns the model time
            as utc unix timestamp
        remembrance (float, optional): maximum :any:`time` difference to keep
            past :any:`values`
    """
    def __init__(self,
        name = None,
        id = None,
        unit = None,
        time_function = None,
        interpolation = None,
        values = None,
        times = None,
        bounds = None,
        remembrance = None,
        ):
        # set properties
        if not time_function is None:  
            self.time_function = time_function
        if not name is None:  
            self.name = name
        if not unit is None:  
            self.unit = unit
        if not id is None:    
            self.id = id
        if not bounds is None: 
            self.bounds = bounds
        if not values is None:
            self.values = values
        if not times is None: 
            self.times = times
        if not interpolation is None: 
            self.interpolation = interpolation
        if not remembrance is None: 
            self.remembrance = remembrance

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
        """ 
        The unique id

        :type: :any:`str`
        """
        try:                   self._id # already defined?
        except AttributeError: self._id = self._default_id # default
        return self._id # return

    @id.setter
    def id(self,newid):
        assert isinstance(newid,str), "id has to be str"
        self._id = newid 

    @property
    def _default_id(self):
        """ 
        Default id if none was given. Subclasses should override this.

        :type: :any:`str`
        """
        return "unnamed_variable"

    @property
    def unit(self):
        """ 
        The SI-unit. 

        :type: :any:`str`, SI-unit
        """
        try:                   self._unit # already defined?
        except AttributeError: self._unit = self._default_unit # default
        return self._unit # return

    @unit.setter
    def unit(self,newunit):
        assert isinstance(newunit,str), "unit has to be str"
        self._unit = newunit 

    @property
    def _default_unit(self):
        """ 
        The default unit if none was given.

        :type: :any:`str`, SI-unit
        """
        return "1"

    @property
    def name(self):
        """ 
        The name.

        :type: :any:`str`
        """
        try:                   self._name # already defined?
        except AttributeError: self._name = self._default_name # default
        return self._name # return

    @name.setter
    def name(self,newname):
        assert isinstance(newname,str), "name has to be str"
        self._name = newname 

    @property
    def _default_name(self):
        """ 
        Default name if none was given.

        :type: :any:`str`
        """
        return "unnamed value"

    @property
    def value(self):
        """ 
        The current value.

        :getter: 
            the return value of :any:`__call__`, i.e.  the current value.
        :setter: 
            When this property is set, the given value is recorded to the
            time given by :any:`next_time`. If this time exists already in
            :any:`times`, the corresponding value in :any:`values` is
            overwritten.  Otherwise, the new time and value are appended to
            :any:`times` and :any:`values`.
            The value is also checked to lie within the :any:`bounds`.
        :type: numeric
        """
        return self() # call us

    @value.setter
    def value(self,newvalue):
        assert utils.is_numeric(newvalue), "value has to be numeric"
        val = np.asarray(newvalue) # convert to numpy array
        assert val.size == 1, "value has to be of size one"
        # check if values are inside bounds
        lower, upper = self.bounds
        assert np.all(newvalue >= lower), \
            ("{}: new value is smaller than lower bound {}").format(
                self.name,lower)
        assert np.all(newvalue <= upper), \
            ("{}: new value is greater than upper bound {}").format(
                self.name,upper)
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
        # for get old values
        self.forget_old_values()

    @property
    def values(self):
        """ 
        All values this InterfaceValue has ever had in chronological order

        :getter: Return the current values
        :setter: Check if all new values lie within the :any:`bounds`
        :type: :any:`numpy.ndarray`
        """
        try:                   self._values # already defined?
        except AttributeError: self._values = self._default_times # default
        return self._values # return

    @values.setter
    def values(self,newvalues):
        assert isinstance(newvalues,np.ndarray), \
            "values have to be numpy.ndarray"
        assert newvalues.size == np.prod(newvalues.shape), \
            "values have to be one-dimensional" 
        # check if values are inside bounds
        lower, upper = self.bounds
        assert np.all(newvalues >= lower), \
            ("{}: new value is smaller than lower bound {}").format(
                self.name,lower)
        assert np.all(newvalues <= upper), \
            ("{}: new value is greater than upper bound {}").format(
                self.name,upper)
        self._values = newvalues
        # reset intepolator
        self.interpolator = None

    @property
    def _default_values(self):
        return np.array([]) # empty array

    @property
    def next_time(self):
        """ 
        The next time to use when :any:`value` is set. 
        
        :getter: 
            Return the next time to use. Defaults to the value of
            :any:`time_function` if no :any:`next_time` was set.
        :setter:
            Set the next time to use. Set to :any:`None` to unset and use the
            default time in the getter again.
        :type: :any:`float`
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
            if hasattr(self, "_next_time"): del self._next_time # del attribute
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
        """ 
        The current time

        :getter:
            Return the current time, i.e. the last time recorded in
            :any:`times`.
        :type: :any:`float`
        """
        return self.times[-1]

    @property
    def times(self):
        """ 
        All times the :any:`value` has ever been set in chronological
        order 

        :type: :any:`numpy.ndarray`
        """
        try:                   self._times # already defined?
        except AttributeError: self._times = self._default_times # default
        return self._times # return

    @times.setter
    def times(self,newtimes):
        assert isinstance(newtimes,np.ndarray), "times have to be numpy.ndarray"
        assert newtimes.size == np.prod(newtimes.shape), \
            "times have to be one-dimensional" 
        assert np.all(np.diff(newtimes)>0), "times must be strictly increasing"
        self._times = newtimes
        # reset intepolator
        self.interpolator = None

    @property
    def _default_times(self):
        """ 
        The default times to use when none were given. Defaults to empty
        :any:`numpy.ndarray`.

        :type: :any:`numpy.ndarray`
        """
        return np.array([]) # empty array

    @property
    def bounds(self):
        """ 
        The :any:`values`' bounds. Defaults to an infinite interval.

        :getter: Return the current bounds
        :setter: If the bounds change, check if all :any:`values` lie within the
            new bounds.
        :type: :any:`list`, ``[lower, upper]``
        """
        try:                   self._bounds # already defined?
        except AttributeError: self._bounds = self._default_bounds # default
        return self._bounds # return

    @bounds.setter
    def bounds(self,newbounds):
        assert isinstance(newbounds,list), "bounds have to be list"
        assert len(newbounds) == 2, "bounds must have two elements" 
        assert all(utils.is_numeric(x) for x in newbounds), \
            "bounds have to be list like [lower, upper]"
        assert newbounds[1] > newbounds[0], \
            "new lower bound has to be smaller than upper bound"
        if self.bounds != newbounds: # bounds changed
            # check the values for the new bounds
            assert np.all( self.values >= newbounds[0] ), \
                "there are values greater than the new upper bound"
            assert np.all( self.values <= newbounds[1] ), \
                "there are values greater than the new upper bound"
        self._bounds = newbounds # set internal attribute

    @property
    def _default_bounds(self):
        """ 
        The default bounds to use when none were given.

        :type: :any:`list`
        """
        return [-np.Inf, np.Inf] # unlimited

    @property
    def remembrance(self):
        """ 
        How long should this :any:`InterfaceValue` store it's :any:`values`?
        This is the greatest difference the current :any:`time` may have to the
        smallest :any:`time`. Values earlier than the :any:`remembrance` time
        are discarded. Set to :any:`None` for no limit.

        :type: :any:`float` or :any:`None`
        """
        try:                   self._remembrance # already defined?
        except AttributeError: self._remembrance = self._default_remembrance
        return self._remembrance # return

    @remembrance.setter
    def remembrance(self, newremembrance):
        if newremembrance is None:
            self._remembrance = newremembrance
        else:
            remembrance = float(newremembrance)
            assert remembrance >= 0, "remembrance has to be positive float"
            self._remembrance = remembrance

    @property
    def _default_remembrance(self):
        """ 
        Default :any:`remembrance` if none was given.

        :type: :any:`float64`
        """
        return None

    @property
    def interpolation(self):
        """ 
        The interpolation kind to use in the :any:`__call__` method. See
        :any:`scipy.interpolate.interp1d` for documentation.

        :getter:
            Return the interplation kind.
        :setter:
            Set the interpolation kind. Reset the internal interpolator if the
            interpolation kind changed.

        :type: :any:`str`
        """
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
        """ 
        Default interpolation if none was given is ``"zero"``, i.e.
        left-neighbour interpolation. Subclasses may override this.

        :type: :any:`str`
        """
        return "zero"

    @property
    def interpolator(self):
        """ 
        The interpolator for interpolation of :any:`values` over :any:`times`.
        Creating this interpolator is costly and thus only performed on demand,
        i.e. when :any:`__call__` is called **and** no interpolator was created
        previously or the previously created interolator was unset before (e.g.
        by setting a new :any:`value` or changing :any:`interpolation`)

        :type: :any:`scipy.interpolate.interp1d`
        """
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

    ###############
    ### Methods ###
    ###############
    def forget_old_values(self):
        """ 
        Drop :any:`values` and :any:`times` older than :any:`remembrance`.

        Returns:
            bool : :any:`True` is data was dropped, :any:`False` otherwise
        """
        res = False
        if not self.remembrance is None: # remembrance was set
            assert self.times.size == self.values.size,\
                "times and values are of different size!"
            up_to_date = self.times >= ( self.time - self.remembrance )
            self._times  = self.times[up_to_date]
            self._values = self.values[up_to_date]
            res = True
        return res

    def __call__(self, times = None):
        """ 
        When called, return the value, optionally at a specific time

        Args:
            times (numeric, optional): The times to obtain data from
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

    def __str__(self): # pragma: no cover
        """ 
        Stringification

        Returns:
            str : a summary
        """
        if self.values.size: value = self.value
        else:                value = "?"
        string = (
        " \"{name}\" \n"
        "--- {id} [{unit}] ---\n"
        "currently: {value} [{unit}]\n"
	"bounds: {bounds}\n"
        "interpolation: {interp} \n"
        "{nr} total recorded values"
        ).format(id=self.id,unit=self.unit,interp=self.interpolation,
        name=self.name,value=value,nr=self.values.size,bounds=self.bounds)
        return string
        
####################################
### Subclasses of InterfaceValue ###
####################################
class ForcingValue(InterfaceValue):
    """ 
    Class for forcing values
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
    """ 
    Class for parameters
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
    """ 
    Class for state variables
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
    """ 
    Base class for sets of interface values

    Args:
        values (:any:`list` of :any:`InterfaceValue`, optional): the list of
            values 
    """
    def __init__(self, elements = []):
        utils.SetOfObjects.__init__(self, # call SetOfObjects constructor
            elements = elements, 
            element_type = InterfaceValue # only InterfaceValue is allowed
            )

    @property
    def time_function(self):
        """ 
        The time function of all the :any:`InterfaceValue` s in the set.

        :getter:
            Return a :any:`list` of time functions from the elements
        :setter:
            Set the time function of each element
        :type: (:any:`list` of) callables
        """
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
            key (str): the unique key for this object. The
            :any:`InterfaceValue.id` is used.
        """
        return obj.id
        
    def __call__(self,id):
        """ 
        Get the value of an :any:`InterfaceValue` in this set

        Args:
            id (str): the id of an :any:`InterfaceValue` in this set

        Returns:
            float : the :any:`value` of the corresponding :any:`InterfaceValue`
        """
        return self[id].value


class SetOfParameters(SetOfInterfaceValues):
    """ 
    Class for a set of parameters
    """
    def __init__(self,elements = []):
        utils.SetOfObjects.__init__( self,
            elements = elements,  # these parameters
            element_type = Parameter, # only parameter belong here
            )

class SetOfForcingValues(SetOfInterfaceValues):
    """ 
    Class for a set of forcing values
    """
    def __init__(self,elements = []):
        utils.SetOfObjects.__init__( self,
            elements = elements,  # these values
            element_type = ForcingValue, # only forcingvalues belong here
            )
        
class SetOfStateVariables(SetOfInterfaceValues):
    """ 
    Class for a set of state variables
    """
    def __init__(self,elements = []):
        utils.SetOfObjects.__init__( self,
            elements = elements,  # these variables
            element_type = StateVariable, # only statevariables belong here
            )
