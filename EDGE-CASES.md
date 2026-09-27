---
lab2_edge_cases:
  E1: {count: 3, rule: R-08}
  E2: {count: 2, rule: R-06}
  E3: {count: 4, rule: R-09}
  E4: {count: 4, rule: R-10}
  E5: {count: 1, rule: R-12}
  E6: {count: 11, rule: R-13}
---
<!-- ai-generated: 30% - structure from template, explanations written by student -->

## E1: Clock skew produces negative lead time

- What the log contains: Three commit-deployment pairs where the commit timestamp is after the deployment timestamp due to clock skew between machines, producing negative raw lead times.
- What a default definition would have done: A naive implementation would discard pairs with negative lead time or raise an error, silently losing those pairs from the median calculation.
- Why the rule is defensible: Clamping to zero and counting preserves the full set of pairs for the median, ensuring clock skew does not silently distort throughput measurements.

## E2: Revert of a revert resolves to the original change

- What the log contains: Two commits whose reverts field points to another revert commit, forming a chain that collapses transitively back to the original change_id under R-06.
- What a default definition would have done: A model would typically treat each revert commit as its own change or ignore it entirely, inflating or deflating the distinct change count.
- Why the rule is defensible: Transitive resolution ensures that undoing an undo is attributed to the original work, keeping the change count accurate and preventing gaming through revert chains.

## E3: Hotfix deployed straight to production never on main

- What the log contains: Four commit shas carried by production deployments whose branch field is not main, representing hotfixes deployed directly without going through the main branch.
- What a default definition would have done: A model typically filters commits by branch equals main, which would exclude these hotfix commits from lead time pairs entirely.
- Why the rule is defensible: Ignoring the branch field ensures all work that actually reached production is measured, including the most urgent and risky hotfix deliveries.

## E4: Production deployment with no linked commits

- What the log contains: Four production deployments with an empty commits list, contributing to deployment frequency and fail rate denominators but producing no lead-time pairs.
- What a default definition would have done: A model might skip empty-commit deployments entirely from all counts, reducing the denominator for change fail rate and distorting the frequency metric.
- Why the rule is defensible: Counting empty deployments preserves the true picture of deployment cadence and failure rate, including infrastructure-only and configuration releases.

## E5: Failed deployment that never recovered

- What the log contains: One failed deployment whose covering incident has no resolved event, making it an open failure with no computable recovery time.
- What a default definition would have done: A model might invent a recovery time using the window end timestamp or include the open failure in the median with a synthetic value.
- Why the rule is defensible: Excluding open failures from the median and counting them separately gives an honest picture of unresolved incidents without fabricating data.

## E6: Overlapping incident intervals

- What the log contains: Eleven pairs of distinct incidents whose time intervals overlap, each independently covering their own set of failed deployments.
- What a default definition would have done: A model might merge overlapping incidents or sum their durations, computing one combined recovery time instead of independent per-deployment recovery.
- Why the rule is defensible: Computing recovery per failed deployment rather than per incident ensures that one incident covering two failures gives both deployments the same honest recovery instant.

## Gaming demonstration

I improved change_fail_rate by exploiting R-14, which divides failed deployments by total deployments. By adding eleven successful deployments with empty commits to gaming/after.jsonl, the total deployment count increases while the number of failures stays the same, pushing the fail rate below the baseline by more than 0.02 absolute. A real team would be incentivised to add empty deployments before reporting periods to dilute their failure rate. R-21 catches this because the ground truth changes_delivered stays the same while true_change_lead_time increases as the same real work is now spread across more deployments.
