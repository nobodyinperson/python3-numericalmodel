#!/usr/bin/env python3
# system modules
import textwrap
import collections

# internal modules
from . import equations
from . import utils

# external modules
import numpy as np


class NumericalScheme(utils.ReprObject,utils.LoggerObject):
    """ 
    Base class for numerical schemes

    Args:
        description (str): short equation description
        long_description (str): long equation description
        equation (DerivativeEquation): the equation
        fallback_max_timestep (single numeric): the fallback maximum
            timestep if no timestep can be estimated from the equation
        ignore_linear (bool): ignore the linear part of the equation?
        ignore_independent (bool): ignore the variable-independent part of
            the equation?  
        ignore_nonlinear (bool): ignore the nonlinear part of the equation?
    """
    def __init__(self, description = None, long_description = None,
        equation = None, fallback_max_timestep = None, 
        ignore_linear = None, ignore_independent = None, 
        ignore_nonlinear = None):
        if not equation is None: 
            self.equation = equation
        if not fallback_max_timestep is None: 
            self.fallback_max_timestep = fallback_max_timestep
        if not description is None: 
            self.description = description
        if not long_description is None: 
            self.long_description = long_description
        if not ignore_linear is None: 
            self.ignore_linear = ignore_linear
        if not ignore_independent is None: 
            self.ignore_independent = ignore_independent
        if not ignore_nonlinear is None: 
            self.ignore_nonlinear = ignore_nonlinear

    ##################
    ### Properties ###
    ##################
    @property
    def description(self):
        """ 
        The numerical scheme description

        :type: :any:`str`
        """
        try:                   self._description
        except AttributeError: self._description = self._default_description
        return self._description

    @description.setter
    def description(self, newdescription):
        assert isinstance(newdescription, str), "description has to be str"
        self._description = newdescription
        
    @property
    def _default_description(self):
        """ 
        The default description if none was given

        :type: :any:`str`
        """
        return "a numerical scheme"

    @property
    def long_description(self):
        """ 
        The longer numerical scheme description

        :type: :any:`str`
        """
        try:                   self._long_description
        except AttributeError: 
            self._long_description = self._default_long_description
        return self._long_description

    @long_description.setter
    def long_description(self, newlong_description):
        assert isinstance(newlong_description, str), \
            "long_description has to be str"
        self._long_description = newlong_description
        
    @property
    def _default_long_description(self):
        """ 
        The default longer numerical scheme description if none was given

        :type: :any:`str`
        """
        return "This is a numerical scheme to solve a derivative equation."

    @property
    def fallback_max_timestep(self):
        """ 
        The numerical scheme's fallback maximum timestep 

        :type: :any:`float`
        """
        try:                   self._fallback_max_timestep
        except AttributeError: 
            self._fallback_max_timestep = self._default_fallback_max_timestep
        return self._fallback_max_timestep

    @fallback_max_timestep.setter
    def fallback_max_timestep(self, newfallback_max_timestep):
        assert utils.is_numeric(newfallback_max_timestep), \
            "fallback_max_timestep has to be numeric"
        assert np.asarray(newfallback_max_timestep).size == 1, \
            "fallback_max_timestep has to be of size 1"
        self._fallback_max_timestep = float(newfallback_max_timestep)

    @property
    def _default_fallback_max_timestep(self):
        """ 
        The numerical scheme's default fallback maximum timestep 

        :type: :any:`float`
        """
        return 1.0

    @property
    def equation(self):
        """ 
        The equation the numerical scheme's should solve

        :type: :any:`DerivativeEquation`
        """
        try:                   self._equation
        except AttributeError: self._equation = self._default_equation
        return self._equation

    @equation.setter
    def equation(self, newequation):
        assert isinstance(newequation, equations.DerivativeEquation), \
            "equation has to be instance of subclass of DerivativeEquation"
        self._equation = newequation
        
    @property
    def _default_equation(self):
        """ 
        The default equation the numerical scheme's should solve if none was
        given

        :type: :any:`DerivativeEquation`
        """
        return equations.DerivativeEquation()

    @property
    def ignore_linear(self):
        """ 
        Should this numerical scheme ignore the equation's linear factor?

        :type: :any:`bool`
        """
        try:                   self._ignore_linear
        except AttributeError: self._ignore_linear = self._default_ignore_linear
        return self._ignore_linear

    @ignore_linear.setter
    def ignore_linear(self, newignore_linear):
        self._ignore_linear = bool(newignore_linear)
        
    @property
    def _default_ignore_linear(self):
        """ 
        Default behaviour for :any:`ignore_linear`

        :type: :any:`bool`
        """
        return False

    @property
    def ignore_independent(self):
        """ 
        Should this numerical scheme ignore the equation's variable-independent
        addend?

        :type: :any:`bool`
        """
        try:                   self._ignore_independent
        except AttributeError: 
            self._ignore_independent = self._default_ignore_independent
        return self._ignore_independent

    @ignore_independent.setter
    def ignore_independent(self, newignore_independent):
        self._ignore_independent = bool(newignore_independent)
        
    @property
    def _default_ignore_independent(self):
        """ 
        Default behaviour for :any:`ignore_independent`

        :type: :any:`bool`
        """
        return False

    @property
    def ignore_nonlinear(self):
        """ 
        Should this numerical scheme ignore the equation's nonlinear addend?

        :type: :any:`bool`
        """
        try:                   self._ignore_nonlinear
        except AttributeError: 
            self._ignore_nonlinear = self._default_ignore_nonlinear
        return self._ignore_nonlinear

    @ignore_nonlinear.setter
    def ignore_nonlinear(self, newignore_nonlinear):
        self._ignore_nonlinear = bool(newignore_nonlinear)
        
    @property
    def _default_ignore_nonlinear(self):
        """ 
        Default behaviour for :any:`ignore_nonlinear`

        :type: :any:`bool`
        """
        return False

    ###############
    ### Methods ###
    ###############
    @property
    def max_timestep(self, time = None, variablevalue = None):
        """ 
        Return a maximum timestep for the current state. First tries the
        :any:`max_timestep_estimate`, then the :any:`fallback_max_timestep`.

        Args:
            time (single numeric, optional): the time to calculate the 
                derivative. Defaults to the variable's current (last) time.
            variablevalue (numpy.ndarray, optional): the variable vaulue to use. 
                Defaults to the value of self.variable at the given time.

        Returns:
            float : an estimate of the current maximum timestep
        """
        try:
            try: # try an estimate
                ts = self.max_timestep_estimate(
                    time=time, variablevalue=variablevalue) # try estimate
            except: # estimating didn't work
                ts = self.fallback_max_timestep # try fallback
            assert utils.is_numeric(ts)
            assert np.asarray(ts).size == 1
        except: # neither estimate nor fallback were sensible
            ts = 1 # default
            raise
        return ts


    def max_timestep_estimate(self, time = None, variablevalue = None):
        """ 
        Based on this numerical scheme and the equation parts, estimate a
        maximum timestep. Subclasses may override this.

        Args:
            time (single numeric, optional): the time to calculate the 
                derivative. Defaults to the variable's current (last) time.
            variablevalue (numpy.ndarray, optional): the variable vaulue to use. 
                Defaults to the value of self.variable at the given time.

        Returns:
            single numeric or bogus: an estimate of the current
            maximum timestep. Definitely check the result for integrity.

        Raises:
            Exception : any exception if something goes wrong
        """
        # equation + state -> timestep estimate functions
        def smaller_than_time_constant(time = None, variablevalue = None):
            eq = self.equation
            nonlin = eq.nonlinear_addend(time=time,variablevalue=variablevalue)
            assert nonlin == 0, "not a linear equation"
            lin = eq.linear_factor(time = time)
            assert lin < 0, "not a decay equation"
            tau = abs(1 / lin) # time constant
            return 0.01 * tau # timestep must be smaller than time constant
        # fallback function
        def nothing(*args,**kwargs):
            raise Exception

        # mapping of schemes to functions
        schemes = { 
            EulerExplicit: smaller_than_time_constant,
            EulerImplicit: smaller_than_time_constant,
            RungeKutta4:   smaller_than_time_constant, # TODO correct?
            }

        fun = schemes.get(self.__class__, nothing ) # get the function
        timestep = fun(time = time, variablevalue = variablevalue) # call it
        return timestep # return

    def needed_timesteps(self, timestep):
        """ 
        Given a timestep to integrate from now on, what other timesteps of the
        dependencies are needed?

        Args:
            timestep (single numeric): the timestep to calculate 

        Returns:
            numpy.ndarray : the timesteps

        Note:
            timestep 0 means the current time
        """
        assert utils.is_numeric(timestep), "timestep needs to be numeric"
        ts = np.asarray(timestep)
        assert ts.size == 1, "timestep needs to be one single value"
        return self._needed_timesteps_for_integration_step(timestep = ts)

    def _needed_timesteps_for_integration_step(self, timestep = None):
        """ 
        Given a timestep to integrate from now on, what other timesteps of the
        dependencies are needed?

        Args:
            timestep (single numeric): the timestep to calculate 

        Returns:
            numpy.ndarray : the timesteps

        Note:
            timestep 0 means the current time
        """
        raise NotImplementedError("Subclasses should override this")

    def linear_factor(self, time = None):
        """ 
        Calculate the equation's linear factor in front of the variable.

        Args:
            time (single numeric, optional): the time to calculate the 
                derivative. Defaults to the variable's current (last) time.

        Returns:
            numeric : the linear factor or 0 if :any:`ignore_linear` is
            ``True``.  
        """
        if self.ignore_linear:
            return 0
        else:
            return self.equation.linear_factor( time = time )

    def independent_addend(self, time = None):
        """ 
        Calculate the equation's addend part that is independent of the
        variable.
        
        Args:
            time (single numeric, optional): the time to calculate the 
                derivative. Defaults to the variable's current (last) time.

        Returns:
            numeric : the independent addend or 0 if :any:`ignore_independent`
            is ``True``.  
        """
        if self.ignore_independent:
            return 0
        else:
            return self.equation.independent_addend( time = time )

    def nonlinear_addend(self, time = None, variablevalue = None):
        """ 
        Calculate the derivative's addend part that is nonlinearly dependent of
        the variable.

        Args:
            time (single numeric, optional): the time to calculate the 
                derivative. Defaults to the variable's current (last) time.
            variablevalue (numpy.ndarray, optional): the variable vaulue to use. 
                Defaults to the value of self.variable at the given time.

        Returns:
            res (numeric): the nonlinear addend or 0 if ignore_nonlinear is 
            True.
        """
        if self.ignore_nonlinear:
            return 0
        else:
            return self.equation.nonlinear_addend( 
                time = time, variablevalue = variablevalue) 

    def integrate(self, time = None, until = None):
        """ Integrate until a certain time, respecting the :any:`max_timestep`.

        Args:
            time (single numeric, optional): The time to begin. Defaults to
                current variable :any:`time`.
            until (single numeric, optional): The time to integrate until.
                Defaults to one :any:`max_timestep` further.
        """
        assert utils.is_numeric(until), "until needs to be numeric"
        if time is None: time = self.equation.variable.time
        current_max_timestep = self.max_timestep
        self.logger.debug("current maximum timestep is {}".format(
            current_max_timestep))
        if until is None: until = time + current_max_timestep
        self.logger.debug("integrating until time {}".format(until))
        time_now = time
        while time_now < until:
            self.logger.debug(("current time {} is smaller than until time {}"
                ).format(time_now,until))
            time_left = until - time_now
            if time_left > current_max_timestep: # full max_timestep fits
                timestep = current_max_timestep
            else:
                timestep = time_left
            self.logger.debug(("integrate one step from time {} with " 
                "timestep {}").format(time_now,timestep))
            # integrate one step
            self.integrate_step( time = time_now, timestep = timestep )
            time_now += timestep
        self.logger.debug(("reached until time {}").format(time_now))
            

    def integrate_step(self, time = None, timestep = None):
        """ 
        Integrate "timestep" forward and set results in-place

        Args:
            time (single numeric, optional): The time to calculate the step
                FROM. Defaults to the current variable time.
            timestep (single numeric, optional): The timestep to calculate the
                step. Defaults to :any:`max_timestep`.
        """
        var = self.equation.variable
        if timestep is None: timestep = self.max_timestep
        if time is None: time = var.time
        var.next_time = time + timestep # this is the next time
        tend = self.step( # integrate one timestep
            time = time, timestep = timestep, tendency = True )
        # self.logger.debug("{} tendency: {}".format(var.id,tend))
        # self.logger.debug("var() = {}".format(var()))
        # self.logger.debug("var({}) = {}".format(time,var(time)))
        # self.logger.debug("var.time = {}".format(var.time))
        # self.logger.debug("var(var.time) = {}".format(var(var.time)))
        new = var(time) + tend
        var.value = new # save value
        var.next_time = None # unset next_time

    def step(self, time, timestep, tendency=True):
        """ 
        Integrate one "timestep" from "time" forward and return value
        
        Args:
            time (single numeric): The time to calculate the step FROM
            timestep (single numeric): The timestep to calculate the step
            tendency (bool, optional): return the tendency or the actual value
                of the variable after the timestep?

        Returns:
            numpy.ndarray : The resulting variable value or tendency
        """
        raise NotImplementedError("Subclasses should override this")

    def __str__(self): # pragma: no cover
        """ 
        Stringification

        Returns:
            str : a summary
        """
        string = (
        " \"{description}\" \n"
        "{long_description}\n"
        "maximum timestep: {max_timestep} \n"
        "[numerical scheme for equation:] \n"
        "{equation}\n"
        ).format(description=self.description, 
            equation = textwrap.indent(text=str(self.equation),prefix="> "),
            max_timestep = self.max_timestep,
            variable=self.equation.variable.id,
            long_description = self.long_description)
        return string


class EulerExplicit(NumericalScheme):
    """ 
    Euler-explicit numerical scheme
    """
    @property
    def _default_description(self):
        return "Euler-explicit scheme"

    @property
    def _default_long_description(self):
        return "This is a Euler-explicit scheme to solve a derivative equation."

    def step(self, time = None, timestep = None, tendency = True):
        if timestep is None: timestep = self.max_timestep
        v = self.equation.variable
        # get equation parts
        linear = self.linear_factor( time = time )
        indep  = self.independent_addend( time = time )
        nonlin = self.nonlinear_addend( time = time )

        cur = v( time )
        # explicit scheme
        tend = timestep * ( linear * cur + indep + nonlin )

        if tendency: # only tendency desired
            res = tend
        else: # value desired
            res = cur + tend
        return res

    def _needed_timesteps_for_integration_step(self, timestep = None):
        return np.array([0]) # only current time needed



class EulerImplicit(NumericalScheme):
    """ 
    Euler-implicit numerical scheme
    """
    @property
    def _default_description(self):
        return "Euler-implicit scheme"

    @property
    def _default_long_description(self):
        return "This is a Euler-implicit scheme to solve a derivative equation."

    def step(self, time = None, timestep = None, tendency = True):
        """ 
        Integrate one "timestep" from "time" forward with the Euler-implicit
        scheme and return the resulting variable value.
        
        Args:
            time (single numeric): The time to calculate the step FROM
            timestep (single numeric): The timestep to calculate the step
            tendency (bool, optional): return the tendency or the actual value
                of the variable after the timestep?

        Returns:
            numpy.ndarray : The resulting variable value or tendency

        Raises:
            AssertionError : when the equation's nonlinear part is not zero and
                :any:`ignore_nonlinear` is not set to ``True``
        """
        if timestep is None: timestep = self.max_timestep
        v = self.equation.variable
        # get equation parts
        linear = self.linear_factor( time = time )
        indep  = self.independent_addend( time = time )
        nonlin = self.nonlinear_addend( time = time )

        assert np.all(nonlin == 0), ("nonlinear part of equation is not "
        "zero! Cannot integrate equation with implicit scheme. Set "
        "ignore_nonlinear to ignore nonlinear part.")

        # implicit scheme
        new = ( indep * timestep + v( time ) ) / ( 1 - linear * timestep )

        if tendency: # tendency desired
            res = new - v( time ) # only tendency
        else: # new value desired
            res = new
        
        return res

    def _needed_timesteps_for_integration_step(self, timestep):
        return np.array([0,1]) * timestep # current time and timestep needed


class LeapFrog(NumericalScheme):
    """ 
    Leap-Frog numerical scheme
    """
    @property
    def _default_description(self):
        return "Leap-Frog scheme"

    @property
    def _default_long_description(self):
        return "This is a Leap-Frog scheme to solve a derivative equation."

    def step(self, time = None, timestep = None, tendency = True):
        if timestep is None: timestep = self.max_timestep
        v = self.equation.variable
        if time is None: time = v.time
        # get equation parts
        linear = self.linear_factor( time = time )
        indep  = self.independent_addend( time = time )
        nonlin = self.nonlinear_addend( time = time )

        # previous value
        prev = v( time - timestep )
        cur = v( time )
        # leap-frog scheme
        new = prev + 2 * timestep * ( linear * cur + indep + nonlin )

        if tendency: # tendency desired
            res = new - cur # only tendency
        else: # new value desired
            res = new
        
        return res

    def _needed_timesteps_for_integration_step(self, timestep):
        return np.array([-1,0]) * timestep # prev time and current time needed


class RungeKutta4(NumericalScheme):
    """ 
    Runte-Kutta-4 numerical scheme
    """
    @property
    def _default_description(self):
        return "Runge-Kutta-4 scheme"

    @property
    def _default_long_description(self):
        return ("This is a Runge-Kutta-4th-order scheme to solve a " 
            "derivative equation.")

    def step(self, time = None, timestep = None, tendency = True):
        if timestep is None: timestep = self.max_timestep
        v = self.equation.variable
        if time is None: time = v.time
        # get equation parts
        linear = self.linear_factor( time = time )
        indep  = self.independent_addend( time = time )
        nonlin = self.nonlinear_addend( time = time )

        half_time = time + timestep / 2
        next_time = time + timestep
        cur = v( time )

        def F(): return linear * cur + indep + nonlin

        # first part
        k1 = timestep * F()

        # second part
        linear = self.linear_factor( time = half_time )
        indep  = self.independent_addend( time = half_time )
        nonlin = self.nonlinear_addend( 
            time = half_time, variablevalue = cur + k1 / 2 )
        k2 = timestep * F()
        nonlin = self.nonlinear_addend( 
            time = half_time, variablevalue = cur + k2 / 2 )
        k3 = timestep * F()
        linear = self.linear_factor( time = next_time )
        indep  = self.independent_addend( time = next_time )
        nonlin = self.nonlinear_addend( 
            time = next_time, variablevalue = cur + k3 )
        k4 = timestep * F()

        tend = ( k1 + 2 * k2 + 2 * k3 + k4 ) / 6

        if tendency: # tendency desired
            res = tend # only tendency
        else: # new value desired
            res = cur + tend # add tendency
        
        return res

    def _needed_timesteps_for_integration_step(self, timestep):
        return np.array([0,0.5,1]) * timestep # current time, half and full 


###############################
### Sets of NumericalScheme ###
###############################
class SetOfNumericalSchemes(utils.SetOfObjects):
    """ 
    Base class for sets of NumericalSchemes
    
    Args:
        elements (:any:`list` of :any:`NumericalScheme`, optional): the the
            numerical schemes 
        fallback_plan (list, optional): the fallback plan if automatic planning
            fails. Depending on the combination of numerical scheme and equations,
            a certain order or solving the equations is crucial. For some
            cases, the order can be determined automatically, but if that
            fails, one has to provide this information by hand.
            Has to be a :any:`list` of ``[varname, [timestep1,timestep2,...]]``
            pairs.

            varname: 
                the name of the equation variable. Obviously there has to be at
                least one entry in the list for each equation.

            timestepN: 
                the normed timesteps (betw. 0 and 1) to calculate.  Normed
                means, that if it is requested to integrate the set of numerical
                equations by an overall timestep, what percentages of this
                timestep have to be available of this variable. E.g. an overall
                timestep of 10 is requested. Another equation needs this
                variable at the timesteps 2 and 8. Then the timesteps would be
                [0.2,0.8].  Obviously, the equations that looks farest into the
                future (e.g.  Runge-Kutta or Euler-Implicit) has to be last in
                this fallback_plan list.
    """
    def __init__(self, elements = [], fallback_plan = None):
        utils.SetOfObjects.__init__(self, # call SetOfObjects constructor
            elements = elements, 
            element_type = NumericalScheme, # only NumericalScheme is allowed
            )

        # set properties
        if fallback_plan is None:
            self.fallback_plan = self._default_fallback_plan
        else: self.fallback_plan = fallback_plan

    ##################
    ### Properties ###
    ##################
    @property
    def plan(self):
        """ 
        The unified plan for this set of numerical schemes. First try to
        determine the plan automatically, if that fails, use the
        :any:`fallback_plan`.
        
        :type: :any:`list`
        """
        try: # try automatic planning
            plan = self._automatic_plan
        except: # automatic planning didn't work
            plan = self.fallback_plan # use fallback
        return plan

    @property
    def fallback_plan(self):
        """ 
        The fallback plan if automatic plan determination does not work

        :type: :any:`list`
        """
        try: self._fallback_plan
        except AttributeError: self._fallback_plan = self._default_fallback_plan
        return self._fallback_plan

    @fallback_plan.setter
    def fallback_plan(self, newfallback_plan):
        try:
            variables = { p[0] for p in newfallback_plan }
            assert all( v in variables for v in self.keys() ), \
                "not all equations present in plan"
            timesteps = [ np.asarray(p[1]) for p in newfallback_plan ]
            assert all( np.all( np.logical_and(0<=ts,ts<=1) ) \
                for ts in timesteps), \
                "timesteps outside (0,1) requested in plan"
        except:
            raise ValueError("wrong scheme plan format")
        self._fallback_plan = newfallback_plan

    @property
    def _default_fallback_plan(self):
        """ 
        The default fallback plan if none was given
        """
        # stupidest plan: solve equations in alphabetical order
        plan = [ [var,[1]] for var in sorted(self.keys()) ]
        return plan

    @property
    def _automatic_plan(self):  
        """ 
        Try to determine the scheme plan based on the equations and the
        numerical schemes.

        :type: :any:`list`

        .. todo::
            Implementing this is definitely possible. All needed information is
            accessible:

                - the equation's dependencies
                - the numerical scheme's needed timesteps
        """
        # TODO: This definitely has to be implemented for convenience
        raise NotImplementedError("Automatic planning is definitely possible, " 
            "but not yet implemented")

    ###############
    ### Methods ###
    ###############
    def _object_to_key(self, obj):
        """ key transformation function. 

        Args:
            obj (object): the element

        Returns:
            key (str): the unique key for this object. The equation's variable's
            id is used.
        """
        return obj.equation.variable.id

    def integrate(self, start_time, final_time):
        """ Integrate the model until final_time

        Args:
            start_time (float): the starting time
            final_time (float): time to integrate until
        """
        self.logger.info("start integration")
        current_time = start_time
        while current_time < final_time:
            self.logger.debug("current time {} is smaller than " 
                "final time {}".format(current_time, final_time))
            # timestep of most dependent equation
            biggest_timestep = self[self.plan[-1][0]].max_timestep
            self.logger.debug("timestep of last scheme: {}".format(
                biggest_timestep))
            run_time_left = final_time - current_time
            if run_time_left > biggest_timestep:
                big_timestep = biggest_timestep
            else:
                big_timestep = run_time_left

            for plan_step in self.plan:
                scheme_time = current_time
                varname = plan_step[0] # variable name
                scheme = self[varname] # get scheme
                timesteps = np.asarray( plan_step[1] ) * big_timestep 
                # self.logger.debug("timesteps: {}".format(timesteps))
                for ts in timesteps: # loop over all timesteps
                    until_time = current_time + ts
                    self.logger.debug(
                        ("integrate scheme '{}' for equation '{}' until time {}"
                        ).format( scheme.description,
                        scheme.equation.description, until_time))
                    scheme.integrate(
                        time = scheme_time,
                        until = until_time)
                    scheme_time = current_time + ts
                
            current_time = current_time + big_timestep
        self.logger.info("end of integration")

