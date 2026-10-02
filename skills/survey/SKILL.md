---
name: survey
model: inherit
effort: medium
agents: [explorer]
description: >
  Use to establish the repo's architecture map the rest of the pipeline reads. Two modes: on an
  EXISTING codebase it scans once and persists what's there; on an EMPTY/greenfield repo it runs a
  short, level-adaptive foundation session — picks the stack / folder structure / data approach /
  conventions WITH you (defaults-heavy), fixes them as the foundation + foundational ADRs, and emits
  a scaffold tasks.json that the scaffold skill materializes into a real skeleton. Triggers on "survey the
  codebase", "map the architecture", "set up a new project", "bootstrap the foundation",
  "/sdd:survey", "вивчи кодову базу", "карта архітектури", "новий проєкт", "заклади фундамент".
  Output: docs/architecture-map.md (+ adr/ + scaffold tasks.json on greenfield). Records
  reflects_commit for staleness; reads, never overwrites, an authored architecture doc.
---

# Skill: survey

The pipeline's anchor on architecture. It produces `docs/architecture-map.md` — the single source of "what the system is" that `specify` (constraints), `design` (matches against it), `data-model`, and `implement` all read instead of re-discovering the code. It runs in one of **two modes**, auto-detected:

- **Brownfield** (the repo has source) → scan it once and persist the **current** architecture.
- **Greenfield** (empty / near-empty repo) → run a short, **level-adaptive foundation session**: pick the stack / structure / data approach / conventions *with* the user (defaults-heavy), fix them as the **foundation** + foundational ADRs, and emit a **scaffold `tasks.json`** that [`scaffold`](../scaffold/SKILL.md) turns into a real skeleton. Greenfield detail → [`./references/foundation.md`](./references/foundation.md).

Repo-level utility (one map serves every feature). The scan is delegated to [`explorer`](../../agents/explorer.md); question phrasing → [`../_shared/ask-style.md`](../_shared/ask-style.md); depth → [`../_shared/size-matrix.md`](../_shared/size-matrix.md).

Map prose follows `artifact_language` (carry the language in the explorer's dispatch prompt) — frontmatter keys like `test_cmd` / `reflects_commit` stay machine-form, module/file names stay as-is → [`../_shared/artifact-language.md`](../_shared/artifact-language.md).

## Owner

Architect / Tech Lead — they own the architecture (brownfield: confirm it reflects reality; greenfield: decide the foundation).

## Inputs

- (Optional) a path/scope hint (default: repo root).
- (Read, never overwrite) repo instructions and document indexes when present (`AGENTS.md`, root
  `CLAUDE.md`, `README.md`, `docs/README.md`) so document status is resolved before content is used.
- (Read, never overwrite) authored product/architecture material after classifying it as one of:
  **active/current authoritative plans**, **accepted ADRs/current architecture**, **historical
  documents**, **research/spikes**, or **abandoned or superseded plans**. Only the first two classes
  can direct the current map; the others are evidence that may inform a question, never authority.
- (Optional, greenfield) `docs/idea-brief.md` — the intent G3 would otherwise ask for; present → confirmed, not re-asked.

## Protocol

1. **Ensure the settings file, classify authority, then detect mode/freshness.** If
`.claude/sdd.local.md` is absent, create it now from the canonical template — documented defaults +
the self-documenting body — and patch `.gitignore`; if it exists, read it and never overwrite. The
one procedure lives in [`../_shared/settings-file.md`](../_shared/settings-file.md). Creating is
unconditional; **changing values is only ever offered by [`config`](../config/SKILL.md)**. Say one
line: «`.claude/sdd.local.md` created with documented defaults — `/sdd:config` to tune it».

   Before interpreting product or architecture documents, read the repo instructions/document
   indexes from **Inputs**, follow the status they declare, and classify candidate material into the
   five authority classes above. Explicit status wins over filenames: a file named `plan.md` can be
   superseded, while an accepted ADR remains an active constraint. When status is unclear, surface
   the ambiguity instead of choosing the most architecture-like document. Historical documents,
   research/spikes, and abandoned/superseded plans may explain context but **must not authorize
   target architecture**, Accepted ADRs, or scaffold tasks merely because no current plan was found.

   Then detect mode + freshness (incremental re-survey on stale). If
`docs/architecture-map.md` exists and is fresh (its `reflects_commit` ≈ current HEAD) → «map is
fresh (reflects `<commit>`). Reuse or refresh?»; STOP on reuse. If it exists but is **stale**, prefer
the **incremental re-survey**: `git diff --name-only <reflects_commit>..HEAD`, group the changed paths
by top-level module, and dispatch the step-3 explorer **scoped only to the changed subfolders**;
update just the touched map rows/sections (module inventory, conventions, frontend, machine keys)
and re-stamp `updated_at` + `reflects_commit`. Fall back to the **full re-scan only when the diff
spans more than half the modules** in the inventory (or `reflects_commit` no longer resolves) — say
which mode ran in the handoff. No map at all → decide the mode: **brownfield** if the repo has source
(modules/packages beyond config), else **greenfield** (empty or only scaffolding like a bare
`go.mod` / `package.json`).

### Brownfield path (existing code)

2. **Read current authored docs first.** Reconcile active/current plans and accepted ADRs with the
   code, never overwrite them. Keep historical/research/superseded material labelled as context;
   it cannot override current code or accepted decisions.
3. **Scan via explorer.** Dispatch the [`explorer`](../../agents/explorer.md) agent — `subagent_type: "sdd:explorer"` (`haiku`/`low`, clean-isolated per [`../_shared/agent-roster.md`](../_shared/agent-roster.md)): «Report (a) language + frameworks + versions, (b) top-level module layout + per-module layers, (c) layering / wiring conventions, (d) datastores + access, (e) inter-module comms, (f) cross-cutting conventions (errors, IDs, tests, migrations) with one cited example each, (g) 2–3 representative features as precedents, (h) **if a frontend exists** — the component library / design system, design tokens (colors/spacing/typography), styling approach (Tailwind / CSS-modules / styled-components / …), shared UI primitives, and a representative screen/component as the UI precedent to reuse.» Large repo → fan out per subtree. (Fallback `subagent_type: "Explore"`.) Item (h) is the **reuse invariant's source**: the §Frontend / UI foundation section it fills is what `design` / `tasks` / `implement` later **compose against instead of reinventing** — new UI work reuses these components / tokens / the single styling approach, and `review` flags from-scratch UI that duplicates them. An incomplete inventory here silently licenses a second design system downstream.
4. **Synthesize + stamp + validate + write.** Fill [`./templates/architecture-map.md`](./templates/architecture-map.md) (C4 of what exists, module inventory, cited conventions, datastores, **the Frontend / UI foundation if a frontend exists**, precedent guide, constraints) with real `file:line` anchors. **Fill the machine-readable frontmatter keys** (`language`, `build_cmd`, `test_cmd`, `lint_cmd`, `migration_tool`, `frontend`) from the explorer's findings — a key with no evidence stays `""` (unknown), **never a guess**; `implement`'s command-detection cascade reads `test_cmd`/`lint_cmd` from here. Record `updated_at` + `reflects_commit: <short HEAD>`. **Validate the C4 Mermaid per [`../_shared/mermaid-check.md`](../_shared/mermaid-check.md)** (render-parse with `mmdc` if available, else the structural lint; fix before committing). Then the **structural self-check** (per [`../_shared/self-check.md`](../_shared/self-check.md)) — re-read the map from disk and verify: (1) every machine key holds an explorer-backed value or the explicit `""`; (2) every convention line cites a file that exists; (3) the C4 validated; (4) `reflects_commit` = current short HEAD. Write + commit `survey: architecture map (reflects <commit>)`. Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) — *What I did* + *Review* (`docs/architecture-map.md`) + *Run next* (`/clear`, then `/sdd:specify <slug>`). (The greenfield path emits its own handoff in G6 — forward to `/sdd:scaffold`.)

### Greenfield path (empty repo) → [`./references/foundation.md`](./references/foundation.md)

G2. **Calibrate to the person.** One opening `AskUserQuestion` to gauge how the user wants to engage — «pick good defaults, I'll confirm» / «walk me through each choice with explanations» / «let me choose each piece, keep it terse». This sets the dialogue's depth + phrasing (junior → defaults + glossed explanations per [`../_shared/ask-style.md`](../_shared/ask-style.md); senior → terser, more control). Not a product brief.
G3. **Intent + authority readiness (short).** Establish what the project is + the kind of
capabilities it'll have (e.g. «HTTP API» / «CLI» / «web app»). Enough to choose an architecture —
deliberately NOT the feature briefing (that's `specify`, per feature). **Read `docs/idea-brief.md`
first if it exists** ([`interview`](../interview/SKILL.md) writes it): its raw-idea and problem
sections already answer this, so restate the intent back in one line for confirmation and move on.
Only what the brief leaves open becomes a question — 1–3 of them, never a re-ask of something already
on disk.

   If the repository explicitly says an **active architecture plan is missing**, surface the gap
   and the architecture-bearing decisions needed for G4 (at minimum system/runtime boundary,
   persistence ownership, integrations, and deployment constraints). Stop before G4 until the user
   or prompt supplies those decisions, or explicitly defers the ones that are not required. In a
   headless run with no such decisions, **write no foundation artifacts**. Never fill the gap from
   historical/research/superseded material.
G4. **Pick the foundation, defaults-heavy.** At the calibrated depth, choose: stack (language/framework/datastore), architectural style (e.g. hexagonal modules), folder/module structure, data/persistence approach (migration tool, ID strategy), core conventions (errors, tests, CI). Recommend a coherent default set; the user confirms or adjusts. Choice menus + defaults → [`./references/foundation.md`](./references/foundation.md).
G5. **Fix the foundation.** Write `docs/architecture-map.md` as the **established foundation** (mark `mode: greenfield-bootstrap`; the C4 is the *target* baseline) + spawn **foundational ADRs** in `docs/adr/` for the irreversible picks (stack, module style, persistence). **Fill the machine-readable frontmatter keys** from the chosen foundation (`language`, `build_cmd`, `test_cmd`, `lint_cmd`, `migration_tool`, `frontend`) — here they encode the *decided* toolchain; anything not yet decided stays `""`. Record `reflects_commit`. **Validate the C4 Mermaid per [`../_shared/mermaid-check.md`](../_shared/mermaid-check.md)** before committing, and run the same step-4 structural self-check.
G6. **Emit the scaffold plan + hand off.** Write a scaffold `tasks.json` (the skeleton: folder/module structure, a baseline module, the test harness, migration tooling, CI, a `CLAUDE.md`/rules doc) per the contract in [`./references/foundation.md`](./references/foundation.md). Each task's DoD anchors on the **skeleton smoke test** — «the project builds + boots + the empty test suite runs + the migration tool runs» (canonical in [`../scaffold/SKILL.md`](../scaffold/SKILL.md)). Commit `survey: greenfield foundation + scaffold plan`. Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) — *What I did* + *Review* (`docs/architecture-map.md`, `docs/adr/`, `docs/features/_scaffold/tasks.json`) + *Run next*: `/clear`, then `/sdd:scaffold` (it materializes the skeleton; the per-feature flow starts afterwards with `/sdd:specify <slug>`).

## Definition of Done

- `docs/architecture-map.md` exists with `updated_at` + `reflects_commit`; an authored doc (if any) was reconciled, never overwritten.
- Document authority was classified; historical/research/superseded material did not become current
  architecture or scaffold work without explicit promotion by an authoritative source or the user.
- **Brownfield:** C4 of what exists + module inventory + cited conventions + precedent guide, real anchors (no placeholders).
- **Greenfield:** foundation fixed (stack/structure/data/conventions) at the user's calibrated level + foundational ADRs + a scaffold `tasks.json` whose tasks carry the skeleton smoke-test DoD, ready for `/sdd:scaffold`.
- The step-4 **structural self-check** passed ([`../_shared/self-check.md`](../_shared/self-check.md)): machine keys explorer-backed or explicitly `""`, convention citations resolve, C4 validated, `reflects_commit` current; its result is reported in the handoff.

## Anti-patterns

- **Re-scanning the repo in every downstream skill** — the point is to scan once; others read the map (drift detection is the only re-read, of real domain files).
- **Overwriting a hand-maintained `docs/architecture.md`** — survey writes its own map and reconciles.
- **Promoting the best-looking old document.** A historical plan or architecture spike remains
  evidence even when no current plan exists; surface the active-plan gap instead of adopting it.
- **A map with no `reflects_commit`** — it silently rots; nobody knows it's stale.
- **Greenfield: a full product brief.** The foundation session picks the *architecture*, not the features — the idea/briefing is `specify`'s job, per feature. Keep it to intent + foundation choices.
- **Greenfield: ignoring the person's level.** A junior gets defaults + plain-language explanations; a senior gets control + terseness. One calibration question sets this — don't fire a senior-level wall of choices at a first-timer.
- **Placeholders / guessed layout** — cited or `UNKNOWN`; a fictional map is worse than none.

## References & template

- [`./references/foundation.md`](./references/foundation.md) — greenfield: the calibration question, level-adaptive depth, the stack/structure/convention choice menus + defaults, foundational-ADR list, and the scaffold `tasks.json` contract.
- [`./templates/architecture-map.md`](./templates/architecture-map.md) — output scaffold (same file for current OR foundation; a `mode:` marker distinguishes).
- [`../_shared/agent-roster.md`](../_shared/agent-roster.md) — the explorer contract.
