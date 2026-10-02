# Reconciliation — Remaining Work

Branch: `reconcile/upstream-v2.3`

Upstream base: `44039133714bea939e5cdfc86671a901b3b01ef0` (`v2.3.0`)

Current reconciliation tip at review time: `e0aaea4b5b0642d583964f279f4abd5a77fe0494`

The semantic reconciliation itself is complete enough to keep. Do not reopen the already-ported domain-discovery, KPI, risk/measurement, survey-authority, or non-Claude decisions unless a regression proves they are wrong.

This file tracks only the remaining closure work before replacing the fork's `main`.

## 1. Fix the stale `plan-tests` skip rule

**Priority:** required before final merge

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

## 2. Reduce brittle prose assertions in `validate_plugin.py`

**Priority:** recommended before final merge

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

## 3. Run the live behavior evals when Claude CLI authentication is available

**Priority:** required verification before final `main` replacement, unless consciously accepted as deferred risk

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

Also run the new `plan-tests` routing regression from section 1.

If practical, finish with:

```bash
./evals/run.sh
```

Record exact PASS/FAIL results. Do not convert a skipped live suite into a passing claim.

## 4. Re-run deterministic validation after the remaining changes

**Priority:** required

After sections 1-2 are implemented, run the existing deterministic checks again:

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

## 5. Decide the fork version/release marker

**Priority:** finalization decision, not a semantic blocker

The reconciled fork still inherits upstream's `2.3.0` version even though it now has additional behavior.

Before publishing the reconciled branch as the maintained fork `main`, decide whether to:

- keep upstream version numbers intentionally and identify fork changes only through Git history; or
- give the fork a distinct patch/suffix/release convention.

If a fork-specific version is chosen, update all manifests that must stay consistent in one focused commit and validate installer/manifests afterward.

Do not change the version merely to create churn; make the convention explicit and consistent.

## 6. Final diff audit and `main` replacement

**Priority:** final step

Before changing `main`:

1. compare the final reconciliation branch against `upstream/main`;
2. verify every remaining fork difference is intentional;
3. confirm `archive/pre-upstream-reconcile` still points to the original fork state (`d20649b`);
4. ensure live behavior eval results are recorded, or explicitly document why that risk is being accepted;
5. keep the current logical commit separation unless the final cleanup creates a clear reason to squash a purely documentary/audit commit.

Only after that should `main` be replaced with the reconciled history.

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