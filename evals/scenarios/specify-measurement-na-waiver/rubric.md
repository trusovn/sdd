# Rubric — specify measurement N/A waiver (walking skeleton)

PASS requires ALL of:

1. `docs/features/order-pipeline-walking-skeleton/spec.md` exists and contains the eight spec
   sections §1–§8 (numbered headings or clearly equivalent), with §6 and §7 present rather than
   deleted.
2. The measurement waiver is explicit and sourced: §6 and/or §7 contains a literal
   `Measurement: N/A` line (or clearly equivalent) naming the walking-skeleton reason AND citing
   an upstream source (the captured idea / §1 committed approach / §3 non-goal) for it. An empty
   or template-placeholder §6/§7 with no waiver line fails.
3. The waiver is revisitable: §8 carries an open question (checkbox line with owner + due or a
   trigger like "before the first real traffic") that re-opens performance targets / outcome
   measurement. A waiver with no revisit fails.
4. No fabricated numbers: §6 carries no invented latency/throughput/availability targets for the
   waived aspects, and §7 contains no vanity KPI rows (e.g. "number of orders processed" with no
   decision) invented to fill the table. Aspects the walking-skeleton reason does NOT make
   meaningless (accuracy, durability, error handling in §5 AC) are still present.
5. The final handoff block lists `docs/features/order-pipeline-walking-skeleton/spec.md` and
   names §6/§7 (or the measurement waiver) as something to review before continuing.

FAIL if §6/§7 silently disappear or hold placeholder rows, if the waiver exists but cites no
source, if there is no revisit question, or if vanity metrics fill the gap the waiver should
have left.