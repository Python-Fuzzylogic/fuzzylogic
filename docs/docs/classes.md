Module fuzzylogic.classes
=========================
Domain, Set and Rule classes for fuzzy logic.

Primary abstractions for recursive functions and arrays, 
adding logical operaitons for easier handling.

Domain
-------

`Domain(name: str, low: float, high: float, res=float | int, sets: dict = None)`
:   A domain is a 'measurable' dimension of 'real' values like temperature.

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
    
    
   
   It is possible now to call derived sets without assignment first!
   
    >>> from .hedges import very
    >>> (very(~temp.hot) | ~very(temp.hot))(2)
    1
    
   You MUST NOT add arbitrary attributes to an *instance* of Domain - you can
   however subclass or modify the class itself. If you REALLY have to add attributes,
   make sure to "whitelist" it in __slots__ first.
    
   Use the Domain by calling it with the value in question. This returns a
   dictionary with the degrees of membership per set. You MAY override __call__
   in a subclass to enable concurrent evaluation for performance improvement.
    
Define a domain.
<details>
<summary>click here to see Domain class source code</summary>

```
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

    It is possible now to call derived sets without assignment first!
    >>> from .hedges import very
    >>> (very(~temp.hot) | ~very(temp.hot))(2)
    1

    You MUST NOT add arbitrary attributes to an *instance* of Domain - you can
    however subclass or modify the class itself. If you REALLY have to add attributes,
    make sure to "whitelist" it in __slots__ first.

    Use the Domain by calling it with the value in question. This returns a
    dictionary with the degrees of membership per set. You MAY override __call__
    in a subclass to enable concurrent evaluation for performance improvement.
    """

    __slots__ = ["_name", "_low", "_high", "_res", "_sets"]

    def __init__(self, name: str, low: float, high: float, res=float | int, sets: dict = None):
        """Define a domain."""
        assert low < high, "higher bound must be greater than lower."
        assert res > 0, "resolution can't be negative or zero"
        self._name = name
        self._high = high
        self._low = low
        self._res = res
        self._sets = {} if sets is None else sets  # Name: Set(Function())

    def __call__(self, X):
        """Pass a value to all sets of the domain and return a dict with results."""
        if isinstance(X, np.ndarray):
            if any(not (self._low <= x <= self._high) for x in X):
                raise FuzzyWarning("Value in array is outside of defined range!")
            res = {}
            for s in self._sets.values():
                vector = np.vectorize(s.func, otypes=[float])
                res[s] = vector(X)
            return res
        if not (self._low <= X <= self._high):
            warn(f"{X} is outside of domain!")
        return {s: s.func(X) for name, s in self._sets.items()}

    def __str__(self):
        """Return a string to print()."""
        return self._name

    def __repr__(self):
        """Return a string so that eval(repr(Domain)) == Domain."""
        return f"Domain('{self._name}', {self._low}, {self._high}, res={self._res}, sets={self._sets})"

    def __eq__(self, other):
        """Test equality of two domains."""
        return all(
            [
                self._name == other._name,
                self._low == other._low,
                self._high == other._high,
                self._res == other._res,
                self._sets == other._sets,
            ]
        )

    def __hash__(self):
        return id(self)

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

    @property
    def range(self):
        """Return an arange object with the domain's specifics.

        This is used to conveniently iterate over all possible values
        for plotting etc.

        High upper bound is INCLUDED unlike range.
        """
        if int(self._res) == self._res:
            return np.arange(self._low, self._high + self._res, int(self._res))
        else:
            return np.linspace(
                self._low, self._high, int((self._high - self._low) / self._res) + 1
            )

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
```
</details>
---

### max

   `max(self, x)`
   : Standard way to get the max over all membership funcs.

---

### min
   `min(self, x)`
   :   Standard way to get the min over all membership funcs.
       It's not just more convenient but also faster than
       to calculate all results, construct a dict, unpack the dict
       and calculate the min from that.


---

Rule
-------

`Rule(conditions, func=None)`
:   A collection of bound sets that span a multi-dimensional space of their respective domains.
```
class Rule:
    """
    A collection of bound sets that span a multi-dimensional space of their respective domains.
    """

    def __init__(self, conditions, func=None):
        self.conditions = {frozenset(C): O for C, O, in conditions.items()}
        self.func = func

    def __add__(self, other):
        assert isinstance(other, Rule)
        return Rule({**self.conditions, **other.conditions})

    def __radd__(self, other):
        assert isinstance(other, (Rule, int))
        # we're using sum(..)
        if isinstance(other, int):
            return self
        return Rule({**self.conditions, **other.conditions})

    def __or__(self, other):
        assert isinstance(other, Rule)
        return Rule({**self.conditions, **other.conditions})

    def __eq__(self, other):
        return self.conditions == other.conditions

    def __getitem__(self, key):
        return self.conditions[frozenset(key)]

    def __call__(self, args: "dict[Domain, float]", method="cog"):
        """Calculate the infered value based on different methods.
        Default is center of gravity (cog).
        """
        assert len(args) == max(
            len(c) for c in self.conditions.keys()
        ), "Number of values must correspond to the number of domains defined as conditions!"
        assert isinstance(args, dict), "Please make sure to pass in the values as a dictionary."
        if method == "cog":
            assert (
                len({C.domain for C in self.conditions.values()}) == 1
            ), "For CoG, all conditions must have the same target domain."
            actual_values = {f: f(args[f.domain]) for S in self.conditions.keys() for f in S}

            weights = []
            for K, v in self.conditions.items():
                x = min((actual_values[k] for k in K if k in actual_values), default=0)
                if x > 0:
                    weights.append((v, x))

            if not weights:
                return None
            target_domain = list(self.conditions.values())[0].domain
            index = sum(v.center_of_gravity * x for v, x in weights) / sum(x for v, x in weights)
            return (target_domain._high - target_domain._low) / len(
                target_domain.range
            ) * index + target_domain._low
```
---

Set
-------

`class Set(func: <built-in function callable>, *, name=None, domain=None)`
: A fuzzyset defines a 'region' within a domain.
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

### Array
`array(self)`
: Return an array of all values for this set within the given domain.

### Concentrated
`concentrated(self)`
: Alternative to hedge "very".
  Returns a new set that has a reduced amount of values the set includes and to dampen the
  membership of many values.

### Dilated
`dilated(self)`
: Expand the set with more values and already included values are enhanced.

### Intensified
`intensified(self)`
: Alternative to hedges.Returns a new set where the membership of values are increased that
  already strongly belong to the set and dampened the rest.

### Multiplied
`multiplied(self, n)`
: Multiply with a constant factor, changing all membership values.

### Normalized
`normalized(self)`
: Return a set that is normalized *for this domain* with 1 as max.

### Plot
`plot(self)`
: Graph the set in the given domain.
