"""
Domain, Set and Rule classes for fuzzy logic.

Primary abstractions for recursive functions and arrays,
adding logical operaitons for easier handling.
"""

from typing import Callable, Iterable

try:
    import matplotlib.pyplot as plt
except ImportError:

    def plt(*args, **kwargs):
        raise ImportError(
            "matplotlib not available. Please re-install with 'pip install fuzzylogic[plotting]'"
        )


import numpy as np

from .combinators import MAX, MIN, bounded_sum, product, simple_disjoint_sum
from .functions import inv, normalize

type Number = int | float


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

    It is possible now to call derived sets without assignment first!
    >>> from .hedges import very
    >>> (very(~temp.hot) | ~very(temp.hot))(2)
    1.0

    You MUST NOT add arbitrary attributes to an *instance* of Domain - you can
    however subclass or modify the class itself. If you REALLY have to add attributes,
    make sure to "whitelist" it in __slots__ first.

    Use the Domain by calling it with the value in question. This returns a
    dictionary with the degrees of membership per set. You MAY override __call__
    in a subclass to enable concurrent evaluation for performance improvement.
    """

    __slots__ = ["_name", "_low", "_high", "_res", "_sets"]

    def __init__(
        self,
        name: str,
        low: Number,
        high: Number,
        res: Number = 1,
        sets: dict | None = None,
    ) -> None:
        """Define a domain."""
        assert low < high, "higher bound must be greater than lower."
        assert res > 0, "resolution can't be negative or zero"
        assert isinstance(name, str), "Name must be a string."
        assert str.isidentifier(name), "Name must be a valid identifier."
        self._name = name
        self._high = high
        self._low = low
        self._res = res
        self._sets = {} if sets is None else sets  # Name: Set(Function())

    def __call__(self, x):
        """Pass a value to all sets of the domain and return a dict with results."""
        if not (self._low <= x <= self._high):
            raise FuzzyWarning(f"{x} is outside of domain!")
        return {name: s.func(x) for name, s in self._sets.items()}

    def __len__(self):
        """Return the size of the domain, as the actual number of possible values, calculated internally."""
        return len(self.range)

    def __str__(self):
        """Return a string to print()."""
        return self._name

    def __repr__(self):
        """Return a string so that eval(repr(Domain)) == Domain."""
        return f"Domain('{self._name}', {self._low}, {self._high}, res={self._res}, sets={self._sets})"

    def __eq__(self, other):
        """Test equality of two domains."""
        return all([
            self._name == other._name,
            self._low == other._low,
            self._high == other._high,
            self._res == other._res,
            self._sets == other._sets,
        ])

    def __hash__(self):
        return id(self)

    def __getattr__(self, name):
        """Get the value of an attribute. Called after __getattribute__ is called with an AttributeError."""
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
            return np.linspace(self._low, self._high, int((self._high - self._low) / self._res) + 1)

    def min(self, x):
        """Standard way to get the min over all membership funcs.

        It's not just more convenient but also faster than
        to calculate all results, construct a dict, unpack the dict
        and calculate the min from that.
        """
        return min((f(x) for f in self._sets.values()), default=0)

    def max(self, x):
        """Standard way to get the max over all membership funcs."""
        return max((f(x) for f in self._sets.values()), default=0)


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

    This class uses the classical MIN/MAX operators for AND/OR. To use different operators, simply subclass &
    replace the __and__ and __or__ functions. However, be careful not to mix the classes logically,
    since it might be confusing which operator will be used (left/right binding).

    """

    type T = Set
    name = None  # these are set on assignment to the domain! DO NOT MODIFY
    domain = None

    def __init__(
        self,
        func: Callable[..., Number],
        *,
        name: str | None = None,
        domain: Domain | None = None,
    ):
        self.func: Callable[..., Number] = func
        self.domain: Domain | None = domain
        self.name: str | None = name
        self.__center_of_gravity: np.floating | None = None

    def __call__(self, x: Number | np.ndarray) -> Number | np.ndarray:
        if isinstance(x, np.ndarray):
            return np.array([self.func(v) for v in x])
        else:
            return self.func(x)

    def __invert__(self) -> T:
        """Return a new set with 1 - function."""
        return Set(inv(self.func), domain=self.domain)

    def __neg__(self) -> T:
        """Synonyme for invert."""
        return Set(inv(self.func), domain=self.domain)

    def __and__(self, other: T) -> T:
        """Return a new set with modified function."""
        assert self.domain == other.domain
        return Set(MIN(self.func, other.func), domain=self.domain)

    def __or__(self, other: T) -> T:
        """Return a new set with modified function."""
        assert self.domain == other.domain
        return Set(MAX(self.func, other.func), domain=self.domain)

    def __mul__(self, other: T) -> T:
        """Return a new set with modified function."""
        assert self.domain == other.domain
        return Set(product(self.func, other.func), domain=self.domain)

    def __add__(self, other: T) -> T:
        """Return a new set with modified function."""
        assert self.domain == other.domain
        return Set(bounded_sum(self.func, other.func), domain=self.domain)

    def __xor__(self, other: T) -> T:
        """Return a new set with modified function."""
        assert self.domain == other.domain
        return Set(simple_disjoint_sum(self.func, other.func), domain=self.domain)

    def __pow__(self, power: int) -> T:
        """Return a new set with modified function."""

        # FYI: pow is used with hedges
        def f(x: float):
            return pow(self.func(x), power)  # TODO: test this

        return Set(f, domain=self.domain)

    def __eq__(self, other: T) -> bool:
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
            return np.array_equal(self.array(), other.array())

    def __le__(self, other: T) -> bool:
        """If this <= other, it means this is a subset of the other."""
        assert self.domain == other.domain
        if self.domain is None or other.domain is None:
            raise FuzzyWarning("Can't compare without Domains.")
        return all(np.less_equal(self.array(), other.array()))

    def __lt__(self, other: T) -> bool:
        """If this < other, it means this is a proper subset of the other."""
        assert self.domain == other.domain
        if self.domain is None or other.domain is None:
            raise FuzzyWarning("Can't compare without Domains.")
        return all(np.less(self.array(), other.array()))

    def __ge__(self, other: T) -> bool:
        """If this >= other, it means this is a superset of the other."""
        assert self.domain == other.domain
        if self.domain is None or other.domain is None:
            raise FuzzyWarning("Can't compare without Domains.")
        return all(np.greater_equal(self.array(), other.array()))

    def __gt__(self, other: T) -> bool:
        """If this > other, it means this is a proper superset of the other."""
        assert self.domain == other.domain
        if self.domain is None or other.domain is None:
            raise FuzzyWarning("Can't compare without Domains.")
        return all(np.greater(self.array(), other.array()))

    def __len__(self) -> int:
        """Number of membership values in the set, defined by bounds and resolution of domain."""
        if self.domain is None:
            raise FuzzyWarning("No domain.")
        return len(self.array())

    @property
    def cardinality(self) -> int:
        """The sum of all values in the set."""
        if self.domain is None:
            raise FuzzyWarning("No domain.")
        return sum(self.array())

    @property
    def relative_cardinality(self) -> np.floating | float:
        """Relative cardinality is the sum of all membership values by number of all values."""
        if self.domain is None:
            raise FuzzyWarning("No domain.")
        if len(self) == 0:
            # this is highly unlikely and only possible with res=inf but still..
            raise FuzzyWarning("The domain has no element.")
        return self.cardinality / len(self)

    def concentrated(self) -> T:
        """
        Alternative to hedge "very".

        Returns a new set that has a reduced amount of values the set includes and to dampen the
        membership of many values.
        """
        return Set(lambda x: self.func(x) ** 2, domain=self.domain)

    def intensified(self) -> T:
        """
        Alternative to hedges.

        Returns a new set where the membership of values are increased that
        already strongly belong to the set and dampened the rest.
        """

        def f(x):
            return 2 * self.func(x) ** 2 if x < 0.5 else 1 - 2 * (1 - self.func(x) ** 2)

        return Set(f, domain=self.domain)

    def dilated(self) -> T:
        """Expand the set with more values and already included values are enhanced."""
        return Set(lambda x: self.func(x) ** 1.0 / 2.0, domain=self.domain)

    def multiplied(self, n) -> T:
        """Multiply with a constant factor, changing all membership values."""
        return Set(lambda x: self.func(x) * n, domain=self.domain)

    def plot(self):
        """Graph the set in the given domain."""
        if self.domain is None:
            raise FuzzyWarning("No domain assigned, cannot plot.")
        R = self.domain.range
        V = [self.func(x) for x in R]
        plt.plot(R, V)

    def array(self) -> np.ndarray:
        """Return an array of all values for this set within the given domain."""
        if self.domain is None:
            raise FuzzyWarning("No domain assigned.")
        return np.fromiter((self.func(x) for x in self.domain.range), float)

    def range(self) -> np.ndarray:
        """Return the range of the domain."""
        if self.domain is None:
            raise FuzzyWarning("No domain assigned.")
        return self.domain.range

    def center_of_gravity(self) -> np.floating | float:
        """Return the center of gravity for this distribution, within the given domain."""
        if self.__center_of_gravity is not None:
            return self.__center_of_gravity
        assert self.domain is not None, "No center of gravity with no domain."
        weights = self.array()
        if sum(weights) == 0:
            return 0
        cog = np.average(self.domain.range, weights=weights)
        self.__center_of_gravity = cog
        return cog

    def __repr__(self) -> str:
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
        if self.domain is not None:
            return f"{self.domain._name}."
        return f"Set({__name__}({self.func.__qualname__})"

    def __str__(self) -> str:
        """Return a string for print()."""
        if self.domain is not None:
            return f"{self.domain._name}.{self.name}"
        if self.name is None:
            return f"dangling Set({self.func})"
        else:
            return f"dangling Set({self.name}"

    def normalized(self) -> T:
        """Return a set that is normalized *for this domain* with 1 as max."""
        if self.domain is None:
            raise FuzzyWarning("Can't normalize without domain.")
        return Set(normalize(max(self.array()), self.func), domain=self.domain)

    def __hash__(self) -> int:
        return id(self)


class Rule:
    """
    Collection of bound sets spanning a multi-dimensional space of their domains, mapping to a target domain.

    """

    type T = Rule

    def __init__(self, conditions_in: dict[Iterable[Set] | Set, Set]):
        self.conditions: dict[frozenset[Set], Set] = {}
        for if_sets, then_set in conditions_in.items():
            if isinstance(if_sets, Set):
                if_sets = (if_sets,)
            self.conditions[frozenset(if_sets)] = then_set

    def __add__(self, other: T):
        return Rule({**self.conditions, **other.conditions})

    def __radd__(self, other: T | int) -> T:
        # we're using sum(..)
        if isinstance(other, int):
            return self
        return Rule({**self.conditions, **other.conditions})

    def __or__(self, other: T):
        return Rule({**self.conditions, **other.conditions})

    def __eq__(self, other: T):
        return self.conditions == other.conditions

    def __getitem__(self, key):
        return self.conditions[frozenset(key)]

    def __call__(self, values: dict[Domain, float | int], method="cog") -> np.floating | float | None:
        """Calculate the infered value based on different methods.
        Default is center of gravity (cog).
        """
        assert isinstance(values, dict), "Please make sure to pass a dict[Domain, float|int] as values."
        assert len(self.conditions) > 0, "No point in having a rule with no conditions, is there?"
        match method:
            case "cog":
                # iterate over the conditions and calculate the actual values and weights contributing to cog
                target_weights: list[tuple[Set, Number]] = []
                target_domain = list(self.conditions.values())[0].domain
                assert target_domain is not None, "Target domain must be defined."
                for if_sets, then_set in self.conditions.items():
                    actual_values: list[Number] = []
                    assert then_set.domain == target_domain, "All target sets must be in the same Domain."
                    for s in if_sets:
                        assert s.domain is not None, "Domains must be defined."
                        actual_values.append(s(values[s.domain]))
                    x = min(actual_values, default=0)
                    if x > 0:
                        target_weights.append((then_set, x))
                if not target_weights:
                    return None
                sum_weights = 0
                sum_weighted_cogs = 0
                for then_set, weight in target_weights:
                    sum_weighted_cogs += then_set.center_of_gravity() * weight
                    sum_weights += weight
                index = sum_weighted_cogs / sum_weights

                return (target_domain._high - target_domain._low) / len(
                    target_domain.range
                ) * index + target_domain._low

            case "centroid":  # centroid == center of mass == center of gravity for simple solids
                raise NotImplementedError("actually the same as 'cog' if densities are uniform.")
            case "bisector":
                raise NotImplementedError("Bisector method not implemented yet.")
            case "mom":
                raise NotImplementedError("Middle of max method not implemented yet.")
            case "som":
                raise NotImplementedError("Smallest of max method not implemented yet.")
            case "lom":
                raise NotImplementedError("Largest of max method not implemented yet.")
            case _:
                raise ValueError("Invalid method.")


def rule_from_table(table: str, references: dict):
    """Turn a (2D) string table into a Rule of fuzzy sets.

    ATTENTION: This will eval() all strings in the table.
    This can pose a potential security risk if the table originates from an untrusted source.

    Using a table will considerably reduce the amount of required text to describe all rules,
    but there are two critical drawbacks: Tables are limited to 2 input variables (2D) and they are strings,
    with no IDE support. It is strongly recommended to check the Rule output for consistency.
    For example, a trailing "." will result in a SyntaxError when eval()ed.
    """
    import io
    from itertools import product
    from typing import Any

    import pandas as pd

    df = pd.read_table(io.StringIO(table), sep=r"\s+")

    D: dict[tuple[Any, Any], Any] = {
        (
            eval(df.index[x].strip(), references),  # type: ignore
            eval(df.columns[y].strip(), references),  # type: ignore
        ): eval(df.iloc[x, y], references)  # type: ignore
        for x, y in product(range(len(df.index)), range(len(df.columns)))
    }
    return Rule(D)  # type: ignore


if __name__ == "__main__":
    import doctest

    doctest.testmod()
