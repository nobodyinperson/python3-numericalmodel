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
        name = "unnamed interface value",
        id = "unnamed_value",
        value = 0
        ):
        """ Class constructor
        Args:
            name (str): value name
            id (str): unique id
            value (numeric): numeric value. Will be converted to np.array
        """
        # set properties
        self.name = name
        self.id = id
        self.value = value

    ##################
    ### Properties ###
    ##################
    @property
    def id(self):
        try:                   self._id # already defined?
        except AttributeError: self._id = "unnamed_variable" # default
        return self._id # return

    @id.setter
    def id(self,newid):
        assert isinstance(newid,str), "id has to be str"
        self._id = newid 

    @property
    def name(self):
        try:                   self._name # already defined?
        except AttributeError: self._name = "unnamed interface value" # default
        return self._name # return

    @name.setter
    def name(self,newname):
        assert isinstance(newname,str), "name has to be str"
        self._name = newname 

    @property
    def value(self):
        try:                   self._value # already defined?
        except AttributeError: self._value = 0 # default
        return self._value # return

    @value.setter
    def value(self,newvalue):
        assert utils.is_numeric(newvalue), "value has to be numeric"
        self._value = np.asarray(newvalue) # convert to numpy array


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
        return list(self.store.values())

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


class ForcingValue(InterfaceValue):
    """ Class for forcing values
    """
    pass

class Parameter(InterfaceValue):
    """ Class for parameters
    """
    pass

class StateVariable(InterfaceValue):
    """ Class for state variables
    """
    pass


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
