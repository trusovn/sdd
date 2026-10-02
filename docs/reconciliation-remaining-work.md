# Reconciliation — Remaining Work

Branch: `reconcile/upstream-v2.3`

Upstream base: `44039133714bea939e5cdfc86671a901b3b01ef0` (`v2.3.0`)

Current reconciliation tip at review time: `e0aaea4b5b0642d583964f279f4abd5a77fe0494`

The semantic reconciliation itself is complete enough to keep. Do not reopen the already-ported domain-discovery, KPI, risk/measurement, survey-authority, or non-Claude decisions unless a regression proves they are wrong.

This file tracks only the remaining closure work before replacing the fork's `main`.

## How to execute this document

The work is intentionally split into independently assignable work items. A prompt such as
`Do WI-1 from docs/reconciliation-remaining-work.md` means:

1. read this whole document and confirm the work item's prerequisites against the current branch;
2. perform only that work item's required changes and verification;
3. report changed files, exact verification results, and any residual risk;
4. do not start a later work item, push, or replace `main` unless that work item explicitly requires it.

If a prerequisite is missing, stop and report it instead of silently widening the item. If an item
uncovers a regression, fix it only when the fix is clearly inside that item's stated scope;
otherwise record it as follow-up work. Preserve the existing reconciliation decisions and the
explicitly out-of-scope list at the end of this document.

### Recommended session split

| Session | Work items | Purpose | Exit gate |
|---|---|---|---|
| 1 — closure implementation | `WI-1`, then `WI-2` | fix the remaining route behavior and make its reconciliation validators durable | both items pass their targeted deterministic checks; keep them as separate commits if committing is authorized |
| 2 — live behavior verification | `WI-3` | execute the authenticated, non-deterministic Claude scenarios and record real evidence | every required targeted scenario has an explicit PASS, or failures/deferred risk are recorded and `WI-6` remains blocked |
| 3 — finalization | `WI-5`, then `WI-4`, then `WI-6` | settle versioning, run final deterministic gates, audit the complete diff, and replace `main` | remote `main` points to the verified reconciliation tip and the archive branch preserves the old fork tip |

Do not combine session 2 with the final `main` replacement. Each behavior scenario makes one
agent run plus one judge call, can take minutes, costs tokens, and may fail non-deterministically.
The full suite currently means substantially more calls than the required targeted set. Run the
targeted set first and expand only when its results justify the extra cost.

## WI-1 — Fix the stale `plan-tests` skip rule

**Priority:** required before final merge

**Depends on:** none

**Scope boundary:** routing contracts, their directly related documentation/static invariant, and
one focused behavior regression. Do not revise the broader `plan-tests` artifact contract.

The upstream route logic still allows `plan-tests` to be skipped entirely when every task DoD already names its test. That condition predates the reconciliation.

After this port, `plan-tests` owns more than AC-to-test mapping. It also carries:

- retained risk coverage (`RISK-NN`);
- KPI measurement readiness (`MEAS-NN`);
- pre-release signal/instrumentation evidence;
- post-release outcome review obligations;
- implementation/release linkage for those checks.

Therefore "each task already names its test" is no longer sufficient to make `plan-tests` N/A.

### Required change

Update the routing contract so `plan-tests` is never fully skipped.

Preferred behavior:

- `quick` route: always run `plan-tests`, but keep its existing lightweight inline form in `spec.md`;
- `standard` route: run normally;
- `full` route: run normally.

Update all places that currently advertise or evaluate the old skip condition, especially:

- `skills/_shared/size-matrix.md`;
- `skills/tasks/SKILL.md` handoff logic;
- any validator text or documentation that encodes the old "every task DoD names its test" shortcut.

Do not make the quick path materially heavier than necessary. The goal is continuity of risk/KPI obligations, not more ceremony.

### Regression coverage

Add a focused routing scenario where:

- every task DoD already names a test;
- the spec contains at least one important KPI and/or retained risk;
- the route is `quick` or `standard`;
- the `tasks` handoff must still route through `plan-tests` rather than directly to `implement`.

The regression should verify observable routing behavior, not exact prose.

### WI-1 verification

Run the narrowest relevant validator/test for the changed routing contract, then run:

```bash
python3 scripts/validate_plugin.py
git diff --check
```

**Done when:** no route can hand off from `tasks` directly to `implement` by claiming that every
task DoD already names a test; `quick` still uses the lightweight inline plan; the focused routing
scenario exists and checks observable handoff behavior; deterministic checks pass.

**Suggested commit boundary:** `fix(routing): always route tasks through plan-tests`

## WI-2 — Reduce brittle prose assertions in `validate_plugin.py`

**Priority:** recommended before final merge

**Depends on:** `WI-1`, so the final routing invariant can be represented structurally.

**Scope boundary:** only the reconciliation-added domain-discovery, KPI, risk/measurement,
implementation-linkage, and `plan-tests` routing checks. Do not redesign the validator or weaken
unrelated pre-existing checks.

The reconciliation added useful static invariants, but some checks depend on exact wording or magic phrases in Markdown files.

Examples of brittle patterns include assertions for exact phrases such as:

- `any depth`;
- `not the competitive researcher`;
- `hard planning gap`;
- individual discovery-trigger wording;
- `monitor` as proof of decision-threshold semantics.

These can fail on harmless wording edits while still missing a semantically broken workflow that happens to retain the expected phrase.

### Keep as structural validator checks

Prefer deterministic checks for things such as:

- required files exist;
- `domain-investigator` is registered in the roster and `specify` agent list;
- discovery template sections/columns exist;
- KPI table columns exist;
- risk/measurement/linkage sections exist;
- `RISK-NN` / `MEAS-NN` identifiers are threaded into downstream contracts;
- focused eval fixtures/prompts/rubrics exist;
- references resolve;
- route/skill contracts name the required artifacts.

### Move semantic proof to behavior evals

Use live behavior scenarios to prove that:

- discovery really fires independently of the interview-depth ideation suite;
- competitive research and domain investigation remain separate;
- unknown research is represented honestly rather than fabricated;
- KPI rows carry actionable decision thresholds;
- risk/KPI obligations actually survive into planning and implementation.

Do not remove useful deterministic invariants merely to reduce the check count.

### WI-2 verification

For every removed magic-phrase assertion, identify the structural invariant or behavior scenario
that now owns the proof. Then run:

```bash
python3 scripts/validate_plugin.py
git diff --check
```

Review the diff specifically for accidental reductions in required file, section, identifier,
registration, reference-resolution, or artifact-linkage coverage.

**Done when:** harmless prose rewrites no longer break the reconciliation checks; deterministic
structure remains protected; semantic behavior is covered by an existing or focused eval rubric;
the validator passes.

**Suggested commit boundary:** `test(validate): make reconciliation invariants structural`

## WI-3 — Run the live behavior evals when Claude CLI authentication is available

**Priority:** required verification before final `main` replacement, unless consciously accepted as deferred risk

**Depends on:** `WI-1` and `WI-2` complete; usable authenticated Claude CLI; explicit approval for
the token/time cost of this live test class.

**Scope boundary:** execute and record behavior evidence. Do not reinterpret an authentication,
model, judge, or unparseable-result failure as a product PASS. If a product regression is found,
report the failing rubric evidence and fix only a small, clearly attributable defect; otherwise
stop and create a follow-up item rather than broadening this verification session.

The current local review could not execute the real Claude behavior scenarios because the local Claude CLI was not authenticated and rejected the injected model.

Structural validation and fixture/rubric review are not equivalent to executing the skills.

Once a usable Claude CLI session is available, run at minimum:

```bash
./evals/run.sh specify-unfamiliar-domain-discovery
./evals/run.sh specify-product-measurement-plan
./evals/run.sh plan-tests-risk-measurement-coverage
./evals/run.sh survey-authority-conflict
./evals/run.sh survey-missing-active-plan
./evals/run.sh survey-empty-cli-scaffold
```

Also run the new `plan-tests` routing regression from `WI-1`.

If practical, finish with:

```bash
./evals/run.sh
```

Record exact PASS/FAIL results. Do not convert a skipped live suite into a passing claim.

**Done when:** each required targeted scenario, including the `WI-1` routing regression, has a
recorded PASS. If the full suite is run, record every result separately. Any consciously deferred
or inconclusive result must be named as accepted risk and keeps `WI-6` blocked unless the person
authorizing the `main` replacement explicitly accepts it.

## WI-4 — Re-run deterministic validation after the remaining changes

**Priority:** required

**Depends on:** `WI-1` and `WI-2`; `WI-5` must also be complete first if it changes manifests.

**Scope boundary:** verification and evidence only. Fix only trivial issues directly caused by
`WI-1`, `WI-2`, or the version-marker update; route other failures back to the responsible item.

After `WI-1` and `WI-2` are implemented, run the existing deterministic checks again:

```bash
python3 scripts/validate_plugin.py
bash -n install.sh evals/run.sh
git diff --check upstream/main...HEAD
```

Repeat the Codex and Cursor installation smokes if the touched files can affect install-time skill/agent generation.

Confirm:

- validator passes;
- shell syntax passes;
- install smokes still produce the expected skills/agents;
- working tree is clean;
- local and remote branch tips match before final review.

**Done when:** every applicable command above passes at the final candidate tip, install smokes are
repeated if generation inputs or manifests changed, the working tree is clean, and the candidate
tip is pushed to `origin/reconcile/upstream-v2.3`.

## WI-5 — Decide the fork version/release marker

**Priority:** finalization decision, not a semantic blocker

**Depends on:** an explicit maintainer decision between the two conventions below. An agent must
not invent a fork version or silently leave the convention undocumented.

**Scope boundary:** make and apply only the version/release-marker decision. Do not combine it with
route, validator, or unrelated documentation changes.

The reconciled fork still inherits upstream's `2.3.0` version even though it now has additional behavior.

Before publishing the reconciled branch as the maintained fork `main`, decide whether to:

- keep upstream version numbers intentionally and identify fork changes only through Git history; or
- give the fork a distinct patch/suffix/release convention.

If a fork-specific version is chosen, update all manifests that must stay consistent in one focused commit and validate installer/manifests afterward.

Do not change the version merely to create churn; make the convention explicit and consistent.

**Done when:** the convention is explicitly recorded; if a fork-specific version is selected, all
required manifests agree and their targeted validation passes. If upstream numbering is retained,
record that this is intentional and make no version-only churn.

**Suggested commit boundary when files change:** `chore(release): set fork version convention`

## WI-6 — Final diff audit and `main` replacement

**Priority:** final step

**Depends on:** `WI-1` through `WI-5` complete. A deferred or inconclusive `WI-3` additionally
requires explicit maintainer acceptance before proceeding.

**Scope boundary:** final read-only audit followed by the deliberate remote branch updates. Do not
resolve newly discovered semantic problems inside this item; stop, report them, and return the work
to the responsible earlier item.

Before changing `main`:

1. compare the final reconciliation branch against `upstream/main`;
2. verify every remaining fork difference is intentional;
3. confirm `archive/pre-upstream-reconcile` still points to the original fork state (`d20649b`);
4. ensure live behavior eval results are recorded, or explicitly document why that risk is being accepted;
5. keep the current logical commit separation unless the final cleanup creates a clear reason to squash a purely documentary/audit commit.

Only after that should `main` be replaced with the reconciled history.

Use a guarded `--force-with-lease` against the observed old `origin/main` tip rather than an
unguarded force-push. Push `archive/pre-upstream-reconcile` first if it does not already exist on
the remote. After replacement, fetch and verify the exact remote `main` commit; do not rely only on
the push command's exit status.

**Done when:** the final intentional diff is approved, the archive branch exists remotely at
`d20649b`, `origin/main` points to the verified reconciliation candidate, the local `main` can be
synchronized to it, and the reconciliation branch remains available until the replacement is
confirmed.

## Explicitly out of scope

Do not reopen or re-port the following without concrete evidence of a regression:

- old universal `sdd-*` source renaming;
- old Ollama-specific eval shell handling;
- the removed dashboard/start flow;
- the old direct greenfield `implement` bootstrap;
- upstream functionality already covered by Codex/Cursor adapters and installers;
- broader governance/checklist machinery beyond source-driven risks and measurements;
- unrelated upstream cleanup or formatting.

The remaining work should stay small and closure-focused.
