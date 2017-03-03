
import matplotlib.pyplot as plt
from numpy import arange, fromiter, array_equal
from logging import warn
import pickle

from fuzzy.functions import inv
from fuzzy.combinators import MAX, MIN, product, bounded_sum

class FuzzyWarning(UserWarning):
    pass


class Domain:
    """
    A domain is a 'measurable' dimension of 'real' values like temperature.

    There must be a lower and upper limit and a resolution (the size of steps)
    specified.

    Fuzzysets are defined within one such domain and are only meaningful
    while considered within their domain ('apples and bananas').
    To operate with sets across domains, there needs to be a mapping.

    The sets are accessed as attributes of the domain like
    >>> temp = Domain('temperature', 0, 100)
    >>> temp.hot = Set(lambda x: 0)
    >>> temp.hot(5)
    0

    DO NOT call a derived set without assignment first as it WILL
    confuse the recursion and seriously mess up.
    NOT: ~temp.hot(2) or ~(temp.hot.)(2) but:
    >>> not_hot = ~temp.hot
    >>> not_hot(2)
    1

    You MUST NOT add arbitrary attributes to an *instance* of Domain - you can
    however subclass or modify the class itself. If you REALLY have to add attributes, 
    make sure to "whitelist" it in _allowed_attrs first. 

    Use the Domain by calling it with the value in question. This returns a
    dictionary with the degrees of membership per set. You MAY override __call__
    in a subclass to enable concurrent evaluation for performance improvement.
    >>> temp.cold = not_hot
    
    # >>> temp(3) == {'temperature.hot': 0, 'temperature.cold': 1}
    # True
    """
    _allowed_attrs = ['name', 'low', 'high', 'res', '_sets']

    def __init__(self, name, low, high, res=1):
        assert low < high, "higher bound must be greater than lower."
        self.name = name
        self.high = high
        self.low = low
        self.res = res
        # one should not access (especially add things) directly
        self._sets = {}

    
    def __call__(self, x):
        if not(self.low <= x <= self.high):
            warn(f"{x} is outside of domain!")
        memberships = {name: s.func(x) for 
                        name, s, in self._sets.items()}
        return memberships

    def __str__(self):
        return self.name

    def __getattr__(self, name):
        if name in self._sets:
            return self._sets[name]
        else:
            raise AttributeError(f"{name} is not a set or attribute")
            
    def __setattr__(self, name, value):
        # it's a domain attr
        if name in self._allowed_attrs:
            object.__setattr__(self, name, value)
        # we've got a fuzzyset
        else:
            if not isinstance(value, Set):
                raise ValueError(f"({name}) {value} must be a Set")
            self._sets[name] = value
            value.domain = self
            value.name = name
            
    def __delattr__(self, name):
        if name in self._sets:
            del self._sets[name]
        else:
            raise FuzzyWarning("Trying to delete a regular attr, this needs extra care.")

class Set:
    """
    A fuzzyset defines a 'region' within a domain.
    The associated membership function defines 'how much' a given value is
    inside this region - how 'true' the value is.

    Sets and functions MUST NOT be mixed because functions don't have
    the methods of the sets needed for the logic.

    Sets that are returned from one of the operations are 'derived sets' or
    'Superfuzzysets' according to Zadeh.
    
    Note that most checks are merely assertions that can be optimized away.
    DO NOT RELY on these checks and use tests to make sure that only valid calls are made.
    """
    _domain = None
    _name = None
    
    def __init__(self, func:callable, *, domain=None, name=None):
        assert callable(func) or isinstance(func, str)
        # if func is a str, we've got a pickled function via repr
        
        if isinstance(func, str):
            try: 
                func = pickle.loads(func)
            except:
                FuzzyWarning("Can't load pickled function %s" % func)
        self.func = func
        # either both must be given or none
        assert (domain is None) == (name is None)
        self.domain = domain
        if domain is not None:
            self.domain._sets[name] = self
        self.name = name
        
    def name_():
        """Name of the fuzzy set."""
        def fget(self):
            return self._name
        def fset(self, value):
            if self._name is None:
                self._name = value 
            else:
                raise FuzzyWarning("Can't change name once assigned.")
        return locals()
    name = property(**name_())
    del name_
    
    def domain_():
        """Domain of the fuzzy set."""
        def fget(self):
            return self._domain
        def fset(self, value):
            if self._domain is None:
                self._domain = value 
            else:
                # maybe could be solved by copy()
                # but it's probably easier to just delete and make new
                raise FuzzyWarning("Can't change domain once assigned.")
        return locals()
    domain = property(**domain_())
    del domain_

    def __call__(self, x):
        return self.func(x)

    def __invert__(self):
        return Set(inv(self.func))

    def __and__(self, other):
        return Set(MIN(self.func, other.func))

    def __or__(self, other):
        return Set(MAX(self.func, other.func))

    def __mul__(self, other):
        return Set(product(self.func, other.func))

    def __add__(self, other):
        return Set(bounded_sum(self.func, other.func))

    def __pow__(self, power):
        """pow is used with hedges"""
        return Set(lambda x: pow(self.func(x), power))
    
    def __eq__(self, other):
        """A set is equal with another if it returns exactly the same values."""
        if self.domain is None or other.domain is None:
            # It would require complete AST analysis to check whether both Sets
            # represent the same recursive functions - 
            # additionally, there are infinitely many mathematically equivalent 
            # functions that don't have the same bytecode...
            raise FuzzyWarning(f"Impossible to determine.")
        else:
            # however, if domains ARE assigned (whether or not it's the same domain), 
            # we simply can check if they map to the same values 
            return array_equal(self.array(), other.array())

    def plot(self, low=None, high=None, res=None):
        """Graph the set.
        Use the bounds and resolution of the domain to display the set
        unless specified otherwise.
        """
        if self.domain is None:
            raise FuzzyWarning("No domain assigned, cannot plot.")

        low = self.domain.low if low is None else low
        high = self.domain.high if high is None else high
        res = self.domain.res if res is None else res
        R = arange(low, high, res)
        V = [self.func(x) for x in R]
        plt.plot(R, V)
    
    def array(self):
        # arange may not be ideal for this
        if self.domain is None:
            raise FuzzyWarning("No domain assigned.")
        return fromiter((self.func(x) for x in arange(self.domain.low,
                                                     self.domain.high,
                                                     self.domain.res)), float)

    def __repr__(self):
        """
        Return a string representation of the Set that reconstructs the set with eval().
        
        *******
        this is harder than expected since all functions are (recursive!) closures which
        can't simply be pickled. If this functionality really is needed, all functions 
        would have to be peppered with closure-returning overhead such as
        
        def create_closure_and_function(*args):
            func = None
            def create_function_closure():
                return func

            closure = create_function_closure.__closure__
            func = types.FunctionType(*args[:-1] + [closure])
            return func
        """
        return NotImplemented
        #return f"Set({}, domain={self.domain}, name={self.name})"
    
    def __str__(self):
        if self.name is None and self.domain is None:
            return f"dangling Set({self.func})"
        else:
            return f"{self.domain}.{self.name}"


class Rule:
    """
    A rule is used to combine fuzzysets of different domains, aggregating the
    results of the previous calculations.

    It works like this:
    >>> temp = Domain("temperature", 0, 100)
    >>> temp.hot = Set(lambda x: 1)
    >>> dist = Domain("distance", 0, 300)
    >>> dist.close = Set(lambda x: 0)
    
    #>>> r = Rule(min, ["distance.close", "temperature.hot"])
    #>>> d1 = temp(32)   # {'temperature.hot': 1}
    #>>> d2 = dist(5)    # {'distance.close': 0}
    #>>> d = d1.copy()   # need to merge the results of the Domains
    #>>> d.update(d2)    # for py3.5: https://www.python.org/dev/peps/pep-0448/
    #>>> r(d)    # min(1, 0)
    #0

    Calling the domains MAY be done async for better performance, a rule only
    needs the dict with the qualified fuzzysets.
    """
    def __init__(self, *, OR:callable, AND:callable, IN:list, OUT:list):
        self.OR = OR
        self.AND = AND
        self.IN = IN
        self.OUT = OUT

    def evaluate(self):
        pass

    def plot(self):
        pass


if __name__ == "__main__":
    import doctest
    doctest.testmod()