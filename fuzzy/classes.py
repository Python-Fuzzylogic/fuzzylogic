
import matplotlib.pyplot as plt
from numpy import arange, fromiter, array_equal, less_equal, greater_equal, less, greater
import numpy as np
from logging import warn
import pickle

from fuzzy.functions import inv, normalize
from fuzzy.combinators import MAX, MIN, product, bounded_sum, simple_disjoint_sum

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
    NOT: ~temp.hot(2) or ~(temp.hot.)(2) 
    BUT:
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
    >>> temp(3) == {"hot": 0, "cold": 1}
    True
    """
    _allowed_attrs = ['name', 'low', 'high', 'res', '_sets']

    def __init__(self, name, low, high, *, res=1, sets:dict=None):
        assert low < high, "higher bound must be greater than lower."
        assert res > 0, "resolution can't be negative or zero"
        self.name = name
        self.high = high
        self.low = low
        self.res = res
        # one should not access (especially add things) directly
        self._sets = {} if sets is None else sets

    
    def __call__(self, x):
        if not(self.low <= x <= self.high):
            warn(f"{x} is outside of domain!")
        memberships = {name: s.func(x) for 
                        name, s, in self._sets.items()}
        return memberships

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"Domain('{self.name}', {self.low}, {self.high}, res={self.res}, sets={self._sets})"
    
    def __eq__(self, other):
        return all([self.name == other.name,
                   self.low == other.low,
                   self.high == other.high,
                   self.res == other.res,
                   self._sets == other._sets])

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

    def range(self):
        """Return an arange object with the domain's specifics.
        
        This is used to conveniently iterate over all possible values
        for plotting etc.
        """
        return arange(self.low, self.high, self.res)
            
    def MIN(self, x):
        """Standard way to get the min over all membership funcs.
        
        It's not just more convenient but also faster than
        to calculate all results, construct a dict, unpack the dict
        and calculate the min from that.
        """
        return min(f(x) for f in self._sets.values())
    
    def MAX(self, x):
        """Standard way to get the max over all membership funcs.
        """
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
        """Name of the fuzzy set.
        
        Tricky because it's coupled to the domain assignment.
        """
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
        """Domain of the fuzzy set.
        
        Tricky because it's coupled to the domain assignment.
        """
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
    
    def __xor__(self, other):
        return Set(simple_disjoint_sum(self.func, other.func))

    def __pow__(self, power):
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
        if self.domain is None:
            raise FuzzyWarning("No domain.")
        return len(self.array())
    
    def cardinality(self):
        if self.domain is None:
            raise FuzzyWarning("No domain.")
        return sum(self.array())

    def relative_cardinality(self):
        if self.domain is None:
            raise FuzzyWarning("No domain.")
        if len(self) == 0:
            # this is highly unlikely and only possible with res=inf but still..
            raise FuzzyWarning("The domain has no element.")
        return self.cardinality() / len(self)
        
    def plot(self):
        """Graph the set.
        Use the bounds and resolution of the domain to display the set
        unless specified otherwise.
        """
        if self.domain is None:
            raise FuzzyWarning("No domain assigned, cannot plot.")
        R = self.domain.range()
        V = [self.func(x) for x in R]
        plt.plot(R, V)
    
    def array(self):
        if self.domain is None:
            raise FuzzyWarning("No domain assigned.")
        return fromiter((self.func(x) for x in self.domain.range()),
                        float)

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
        return f"Set({self.func}, domain={self.domain}, name={self.name})"
    
    def __str__(self):
        if self.name is None and self.domain is None:
            return f"dangling Set({self.func})"
        else:
            return f"{self.domain}.{self.name}"
        
    def normalized(self):
        """Returns a set *in this domain* whose max value is 1."""
        if self.domain is None:
            raise FuzzyWarning("Can't normalize without domain.")
        else:
            return Set(normalize(max(self.array()), self.func), 
                            domain=self.domain,
                            name=f"normalized_{self.name}")

if __name__ == "__main__":
    import doctest
    doctest.testmod()