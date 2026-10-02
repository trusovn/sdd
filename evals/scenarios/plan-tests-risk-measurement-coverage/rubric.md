# Rubric — plan-tests risk and measurement continuity

The fixture is a medium feature with specification, discovery, architecture risks, and an existing
task DAG. PASS requires ALL of:

1. `docs/features/invoice-approval-guardrails/test-plan.md` exists as a separate file.
2. AC coverage maps `AC-01` through `AC-05`; error, authorization, invariant, and cross-context
   cases have dedicated rows.
3. `Risk coverage` traces every retained High/Medium source risk: stale vendor-compliance state,
   missing denied-release audit evidence, approval/compliance disagreement, eventual audit-event
   consistency, and the explicit authorization/audit-tampering cases. Each has concrete
   verification/monitoring or an owner-backed not-test-covered rationale; no generic checklist.
4. `Measurement readiness` covers all three §7 KPIs with source/event, baseline plan,
   target/timebox, decision threshold, owner, and review timing. Each row distinguishes a
   pre-release signal/readiness check from post-release outcome evaluation; it does not claim an
   event emitting proves a future target was met.
5. Every `RISK-NN` and `MEAS-NN` has an `Implementation linkage` row. Executable checks point to a
   plausible existing task (`T1`–`T3`); rollout monitoring/residual-risk work names an owner and
   timing. Nothing silently rewrites `tasks.json`.
6. Test levels remain generic, and the final handoff reports `self-check: 9/9 pass`, lists
   `test-plan.md`, and names `/sdd:implement invoice-approval-guardrails` next.

FAIL if a High/Medium risk or KPI disappears, measurement instrumentation is presented as a
pre-release product outcome, linkage is absent, or untraceable generic governance rows are added.
