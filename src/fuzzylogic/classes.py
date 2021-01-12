
"""
Domain and Set classes for fuzzy logic.

Primary abstractions for recursive functions for better handling.
"""

import matplotlib.pyplot as plt
import numpy as np
import pickle

from logging import warn
from numpy import arange
from numpy import array_equal
from numpy import fromiter
from numpy import greater
from numpy import greater_equal
from numpy import less
from numpy import less_equal

from .combinators import MAX
from .combinators import MIN
from .combinators import bounded_sum
from .combinators import product
from .combinators import simple_disjoint_sum
from .functions import inv
from .functions import normalize

class FuzzyWarning(UserWarning):
    """Extra Exception so that user code can filter exceptions specific to this lib."""
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
    NOT: ~temp.hot(2) or ~(temp.hot.)(2) 
    BUT:
    >>> not_hot = ~temp.hot
    >>> not_hot(2)
    1

    You MUST NOT add arbitrary attributes to an *instance* of Domain - you can
    however subclass or modify the class itself. If you REALLY have to add attributes, 
    make sure to "whitelist" it in __slots__ first. 

    Use the Domain by calling it with the value in question. This returns a
    dictionary with the degrees of membership per set. You MAY override __call__
    in a subclass to enable concurrent evaluation for performance improvement.
    >>> temp.cold = not_hot
    >>> temp(3) == {"hot": 0, "cold": 1}
    True
    """
    
    __slots__ = ['_name', '_low', '_high', '_res', '_sets']

    def __init__(self, name, low, high, *, res=1, sets:dict=None):
        """Define a domain."""
        assert low < high, "higher bound must be greater than lower."
        assert res > 0, "resolution can't be negative or zero"
        self._name = name
        self._high = high
        self._low = low
        self._res = res
        self._sets = {} if sets is None else sets  # Name: Set(Function())

    
    def __call__(self, x):
        """Pass a value to all sets of the domain and return a dict with results."""
        if not(self._low <= x <= self._high):
            warn(f"{x} is outside of domain!")
        memberships = {name: s.func(x) for name, s in self._sets.items()}
        return memberships

    def __str__(self):
        """Return a string to print()."""
        return self._name
    
    def __repr__(self):
        """Return a string so that eval(repr(Domain)) == Domain."""
        return f"Domain('{self._name}', {self._low}, {self._high}, res={self._res}, sets={self._sets})"
    
    def __eq__(self, other):
        """Test equality of two domains."""
        return all([self._name == other._name,
                   self._low == other._low,
                   self._high == other._high,
                   self._res == other._res,
                   self._sets == other._sets])
    
    def __getattr__(self, name):
        """Get the value of an attribute. Is called after __getattribute__ is called with an AttributeError."""
        if name in self._sets:
            return self._sets[name]
        else:
            raise AttributeError(f"{name} is not a set or attribute")
            
    def __setattr__(self, name, value):
        """Define a set within a domain or assign a value to a domain attribute."""
        # It's a domain attr
        if name in self.__slots__:
            object.__setattr__(self, name, value)
        # We've got a fuzzyset
        else:
            assert str.isidentifier(name), f"{name} must be an identifier."
            if not isinstance(value, Set):
                # Often useful to just assign a function for simple sets..
                value = Set(value)
            # However, we need the abstraction if we want to use Superfuzzysets (derived sets).
            self._sets[name] = value
            value.domain = self
            value.name = name
            
    def __delattr__(self, name):
        """Delete a fuzzy set from the domain."""
        if name in self._sets:
            del self._sets[name]
        else:
            raise FuzzyWarning("Trying to delete a regular attr, this needs extra care.")

    def range(self):
        """Return an arange object with the domain's specifics.
        
        This is used to conveniently iterate over all possible values
        for plotting etc.
        
        High upper bound is INCLUDED unlike range.
        """
        return arange(self._low, self._high + self._res, self._res)
            
    def min(self, x):
        """Standard way to get the min over all membership funcs.
        
        It's not just more convenient but also faster than
        to calculate all results, construct a dict, unpack the dict
        and calculate the min from that.
        """
        return min(f(x) for f in self._sets.values())
    
    def max(self, x):
        """Standard way to get the max over all membership funcs."""
        return max(f(x) for f in self._sets.values())
            
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
    
    This class uses the classical MIN/MAX operators for AND/OR. To use different operators, simply subclass and 
    replace the __and__ and __or__ functions. However, be careful not to mix the classes logically, 
    since it might be confusing which operator will be used (left/right binding).
    
    """
    name = None  # these are set on assignment to the domain! DO NOT MODIFY
    domain = None
    
    
    def __init__(self, func:callable, *, name=None, domain=None):
        """Initialize the set."""
        assert callable(func) or isinstance(func, str)
        # if func is a str, we've got a pickled function via repr
        if isinstance(func, str):
            try: 
                func = pickle.loads(func)
            except:
                FuzzyWarning("Can't load pickled function %s" % func)
        self.func = func
        
        if name is not None and domain is not None:
            setattr(domain, name, self)
        
        if bool(name)^bool(domain):
            raise FuzzyWarning("Name or domain is provided, but not both!")

    def __call__(self, x):
        """Call the function of the set (which can be of any arbitrary complexity)."""
        return self.func(x)

    def __invert__(self):
        """Return a new set with modified function."""
        return Set(inv(self.func)),
    
    def __neg__(self):
        return Set(inv(self.func))
    
    def __and__(self, other):
        """Return a new set with modified function."""
        return Set(MIN(self.func, other.func))

    def __or__(self, other):
        """Return a new set with modified function."""
        return Set(MAX(self.func, other.func))

    def __mul__(self, other):
        """Return a new set with modified function."""
        return Set(product(self.func, other.func))

    def __add__(self, other):
        """Return a new set with modified function."""
        return Set(bounded_sum(self.func, other.func))
    
    def __xor__(self, other):
        """Return a new set with modified function."""
        return Set(simple_disjoint_sum(self.func, other.func))

    def __pow__(self, power):
        """Return a new set with modified function."""
        #FYI: pow is used with hedges
        return Set(lambda x: pow(self.func(x), power))
    
    def __eq__(self, other):
        """A set is equal with another if both return the same values over the same range."""
        if self.domain is None or other.domain is None:
            # It would require complete AST analysis to check whether both Sets
            # represent the same recursive functions - 
            # additionally, there are infinitely many mathematically equivalent 
            # functions that don't have the same bytecode...
            raise FuzzyWarning("Impossible to determine.")
        else:
            # however, if domains ARE assigned (whether or not it's the same domain), 
            # we simply can check if they map to the same values 
            return array_equal(self.array(), other.array())
        
    def __le__(self, other):
        """If this <= other, it means this is a subset of the other."""
        if self.domain is None or other.domain is None:
            raise FuzzyWarning("Can't compare without Domains.")
        return all(less_equal(self.array(), other.array()))
    
    def __lt__(self, other):
        """If this < other, it means this is a proper subset of the other."""
        if self.domain is None or other.domain is None:
            raise FuzzyWarning("Can't compare without Domains.")
        return all(less(self.array(), other.array()))
    
    def __ge__(self, other):
        """If this >= other, it means this is a superset of the other."""
        if self.domain is None or other.domain is None:
            raise FuzzyWarning("Can't compare without Domains.")
        return all(greater_equal(self.array(), other.array()))

    def __gt__(self, other):
        """If this > other, it means this is a proper superset of the other."""
        if self.domain is None or other.domain is None:
            raise FuzzyWarning("Can't compare without Domains.")
        return all(greater(self.array(), other.array()))
    
    def __len__(self):
        """Number of membership values in the set, defined by bounds and resolution of domain."""
        if self.domain is None:
            raise FuzzyWarning("No domain.")
        return len(self.array())
    
    def cardinality(self):
        """The sum of all values in the set."""
        if self.domain is None:
            raise FuzzyWarning("No domain.")
        return sum(self.array())

    def relative_cardinality(self):
        """Relative cardinality is the sum of all membership values by number of all values."""
        if self.domain is None:
            raise FuzzyWarning("No domain.")
        if len(self) == 0:
            # this is highly unlikely and only possible with res=inf but still..
            raise FuzzyWarning("The domain has no element.")
        return self.cardinality() / len(self)
    
    def concentrated(self):
        """
        Alternative to hedge "very".
        
        Returns an new set that has a reduced amount of values the set includes and to dampen the
        membership of many values.
        """
        return Set(lambda x: self.func(x) ** 2)

    def intensified(self):
        """
        Alternative to using hedges.
        
        Returns a new set where the membership of values are increased that 
        already strongly belong to the set and dampened the rest.
        """
        def f(x):
            if x < 0.5:
                return 2 * self.func(x)**2
            else:
                return 1 - 2(1 - self.func(x)**2)
        return Set(f)
        
    def dilated(self):
        """Expand the set with more values and already included values are enhanced.
        """
        return Set(lambda x: self.func(x) ** 1./2.)

    def multiplied(self, n):
        """Multiply with a constant factor, changing all membership values."""
        return Set(lambda x: self.func(x) * n)
        
    def plot(self):
        """Graph the set in the given domain."""
        if self.domain is None:
            raise FuzzyWarning("No domain assigned, cannot plot.")
        R = self.domain.range()
        V = [self.func(x) for x in R]
        plt.plot(R, V)
    
    def array(self):
        """Return an array of all values for this set within the given domain."""
        if self.domain is None:
            raise FuzzyWarning("No domain assigned.")
        return fromiter((self.func(x) for x in self.domain.range()), float)

    def __repr__(self):
        """
        Return a string representation of the Set that reconstructs the set with eval().
        
        *******
        Current implementation does NOT work correctly.
        
        This is harder than expected since all functions are (recursive!) closures which
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
        return f"Set({self.func})"
    
    def __str__(self):
        """Return a string for print()."""
        if self.name is None and self.domain is None:
            return f"dangling Set({self.func})"
        else:
            return f"{self.domain._name}.{self.name}"
        
    def normalized(self):
        """Return a set that is normalized *for this domain* with 1 as max."""
        if self.domain is None:
            raise FuzzyWarning("Can't normalize without domain.")
        return Set(normalize(max(self.array()), self.func))

if __name__ == "__main__":
    import doctest
    doctest.testmod()