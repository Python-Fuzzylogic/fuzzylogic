from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .classes import Membership, Set


def cog(target_weights: list[tuple[Set, float]]) -> float:
    """
    Defuzzify using the center-of-gravity (or centroid) method.
    target_weights: list of tuples (then_set, weight)

    The COG is defined by the formula:

        COG = (∑ μᵢ × xᵢ) / (∑ μᵢ)

    where:
        • μᵢ is the membership value for the iᵗʰ element,
        • xᵢ is the corresponding value for the iᵗʰ element in the output domain.

    """

    sum_weights = sum(weight for _, weight in target_weights)
    if sum_weights == 0:
        raise ValueError("Total weight is zero. Cannot compute center-of-gravity.")
    sum_weighted_cogs = sum(then_set.center_of_gravity() * weight for then_set, weight in target_weights)
    return sum_weighted_cogs / sum_weights


def bisector(
    aggregated_membership: Membership,
    points: list[float],
    step: float,
) -> float:
    """
    Defuzzify via the bisector method.
    aggregated_membership: function mapping crisp value x -> membership degree (typically in [0,1])
    points: discretized points in the target domain
    step: spacing between points
    """
    total_area = sum(aggregated_membership(x) * step for x in points)
    half_area = total_area / 2.0
    cumulative = 0.0
    for x in points:
        cumulative += aggregated_membership(x) * step
        if cumulative >= half_area:
            return x
    return points[-1]


def mom(aggregated_membership: Membership, points: list[float]) -> float | None:
    """
    Mean of Maxima (MOM): average the x-values where the aggregated membership is maximal.
    """
    max_points = _get_max_points(aggregated_membership, points)
    return sum(max_points) / len(max_points) if max_points else None


def som(aggregated_membership: Membership, points: list[float]) -> float | None:
    """
    Smallest of Maxima: return the smallest x-value at which the aggregated membership is maximal.
    """
    return min(_get_max_points(aggregated_membership, points), default=None)


def lom(aggregated_membership: Membership, points: list[float]) -> float | None:
    """
    Largest of Maxima: return the largest x-value at which the aggregated membership is maximal.
    """
    return max(_get_max_points(aggregated_membership, points), default=None)


def _get_max_points(aggregated_membership: Membership, points: list[float]) -> list[float]:
    values_points = [(x, aggregated_membership(x)) for x in points]
    max_value = max(y for (_, y) in values_points)
    tol = 1e-6  # tolerance for floating point comparisons
    return [x for (x, y) in values_points if abs(y - max_value) < tol]
