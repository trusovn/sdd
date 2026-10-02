# Rubric — specify product measurement plan

PASS requires ALL of:

1. `docs/features/onboarding-dropoff-insights/spec.md` exists and contains the eight spec sections
   §1–§8, or clearly equivalent headings.
2. `spec.md` §7 is a product-measurement table, not a loose KPI bullet list. The table has columns
   equivalent to: Metric, Why it matters, Source/event, Baseline, Target/timebox, Decision
   threshold, Owner, and When reviewed.
3. §7 contains at least three metric rows. Each row names an observable source/event or review
   source, a baseline or baseline-establishment plan, a target with a timebox, an owner, and review
   timing. Empty placeholders such as `<...>`, unowned `TBD`, or "monitor it" do not count.
4. Each §7 row has a real decision threshold: it says what the team will do after the timebox
   (for example ship, continue, iterate, rollback, stop, or investigate). A threshold that only
   says "track", "monitor", or "review" without a decision rule fails.
5. If a baseline is unknown, §7 names how it will be established and §8 carries the owner and due
   point for that baseline question.
6. The final handoff block lists `docs/features/onboarding-dropoff-insights/spec.md` and calls out
   the measurement plan or §7 as something to review before continuing.

FAIL if §7 is prose-only, if KPI rows lack source/event or decision thresholds, if ownership or
review timing is missing, or if the final message treats measurement as a post-release
afterthought.
