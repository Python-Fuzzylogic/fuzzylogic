"""
Lingual hedges modify curves of membership values.

These should work with Sets and functions.
"""

from typing import overload

from .classes import Set
from .functions import Membership


@overload
def very(G: Set) -> Set: ...
@overload
def very(G: Membership) -> Membership: ...
def very(G: Set | Membership) -> Set | Membership:
    """Sharpen memberships so that only the values close 1 stay at the top."""
    if isinstance(G, Set):

        def s_f(g: Membership) -> Membership:
            def f(x: float) -> float:
                return g(x) ** 2

            return f

        return Set(s_f(G.func), domain=G.domain, name=f"very_{G.name}")
    else:

        def f(x: float) -> float:
            return G(x) ** 2

        return f


@overload
def plus(G: Set) -> Set: ...
@overload
def plus(G: Membership) -> Membership: ...
def plus(G: Set | Membership) -> Set | Membership:
    """Sharpen memberships like 'very' but not as strongly."""
    if isinstance(G, Set):

        def s_f(g: Membership) -> Membership:
            def f(x: float):
                return g(x) ** 1.25

            return f

        return Set(s_f(G.func), domain=G.domain, name=f"plus_{G.name}")
    else:

        def f(x: float) -> float:
            return G(x) ** 1.25

        return f


@overload
def minus(G: Set) -> Set: ...
@overload
def minus(G: Membership) -> Membership: ...
def minus(G: Set | Membership) -> Set | Membership:
    """Increase membership support so that more values hit the top."""
    if isinstance(G, Set):

        def s_f(g: Membership) -> Membership:
            def f(x: float) -> float:
                return g(x) ** 0.75

            return f

        return Set(s_f(G.func), domain=G.domain, name=f"minus_{G.name}")
    else:

        def f(x: float) -> float:
            return G(x) ** 0.75

        return f
