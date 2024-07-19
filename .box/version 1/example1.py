from base import Domain, Rule
import fuzzyfication as fuzzy


# http://petro.tanrei.ca/fuzzylogic/fuzzy_negnevistky.html

# the stuff a system architect needs to write
funding = Domain("project_funding", (0, 100))
funding.inadequate = fuzzy.linear(30, 20)
funding.marginal = fuzzy.triangular(20, 80)
funding.adequate = fuzzy.linear(60, 80)

staffing = Domain("project_staffing", (0, 100))
staffing.small = fuzzy.linear(60, 30)
staffing.large = fuzzy.linear(40, 60)


risk = Domain("project_risk", (0, 100))
risk.low = fuzzy.linear(40, 20)
risk.normal = fuzzy.triangular(20, 80)
risk.high = fuzzy.linear(60, 80)

staffing.plot()

funding(25)
staffing(55)


# the stuff a user needs to write
# max(project_funding.adequat(25), project_staffing.small(55)),
Rule("project_funding.adequate or project_staffing.small", "risk.low")
Rule("project_funding.marginal and project_staffing.large", "risk.normal")
Rule("project_funding.inadequate", "risk.high")

# the system evaluates concrete values
