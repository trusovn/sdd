<!-- Template for `plan-tests`. -->
<!-- M+: write to docs/features/<slug>/test-plan.md (this whole file). -->
<!-- XS/S: paste the AC + edge-case blocks inline into spec.md under `## Test plan`; include -->
<!--       risk, measurement, and linkage blocks only when source artifacts justify rows. -->
<!-- The plan is written BEFORE tests exist; `implement` reads the AC map and open linkage rows. -->
<!-- Stay STACK-AGNOSTIC: name test LEVELS, never a runner / broker / -->
<!-- load tool. The real commands are detected by `implement` against the repo, not fixed here. -->
<!-- Risk and measurement rows are source-driven additions, not a generic governance checklist. -->

---
status: Draft
owner: "<QA owner>"
reviewers: ["<implementing engineer>", "<Tech Lead>"]
updated_at: "<YYYY-MM-DD>"
feature_size: "<XS|S|M|L|XL>"
---

# Test plan — <feature>

<!-- One-line restatement of what this feature must do, so the coverage below has a frame. -->

## Levels

<!-- The only allowed levels — generic, no tool names. Drop a row that doesn't apply to this -->
<!-- feature; mark it <!-- N/A: reason -->  rather than padding it. `implement` picks the actual -->
<!-- runner/tool for each level from what the repo already uses. -->
<!-- The Component / Visual-regression / E2E-through-UI rows apply ONLY when sad.md frontmatter -->
<!-- target_surfaces declares a UI surface (web-frontend / mobile-app / desktop-app) — the -->
<!-- "testing trophy" vocabulary (_shared/surfaces.md). Drop them for a backend-only feature. -->

| Level | Scope | Strategy (generic — no tool names) |
|---|---|---|
| Unit | Pure logic: a rule, a calculation, a validator — no I/O. | In-memory, no external dependency. |
| Integration | The module against a real dependency it owns (store / cache / queue). | An ephemeral real dependency, e.g. a throwaway DB container spun up per suite. |
| Contract | A boundary between two participants — an API shape or event schema both sides agree on. | Validate the real shape against the agreed contract; no hand-rolled stubs. |
| E2E | One full flow end to end (one per critical user story). | The flow exercised through its real entry point against ephemeral dependencies. |
| Load | NFR validation — only when an NFR carries a number. | The load tool already in your repo, or e.g. k6 or Locust. |
| Component *(UI surface only)* | A UI component exercised in isolation — props/state → rendered output + interactions. | Render in a component harness; assert output + behaviour, no full app boot. |
| Visual-regression *(web UI only)* | The rendered UI diffed against an approved baseline image. | Snapshot the render; fail on an unintended visual diff; update the baseline deliberately. |
| E2E-through-UI *(UI surface only)* | A user-story flow driven through the real UI, not just the API. | The flow exercised through the rendered UI against ephemeral dependencies. |

## AC coverage

<!-- THE CORE OF THIS PLAN: every acceptance criterion in spec.md §5 → at least one test row. -->
<!-- One AC may fan out to several rows (a unit test for the rule + an e2e test for the flow). -->
<!-- Zero uncovered ACs allowed. Name the test from the AC's intent, not a framework convention. -->
<!-- Expected outcome in plain words — NO status numbers, NO error-code strings, NO SQL. -->

| AC (spec.md §5) | Test name (intent-based) | Level | Expected outcome |
|---|---|---|---|
| AC-01 <happy path> | <e.g. request within limit is served> | unit + e2e | <served normally> |
| AC-02 <error path> | <e.g. request over limit is rejected> | unit + e2e | <rejected, caller told the limit was hit> |
| AC-03 <authorization> | <e.g. caller without rights is refused> | integration | <refused, action not performed> |
| AC-04 <domain invariant> | <e.g. invariant holds after the operation> | integration | <invariant still true> |

## Edge cases / error paths

<!-- Each error / authorization AC gets its OWN dedicated row — never folded into a happy path. -->
<!-- Add the boundary & failure cases the spec implies. Outcome named in plain words. -->

- <missing required identifier> → expected: <named outcome>
- <malformed input> → expected: <named outcome>
- <dependency unavailable> → expected: <the spec's fallback behaviour, e.g. fail-open / fail-closed>

## Risk coverage

<!-- Source each row from discovery.md §§7–9, sad.md §11, spec.md §6.1, or another named risk -->
<!-- source. Every retained High/Medium risk needs concrete verification/monitoring OR an explicit -->
<!-- not-test-covered rationale with residual-risk owner and review timing. -->

| Check ID | Source | Risk / failure mode | Severity | Verification / monitoring activity | Pass or decision condition | Owner / timing |
|---|---|---|---|---|---|---|
| RISK-01 | discovery.md §9 | <risk> | High | <test, gate, release check, or rollout monitoring> | <evidence/threshold that closes or escalates it> | <owner + when reviewed> |
| RISK-02 | sad.md §11 | <risk not test-covered> | Medium | not test-covered: <rationale and residual-risk handling> | <accept/revisit/stop condition> | <owner + review gate/date> |

<!-- If no source justifies rows: -->
<!-- N/A: no retained High/Medium risk requiring additional verification. -->

## Measurement readiness

<!-- Every important spec.md §7 KPI appears here. Pre-release proves the signal can be collected; -->
<!-- post-release evaluates the product outcome. Do not claim the latter from instrumentation alone. -->
<!-- If §7 carries the sourced measurement N/A waiver: mirror it — -->
<!-- N/A: measurement waived at spec — <reason> (source: <spec §ref>); revisit OQ §8 carries owner + due. -->
<!-- Never fabricate MEAS rows for a waived §7. -->

| Check ID | Metric | Source/event | Baseline plan | Target/timebox | Decision threshold | Pre-release readiness check | Post-release outcome review | Owner / review timing |
|---|---|---|---|---|---|---|---|---|
| MEAS-01 | <metric> | <event/log/report/manual source> | <known value or concrete establishment plan> | <target + timebox> | <ship/continue/iterate/rollback/stop/investigate trigger> | <prove the source emits or report/sample can be produced> | <when outcome is evaluated and what decision follows> | <owner + date/cadence> |
| MEAS-02 | <discovery.md §10 seed> | <possible source> | <baseline status> | seed deferred | <decision it may inform> | <prerequisite before adoption> | <revisit trigger> | <owner + revisit point> |

## Implementation linkage

<!-- One row per RISK-NN / MEAS-NN. Use an existing tasks.json id when useful. An executable -->
<!-- pre-release check with no owner task is `unassigned — update/split tasks before implement`. -->
<!-- Non-test work remains explicit as release/monitoring/residual-risk evidence. -->

| Check ID | Source row | Task link | Closure activity | Evidence required | Owner / timing | Status |
|---|---|---|---|---|---|---|
| RISK-01 | <risk row> | T<n> | <RED test / automated gate / release-readiness check> | <path/run/report proving the pass condition> | <owner + timing> | open |
| RISK-02 | <risk row> | <release owner> | residual-risk decision | <recorded decision + revisit condition> | <owner + timing> | open |
| MEAS-01 | <KPI row> | T<n> | <release-readiness check / rollout monitoring> | <pre-release signal proof + post-release review path> | <owner + timing> | open |
| MEAS-02 | <seed row> | <owner> | deferred measurement seed | <reason + revisit trigger> | <owner + timing> | open |

## Test data

<!-- How test data is built and torn down. Seed = factories/fixtures for the entity shape -->
<!-- (read data-model.md if present). Cleanup boundary matters: no cleanup → flaky suite → CI block. -->

- Seed strategy: <factories / fixtures matching data-model.md entities>.
- Integration dependency: an ephemeral real dependency (throwaway container), NOT a mocked store.
- Cleanup boundary: <per-test | per-suite> — reset state so runs are independent.

## NFR validation (load)

<!-- One scenario per NUMERIC NFR from spec.md §6. If no NFR carries a number → N/A, do NOT invent one. -->
<!-- Tool stays generic: the load tool already in your repo, or e.g. k6 / Locust. -->

- <NFR: p95 latency ≤ N ms> → scenario: <target rate> for <duration>, assert <metric> ≤ <threshold>.
- <NFR: throughput ≥ N req/s> → scenario: sustain <rate> for <duration>, assert no error-rate regression.

<!-- If spec.md §6 has no numeric NFR: -->
<!-- N/A: no numeric NFR to load-test. -->

## CI placement

<!-- Advice, not pipeline config — `implement` and the repo's CI own the real wiring. -->

- On every PR: <unit, contract — the fast suites>.
- On schedule / pre-release: <e2e, load — the heavier suites>.
- Release gate: <risk and measurement-readiness checks justified above>.
- Post-release: <outcome reviews and rollout monitoring tied to decision thresholds>.
