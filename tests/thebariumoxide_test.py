from matplotlib import pyplot as plt

from fuzzylogic.classes import Domain, Rule
from fuzzylogic.functions import R, S, trapezoid, triangular

left = Domain("left_obstacle_sensor", 0, 100, res=0.1)
right = Domain("right_obstacle_sensor", 0, 100, res=0.1)
theta = Domain("θ", -50.5, 50.5, res=0.1)

left.veryStrong = S(0, 25)
left.strong = trapezoid(0, 25, 25, 50)
left.medium = trapezoid(25, 50, 50, 75)
left.weak = trapezoid(50, 75, 75, 100)
left.veryWeak = R(75, 100)

right.veryStrong = S(0, 25)
right.strong = trapezoid(0, 25, 25, 50)
right.medium = trapezoid(25, 50, 50, 75)
right.weak = trapezoid(50, 75, 75, 100)
right.veryWeak = R(75, 100)

theta.mediumRight = triangular(-50.5, -49.5)
theta.smallRight = triangular(-25.5, -24.5)
theta.noTurn = triangular(-0.5, 0.5)
theta.smallLeft = triangular(24.5, 25.5)
theta.mediumLeft = triangular(49.5, 50.5)

rules = Rule({
    (left.veryStrong, right.veryStrong): theta.noTurn,
    (left.veryStrong, right.strong): theta.smallRight,
    (left.veryStrong, right.medium): theta.smallRight,
    (left.veryStrong, right.weak): theta.mediumRight,
    (left.veryStrong, right.veryWeak): theta.mediumRight,
    (left.strong, right.veryStrong): theta.smallLeft,
    (left.strong, right.strong): theta.noTurn,
    (left.strong, right.veryWeak): theta.mediumRight,
    (left.strong, right.weak): theta.mediumRight,
    (left.strong, right.medium): theta.smallRight,
    (left.medium, right.veryStrong): theta.smallLeft,
    (left.medium, right.strong): theta.smallLeft,
    (left.medium, right.medium): theta.noTurn,
    (left.medium, right.weak): theta.smallRight,
    (left.medium, right.veryWeak): theta.smallRight,
    (left.weak, right.veryStrong): theta.mediumLeft,
    (left.weak, right.strong): theta.mediumLeft,
    (left.weak, right.medium): theta.smallLeft,
    (left.weak, right.weak): theta.noTurn,
    (left.weak, right.veryWeak): theta.smallRight,
    (left.veryWeak, right.veryStrong): theta.mediumLeft,
    (left.veryWeak, right.strong): theta.mediumLeft,
    (left.veryWeak, right.medium): theta.smallLeft,
    (left.veryWeak, right.weak): theta.smallLeft,
    (left.veryWeak, right.veryWeak): theta.noTurn,
})


def fuzzyObjectAvoidance(leftDist, rightDist):
    values = {left: leftDist, right: rightDist}
    return rules(values)


def main():
    theta.mediumRight.plot()
    theta.smallRight.plot()
    theta.noTurn.plot()
    theta.smallLeft.plot()
    theta.mediumLeft.plot()

    plt.show()

    print(fuzzyObjectAvoidance(100, 100))


if __name__ == "__main__":
    main()
