# SDD behaviour evals — on-demand, NOT CI

End-to-end scenarios that drive a real `claude` session over a fixture repo and let an LLM judge
verify the outcome against a rubric. They complement `scripts/validate_plugin.py` (structure):
evals check that a **skill's protocol actually behaves** —
gates refuse, artifacts land in shape, handoffs are emitted.

> **Why not CI.** Each run invokes `claude -p` (the run under test) + a judge call — it costs real
> tokens, takes minutes, and is non-deterministic. Run evals locally when you change a skill's
> protocol; CI stays deterministic (`validate`).

## Prerequisites

- `claude` CLI installed and logged in. The sdd plugin does **not** need to be installed —
  `run.sh` loads it from this checkout via `--plugin-dir`, so the eval exercises the working
  tree, not an installed version.
- `jq`, `git` on PATH.
- Budget: one scenario ≈ one short agent session + one judge call.

## Run

```bash
./evals/run.sh                        # all scenarios
./evals/run.sh design-gate-refusal    # one scenario
SDD_EVAL_MODEL=opus ./evals/run.sh classify-size   # override the model
```

Exit code is non-zero when any scenario's verdict is `FAIL` (or unparseable).

## How a scenario works

1. `run.sh` copies `scenarios/<name>/fixture/` into a `mktemp` dir and `git init && commit`s it
   (the baseline).
2. It runs `claude -p "$(cat prompt.txt)" --permission-mode acceptEdits --max-turns 40
   --output-format json` **inside that dir**. Prompts always pin `--depth=easy` and state
   «headless — no interactive user», because a headless run cannot answer `AskUserQuestion`.
3. It then asks a judge (`claude -p` with [`judge-prompt.md`](./judge-prompt.md)) to verify the
   **rubric** against the file tree, the `git log` (so rubrics can count/inspect the run's
   commits — `Bash(git:*)` is pre-allowed in the throwaway workdir so runs CAN commit), the
   full `git diff` vs the fixture baseline (committed + uncommitted), and the tail of the
   run's final message. The judge answers one JSON object:
   `{"verdict": "PASS"|"FAIL", "checks": [...]}`.

## Scenarios

| Scenario | What it proves |
|---|---|
| `specify-happy-path` | `/sdd:specify` produces a spec.md with §1–§8, business-observable ACs, `.size` + `.route`, and the handoff block |
| `specify-unfamiliar-domain-discovery` | `/sdd:specify --depth=easy` still runs risk-gated authoritative domain discovery, writes `discovery.md`, preserves `RESEARCH_LIMITED` source gaps, and feeds relevant findings into `spec.md` |
| `specify-product-measurement-plan` | `/sdd:specify` produces actionable KPI rows with observable sources, baseline plans, target/timeboxes, decision thresholds, owners, and review timing |
| `specify-measurement-na-waiver` | `/sdd:specify` on a walking skeleton resolves §6/§7 to a sourced `Measurement: N/A` + §8 revisit instead of fabricated targets or vanity rows |
| `plan-tests-risk-measurement-coverage` | `/sdd:plan-tests` traces retained risks and KPI promises into task-linked pre-release evidence plus honest post-release outcome monitoring |
| `survey-authority-conflict` | `/sdd:survey` follows a current local-CLI plan over a conflicting historical distributed-system spike and keeps the scaffold structural |
| `survey-missing-active-plan` | `/sdd:survey` on a docs-only repo whose authority map says the active architecture plan is missing stops without promoting historical research |
| `survey-empty-cli-scaffold` | `/sdd:survey` on an empty CLI repo uses prompt-confirmed foundation decisions and hands the structural plan to the current `scaffold` flow |
| `design-gate-refusal` | `/sdd:design` on a folder with `.size` but **no spec.md** refuses, points at `specify`, writes no sad.md/ADRs |
| `classify-size` | `/sdd:classify-size` writes one-token `.size` + `.route` and hands off (utility variant) |
| `api-fastlane-no-datamodel` | `/sdd:api` on a no-schema-change feature **without** data-model.md does not refuse — it derives the contract from the existing schema, names the legal skip + «existing schema» origins, and emits the handoff |
| `api-schema-change-refusal` | `/sdd:api` on a feature **with** a schema change (staged migration + new sad §5 entity) and no data-model.md hard-refuses, names `data-model`, writes no contract and no self-served data-model.md |
| `design-quick-commit-batching` | `/sdd:design` on route quick + depth easy writes all 12 SAD sections to disk but batches commits — ≤4 after the baseline (bootstrap + ≤3 batches), not per-section |
| `tasks-compile-coupled-lane` | `/sdd:tasks` on a Go feature extending a shared interface emits no standalone interface-only task — it folds the contract change or marks the compile-coupled pair via a shared `files_hint` |
| `ux-flows-code-mode` | `/sdd:ux-flows` on a UI feature with a committed `docs/design-system.md` (`tool: code`, mobile-first) derives `ux-flows.md` headlessly — valid mermaid flowcharts, an SCR inventory, a UXD-NN interaction-decision ledger, a full AC-coverage map, the mobile-first posture honoured, and a handoff forwarding to `design` |
| `ux-flows-interaction-decision` | `/sdd:ux-flows` on a walking-skeleton spec whose post-success transition is unspecified records the prompt-stated interaction decision as `UXD-01` and honors it: US-01 ends at the intended Project state, no automatic edge runs into Environment creation, US-02 stays its own flow, and coverage/SCR/handoff invariants hold |
| `ux-flows-spec-conflict` | `/sdd:ux-flows` on a spec whose AC explicitly requires automatic Environment creation, with a prompt demanding the opposite, does NOT silently rewrite the flow against the AC — it surfaces the spec conflict (requested behavior + exact AC), never writes a contradictory flow at any artifact status nor accepts the behavior as a UXD row, directs requirement amendment upstream, and (headless + explicit conflicting request) ends in a blocker + upstream redirect, not a normal design handoff |
| `roadmap-fog-unsized` | `/sdd:roadmap` on a brief whose second data source has never been inspected writes `fog` in that step's **`Size`** cell and parks it as ONE area in `## Not yet specified` instead of sizing the unformulated — and writes the file at all, with no architecture map in the fixture |
| `roadmap-same-zone-wave` | `/sdd:roadmap` keeps two steps that both edit `internal/checkout/pricing.go` out of the same wave (the graph permits it, the codebase doesn't) while still letting the `internal/notify/` step run in parallel |
| `clarify-judgment-sonnet` | `/sdd:clarify` with `judgment_model: sonnet` in the fixture settings completes the sweep on the sonnet tier — the setting is read + honoured, the handoff reflects sonnet and never claims opus. *Limitation:* headless can't simulate a missing entitlement, so this covers the configuration path only, not the hard-failure fallback (retry on `inherit` per `agent-roster.md` §Model availability) |

## Adding a scenario

Create `scenarios/<name>/` with three parts:

- `fixture/` — the starting repo tree (committed as the git baseline; keep it minimal).
- `prompt.txt` — the exact `-p` prompt: the `/sdd:` command line plus the headless framing
  (state the idea/answers inline; always `--depth=easy`).
- `rubric.md` — numbered PASS conditions the judge can verify from the diff/tree/final message
  only. Make every item observable; «the model tried» is not a rubric item.

## Manual medium-depth regression check (not automatable)

The headless harness pins `--depth=easy` and cannot answer `AskUserQuestion`, so the most
important conversational change in `ux-flows` — that it asks about **unresolved UX behavior**
instead of asking the user to approve a generated diagram — has no automated eval. Run this
interactively when you change `ux-flows`' behavior-resolution pass:

1. Take the `ux-flows-interaction-decision` fixture (or any feature spec where Project-creation
   success is defined but the active-context selection and any automatic Environment prompting
   are left unspecified).
2. Run `/sdd:ux-flows <slug> --depth=medium` with a real user.

**Good:** the skill asks the behavior question with concrete alternatives:

> What should happen immediately after successful Project creation?
> 1. Make the new Project active and remain in its Project context.
> 2. Make it active and immediately start Environment creation.
> 3. Save it without automatically selecting it.

…potentially followed by *Should the newly created Project become the active Project context?*
if that remains a separate ambiguity.

**Fail:** the skill instead asks to approve the generated drawing — e.g. «Flow US-01 generated.
1 Accept / 2 Fix / 3 Save as OQ / 4 Drop». That approval-instead-of-behavior regression is the
manual failure criterion.
