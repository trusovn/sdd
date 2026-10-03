---
name: plan-tests
model: inherit
effort: medium
agents: []
description: >
  Use to turn a feature's acceptance criteria into a test plan before any test is written — a
  table that maps every spec.md §5 acceptance criterion to at least one test, names the test
  levels (unit / integration / e2e / contract / load) without binding to a language or
  framework, and fixes the integration and data strategy. Triggers on "plan tests for {slug}",
  "test plan for {slug}", "how do we test {slug}", "test strategy for {slug}",
  "/sdd:plan-tests {slug}", "план тестів для {slug}", "як тестувати {slug}", "тест-план".
  Output: docs/features/{slug}/test-plan.md (separate file for M+), or inline in spec.md for
  XS/S per the size matrix. Also traces retained risks and KPI measurement readiness into
  implementation/release checks. Hard-refuse if spec.md is missing → run `specify {slug}` first.
---

# Skill: plan-tests

Turns an already-specified feature into a **test plan**: a table that ties every acceptance criterion in `spec.md §5` to at least one named test, the levels those tests live at (unit / integration / e2e / contract / load), the integration strategy (a real dependency, spun up throwaway), and the test-data + cleanup approach. It also keeps important risks and KPI promises alive as concrete verification, release, or monitoring work. The plan is written *before* a single test exists — the next stage, `implement`, reads this map and writes the red tests and linked checks against it, not "however it seems". This file is the spine; the output scaffold lives in `templates/test-plan.md`.

This skill keeps only its own machinery. Question phrasing is **shared** → [`../_shared/ask-style.md`](../_shared/ask-style.md). Depth (inline in the spec vs a separate file) follows the **size matrix** → [`../_shared/size-matrix.md`](../_shared/size-matrix.md). It names test *levels*, never test *tools* — the concrete commands are detected by `implement` against the repo, not hard-coded here.

Plan prose follows `artifact_language` — the `## Test plan` heading (parsed downstream), test names and level tokens stay English → [`../_shared/artifact-language.md`](../_shared/artifact-language.md).

## Owner

QA + the engineer who will implement the feature (co-authors). QA drives the level breakdown and the edge/error cases; the implementing engineer confirms each acceptance criterion has a reachable test and that the integration strategy fits the repo. The Tech Lead signs off that no acceptance criterion is left uncovered.

## Inputs

- `<slug>` — the same feature slug every earlier stage used.
- **Gate (hard-refuse if missing):** `docs/features/<slug>/spec.md`. Its §5 acceptance criteria are the entire reason this plan exists — each one must map to a test. If `spec.md` is absent → STOP and point: «run `specify <slug>` first — the test plan maps its §5 acceptance criteria to tests».
- (Optional) `docs/features/<slug>/discovery.md` — read §§7–10 if present: edge cases, failure modes, retained risks, and measurement seeds.
- (Optional) `docs/features/<slug>/tasks.json` — read if present so executable risk/measurement checks can point to existing implementation tasks. Do not invent or silently rewrite the DAG here.
- (Optional) `docs/features/<slug>/data-model.md` — the entity shapes tell you what test data to build and what to seed/clean per suite. Read it if present.
- (Optional) `docs/features/<slug>/sad.md` §6 sequence diagrams and §11 risks / technical debt — each drawn flow is an e2e candidate; each cross-participant boundary is a contract-test candidate; each retained High/Medium risk is a risk-coverage candidate.
- (Optional) `docs/features/<slug>/.size` — depth hint. Absent → default to M (separate `test-plan.md` file) **and say so loudly in the handoff** — «size M (default — no `.size`; run `/sdd:classify-size <slug>`)».

## Protocol

1. **Gate.** `test -f docs/features/<slug>/spec.md` → fail = refuse with the pointer above. Then read §5 (acceptance criteria), §6 (NFRs), §6.1 (security/privacy/abuse cases), and §7 (KPIs). Read `discovery.md` §§7–10, `tasks.json`, `data-model.md`, and `sad.md` §6 + §11 when present.
2. **Pick the output target.** Per the size matrix: **XS/S → write the plan inline in `spec.md`** as a short `## Test plan` section (AC coverage + edge cases, plus risk/measurement/linkage rows when source artifacts justify them — no separate file); **M+ → a separate `docs/features/<slug>/test-plan.md`** from the template. Confirm the target with one `AskUserQuestion` (phrasing per [`../_shared/ask-style.md`](../_shared/ask-style.md)) when `.size` is absent.
3. **Map levels — generic only.** Name test levels from a fixed vocabulary, never a tool or language: **unit** (pure logic — a rule, a calculation, a validator, no I/O), **integration** (the module against a real dependency it owns — DB, cache, queue), **e2e** (a full flow end to end, one per critical user story), **contract** (a boundary between two participants — an API shape or an event schema agreed by both sides), **load** (only when an NFR carries a number — throughput, p95 latency). **When `sad.md` frontmatter `target_surfaces` declares a UI surface** (`web-frontend` / `mobile-app` / `desktop-app`), add the frontend tiers — **component** (a UI component exercised in isolation), **visual-regression** (web — the rendered UI diffed against a baseline), **e2e-through-UI** (the flow driven through the real UI, not just the API). These are the **"testing trophy"**, the dominant frontend testing vocabulary (web.dev / Kent C. Dodds) — a vocabulary, not a mandate (→ [`../_shared/surfaces.md`](../_shared/surfaces.md)). When the design pipeline ran, source the UI rows from its artifacts: the **e2e-through-UI path comes from `ux-flows.md`** (the flow is the test's script, and a resolved `UXD-NN` interaction decision is asserted as the flow's expected behavior — e.g. «creation does not auto-open the next step» — never re-derived). **When deriving e2e-through-UI paths, preserve resolved interaction behavior — do not extend the UX flow with "logical next steps" that are absent or explicitly excluded.** (A relevant e2e path may verify: *create Project → successful save → Project context visible → Environment creation is not automatically opened* — but only when that behavior matters to the corresponding AC/test scope; do not turn every `UXD-NN` row automatically into a standalone test.) The **states a component test must cover come from `screens.md`** (the manifest's state rows). Do not write tool names (no specific test runner, broker, visual-regression, or load tool) — `implement` detects what the repo already uses (e.g. Playwright / Storybook / a visual-diff tool).
4. **Core mapping (the contract of this skill) — user chooses the level per AC.** Build the AC→test table: **every acceptance criterion in §5 maps to ≥1 test.** For each AC, **propose a default level** from a heuristic (pure logic/rule/validator → unit; behaviour against a real dependency the module owns → integration; a full user-story flow → e2e; a cross-participant API/event shape → contract; and — when a UI surface is declared — a UI piece → component, a user-facing flow → e2e-through-UI), then **confirm the level(s) with the user** via one `AskUserQuestion` (multiSelect — an AC may fan out to several levels, e.g. unit for the rule + e2e for the flow), phrased per [`../_shared/ask-style.md`](../_shared/ask-style.md). The user's choice is authoritative and is recorded in the table's Level column; `implement` reads it to write the test at the right level (it does not re-decide). A criterion with zero tests is the cardinal anti-pattern. Name each test descriptively from the criterion's intent (e.g. `over-quota request is rejected`), not from any framework convention.
5. **Edge cases & error paths.** Every error/authorization acceptance criterion gets its own dedicated test row — never folded into the happy path. List the boundary and failure cases the spec implies (missing identifier, malformed input, dependency unavailable → the spec's fallback behaviour) as explicit rows with their expected outcome named in plain words (no status numbers, no error-code strings).
6. **Integration strategy — real, ephemeral dependency.** For integration tests, the default is **an ephemeral real dependency, e.g. a throwaway DB container** spun up for the suite and torn down after (testcontainers-style). Mocking the datastore is an anti-pattern — a passing mock is not a passing production. State the seed strategy (factories/fixtures for the data shape) and the cleanup boundary (per-test vs per-suite); without cleanup the suite goes flaky and blocks CI.
7. **Risk coverage — source-driven only.** Build `Risk coverage` from retained High/Medium risks in `discovery.md §9`, `sad.md §11`, explicit `spec.md §6.1` security/privacy/abuse cases, and other clearly identified risk sources. Every such risk gets either (a) a stable `RISK-NN` row naming a concrete test, automated gate, release-readiness check, or rollout-monitoring activity and its pass/decision condition; or (b) an explicit `not test-covered` rationale with residual-risk owner and review timing. Low risks appear only when their handling needs verification. Do not create a generic security/observability/accessibility checklist.
8. **Measurement readiness — do not confuse signal with outcome.** For every important `spec.md §7` KPI, add a stable `MEAS-NN` row carrying metric, source/event, baseline plan, target/timebox, decision threshold, owner, and review timing. Separate the **pre-release readiness check** (the event/report/manual sample can actually be produced) from the **post-release outcome review** (the KPI reaches its target and drives the named decision). A working event is not proof of a future product outcome. Map each `discovery.md §10` seed to a KPI or record `seed deferred` with owner and revisit trigger. **Waived §7 (the sourced `Measurement: N/A` line):** do not fabricate MEAS rows — mirror the waiver with `<!-- N/A: measurement waived at spec — <reason> (source: <spec §ref>) → revisit OQ §8 -->` and, if the revisit point lands before/around release, one linkage row carrying the revisit OQ to its owner. An unsourced waiver or a missing revisit OQ is a hole upstream — surface it (Save-as-OQ with `specify` as owner), never paper over it.
9. **Implementation linkage.** Add one linkage row for every `RISK-NN` / `MEAS-NN`: source row, existing `tasks.json` task id when useful, closure activity, required evidence, owner/timing, and `open` status. Use the cleanest activity for the row (for example RED test, automated gate, release-readiness check, rollout monitoring, residual-risk decision, or deferred measurement seed); do not force every row into a test. If `tasks.json` exists but no task owns an executable pre-release check, write `unassigned — update/split tasks before implement`. If it is absent, write `assign before implement`.
10. **NFR → load.** For each §6 NFR that carries a number, write one concrete load scenario (target rate, duration, the metric and its threshold) and name the tool generically: **the load tool already in your repo, or e.g. k6 or Locust**. If no NFR carries a number, mark the load section `<!-- N/A: no numeric NFR -->` — do not invent a load test.
11. **CI/release placement.** Note which suites run where: fast suites (unit, contract) on every PR; heavier suites (e2e, load) on a schedule or pre-release; release-readiness checks at the release gate; outcome measurement after deployment. The split is advice, not pipeline config.
12. **Socratic walk + write.** Walk the AC, risk, measurement, and linkage rows plus strategy choices with the 4-state actions from [`../_shared/ask-style.md`](../_shared/ask-style.md) (Accept / Fix / Save-as-OQ / Drop); on Fix, regenerate that one row (one round, second answer final). Maintain the edits-log per [`../_shared/socratic-loop.md`](../_shared/socratic-loop.md). On pass, write the plan to its target.
13. **Structural self-check** — per [`../_shared/self-check.md`](../_shared/self-check.md): re-read the written plan from disk and verify **9 items**: (1) every `spec.md` §5 AC id appears in the coverage table; (2) every error/authorization AC has its own row; (3) every AC Level value is in the fixed vocabulary; (4) zero tool names outside the allowed load example; (5) load rows carry numbers or the literal N/A marker; (6) every retained High/Medium risk has verification/monitoring or an owner-backed not-covered rationale; (7) every important §7 KPI has both pre-release readiness and post-release outcome handling plus all KPI contract fields — or the spec's sourced measurement N/A is mirrored with its revisit accounted for; (8) every `RISK-NN` / `MEAS-NN` has an implementation-linkage row, and executable pre-release rows have a task or explicit unassigned blocker; (9) the plan sits at its size-correct target. Fix + re-check ≤2 cycles; surface anything unresolved.
14. **Propose commit + handoff.** `test-plan: <slug>`. Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) — *What I did* (incl. «self-check: 9/9 pass») + *Review* (`test-plan.md`, or `spec.md` `## Test plan` for XS/S) + *Run next* (`/clear`, then `/sdd:implement <slug>`, which consumes the AC map and open linkage rows).

## Definition of Done

- The plan exists at its size-correct target: a separate `docs/features/<slug>/test-plan.md` for M+, or an inline `## Test plan` section in `spec.md` for XS/S.
- **Every acceptance criterion in spec.md §5 maps to ≥1 named test** — zero uncovered criteria.
- Each error / authorization criterion has its own dedicated test row, not folded into a happy path.
- Test levels are generic (unit / integration / e2e / contract / load; + component / visual-regression / e2e-through-UI when a UI surface is declared in `target_surfaces`) — **no test-runner, broker, visual-regression, or load-tool name is hard-coded** (the load tool is named only as "the one in your repo, or e.g. k6 / Locust"; UI tools are detected by `implement`).
- Integration tests use an ephemeral real dependency (throwaway container), with the seed and cleanup boundary stated; no mocked datastore.
- Every numeric §6 NFR has a load scenario (rate + duration + metric + threshold), or the load section is explicitly `<!-- N/A -->`.
- Every retained High/Medium risk has a concrete verification/monitoring activity or an explicit owner-backed residual-risk rationale.
- Every important KPI has pre-release signal-readiness evidence and a distinct post-release outcome review carrying the full §7 decision contract — or the spec's sourced measurement N/A is mirrored verbatim with the §8 revisit accounted for.
- Every risk/measurement row reaches implementation through a task-linked or explicitly unassigned linkage row; executable gaps block rather than disappear.

## Anti-patterns

- **An acceptance criterion with no test.** The whole point of the map is that §5 is verifiable; an uncovered criterion means it isn't.
- **Naming a concrete tool or language** — a specific runner, broker, or load tool. The legacy plan hard-coded **k6**; here load is "the tool already in your repo, or e.g. k6 / Locust", and the rest stay generic levels. `implement` detects the real commands.
- **Mocking the datastore.** A passing mock is not a passing production — use a throwaway real dependency for integration.
- **e2e without a cleanup boundary.** Leftover state makes the suite flaky and every flaky run blocks CI.
- **Extending the UX flow with "logical next steps"** the resolved flow doesn't contain — an
  e2e-through-UI path that invents an automatic continuation (or erases a resolved `UXD-NN`
  exclusion) silently rewrites user behavior; assert what ux-flows resolved, and only where the
  AC/test scope makes it matter.
- **"100 % coverage" as the goal.** The target is critical paths + happy + error paths mapped to acceptance criteria, not a line-count number.
- **A wishlist plan** — "would be nice to add". A test plan is a commitment the next stage executes, not a backlog.
- **Inventing a load test with no numeric NFR.** No number → `<!-- N/A -->`, not a fabricated throughput target.
- **A generic governance checklist.** Add a risk/measurement row only when a source artifact justifies it.
- **Instrumentation equals success.** Proving an event emits before release does not prove a post-release KPI target was met.
- **An unlinked promise.** A risk or KPI row without an implementation/release owner will disappear after planning.

## References & template

- [`../_shared/ask-style.md`](../_shared/ask-style.md) — canonical question/option phrasing for steps 2 and 9.
- [`../_shared/self-check.md`](../_shared/self-check.md) — the structural self-check contract step 13 runs.
- [`../_shared/size-matrix.md`](../_shared/size-matrix.md) — inline-in-spec (XS/S) vs separate file (M+) depth.
- [`../_shared/surfaces.md`](../_shared/surfaces.md) — a declared UI surface adds the component / visual-regression / e2e-through-UI tiers (testing-trophy vocabulary); read from `sad.md` `target_surfaces`.
- [`./templates/test-plan.md`](./templates/test-plan.md) — output scaffold: AC mapping, risk coverage, measurement readiness, implementation linkage, integration strategy, and load section. Its `<!-- … -->` comments are the per-section contract.
