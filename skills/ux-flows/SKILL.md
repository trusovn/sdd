---
name: ux-flows
model: inherit
effort: high
agents: []
description: >
  Use to derive the user flows of a UI-touching feature after the spec is clarified — one mermaid
  flowchart per UI-touching §4 user story (happy + alt/error branches from §5 ACs), a screen
  inventory (SCR-NN ids), an AC→flow map and an interaction-decision ledger (UXD-NN), written to
  docs/features/{slug}/ux-flows.md. Triggers on "ux flows for {slug}", "user flows for {slug}",
  "screen flow for {slug}", "/sdd:ux-flows {slug}", "юзер-флоу для {slug}",
  "потік екранів {slug}", "намалюй флоу користувача". Always markdown + mermaid regardless of the
  design tool; each flow is presented in prose, never raw mermaid, and only unresolved material UX
  forks are asked about — behavior is resolved for every story before any flow is drawn, and at
  easy depth the forks inferred without asking are surfaced together as ONE batch assumptions
  ledger before the flows are finalized (interactive runs; a headless run records the assumption
  rows directly and asks nothing) — spec-determined behavior is never re-asked, and a flow is
  never held hostage for approval once its behavior is resolved. Feeds design (target-surface
  evidence), sequences (SCR alignment + UXD pins), screens (the inventory) and plan-tests
  (e2e-through-UI paths). Hard-refuse if spec.md is missing; skipped for features with no
  human-facing UI.
---

# Skill: ux-flows

Draws **how the user moves** through a UI-touching feature — after `clarify`, before `design`. For
each UI-touching §4 user story it produces a mermaid `flowchart` (happy path + the alt/error
branches the §5 ACs demand), builds the **screen inventory** (`SCR-NN` — the id contract `screens`
details later), records the **interaction decisions** (`UXD-NN` — flow-altitude behavior choices
with their provenance), and maps every UI-touching AC to the flow/branch that shows it. The
artifact is **always markdown + mermaid** whatever `docs/design-system.md` picks as the drawing
tool — flows are flow-altitude, not visual design. `design` then reads it as **evidence** for the
target-surface + UI-architecture decisions (the formal `target_surfaces` declaration stays
`design`'s); `sequences` aligns UI-driven flows on the SCR ids and honors the UXD pins; `plan-tests`
takes the e2e-through-UI paths from here.

**This stage is optional by surface, not by size:** its N/A condition (no human-facing UI) lives in
[`../_shared/size-matrix.md`](../_shared/size-matrix.md) and is evaluated by `clarify`'s handoff
(`specify`'s when clarify was legally skipped). Invoked directly, it always runs.

Question phrasing → [`../_shared/ask-style.md`](../_shared/ask-style.md); each diagram is presented
**in prose, never as raw mermaid** → [`../_shared/diagram-presentation.md`](../_shared/diagram-presentation.md);
the approval policy is **ux-flows' own**: flows are behavior-resolution evidence, so the skill asks
about **unresolved UX behavior** (the classification pass below), never manufactures an approval
stop for a flow whose behavior is already pinned. Flow labels + prose follow `artifact_language` —
mermaid keywords, SCR ids and AC ids stay English → [`../_shared/artifact-language.md`](../_shared/artifact-language.md).

## Owner

PM + designer (or whoever owns the user experience). The PM confirms each flow matches a real user
story; the Tech Lead flags flows that imply architecture (they become `design` input, not decisions
here).

## Inputs

- `<slug>` — feature slug.
- **Gate (hard-refuse if missing):** `docs/features/<slug>/spec.md` — the flows derive from §4 user
  stories + §5 ACs. Absent → STOP: «run `specify <slug>` first — ux-flows derives from its user
  stories».
- (Expected) `docs/design-system.md` — the platform posture (the default platform assumption) +
  the tool. **Absent → not a block**: work in `code`-mode assumptions, recommend
  `/sdd:design-system` in the handoff.
- (Optional) `CONTEXT.md` (both levels, per-feature wins) — canonical roles for the actors.
- (Optional) `docs/features/<slug>/.size` / `.route` — depth + handoff resolution; absent → default
  M / standard and say so in the handoff.

## Behavior classification (the pass before every branch is drawn)

Before drawing each flow, classify every meaningful transition/branch into one of four categories.
The category decides **what happens to it**, not just how it is drawn.

| # | Category | What it looks like | What to do |
|---|---|---|---|
| **A** | **Spec-determined** | The behavior is explicitly stated by the user story or AC — e.g. blank trimmed Project name → validation failure → nothing persisted. | Use directly. **Do not ask.** |
| **B** | **Safe derivation** | The exact UI mechanics aren't stated, but only one ordinary interpretation is needed and it does not materially change the user's journey — e.g. validation failure allows retry on the same logical creation surface. | Depends on depth: **easy** → derive + ledger if meaningful; **medium** → normally derive; **hard** → may inspect for edge ambiguity, but don't ask merely for approval. |
| **C** | **Material UX fork** | Two or more plausible user-visible behaviors exist — e.g. after successful Project creation: remain in the new Project context / automatically launch Create Environment / return to the project list; or independently: does the newly created Project automatically become active context? | Resolve per the C fork-resolution rule below (asked at medium/hard; at easy only inferred under the inferable+reversible test). Never silently invent one. |
| **D** | **Upstream contradiction** | The requested behavior contradicts an explicit requirement in `spec.md` — e.g. AC says Environment creation opens automatically, but the user says it must not. | Surface it (see below). Never silently override the spec. |

**Never ask** Accept / Fix / OQ / Drop *this flow?* when the unresolved thing is actually a **C**
domain choice — resolve the behavior instead (per the C fork-resolution rule below; ask the
question when it is not inferable):

> What should happen after the Project is successfully created?
> 1. Make the new Project active and remain in its Project context.
> 2. Make it active and immediately start Environment creation.
> 3. Save it without automatically selecting it.
> 4. Another behavior / defer.

The alternatives must come from **plausible behaviors supported by the known feature context** —
not generic workflow states.

Behavior resolution runs as its own pass, **before** any flow is drawn: the fork's outcome
feeds the flow, never the other way around — so the flows are generated from resolved behavior,
and the assumptions-ledger gate below sits **between** the two passes (behavior resolved first →
flows generated second).

### C fork resolution (the single rule)

At **medium** a material C fork is asked; at **hard** the hidden-fork sweep asks even more. The
only level that may resolve a material C fork without asking is **easy**, and this is the exact
rule for it — easy reduces question volume; it does not license invention.

**Interactive easy:**

- A material C fork **MAY be inferred without asking** only when **all three** hold:
  1. a reasonably strong conventional/default answer exists for this product surface;
  2. the choice is reversible / low-risk for the user journey;
  3. the rationale can be stated in one line.
- Record such a choice as a provisional `UXD-NN` row with Source `easy assumption` — collected
  in memory during the behavior-resolution pass and **confirmed via the batch easy-assumptions
  ledger below, before the flows are finalized on top of it**.
- **If the fork is genuinely ambiguous / un-inferable, ask the concrete behavior question even at
  easy.**

**Headless easy (no interactive user — `AskUserQuestion` unavailable):**

- If the prompt already supplies the UX decision, treat it as user-confirmed (Source
  `user-confirmed`) and continue.
- If the behavior is safely inferable under the interactive rule above, use an easy assumption.
- **If a material fork is genuinely ambiguous and neither the spec nor the prompt resolves it,
  surface/block on the unresolved behavior** (say what is unresolved and why it cannot be
  inferred). Do **not** pick an arbitrary UX choice merely because `AskUserQuestion` is
  unavailable — headlessness removes the question channel, not the fork. The same holds at any
  depth in a headless run: an un-answerable question is a blocker, never an invention.
- **No assumptions-ledger question** — the shared ledger's ONE batch `AskUserQuestion`
  ([`../_shared/interview-depth.md`](../_shared/interview-depth.md)) presumes an interactive
  user; a headless run has none, so the inferable forks are recorded directly as `easy
  assumption` UXD rows and the run proceeds. The ledger's substance still holds — every
  assumption is written down in the UXD ledger where the user (or the invoking prompt) can see
  and veto it.

The distinction, always:

- **inferable + reversible →** possible `easy assumption` UXD row;
- **genuinely un-inferable material fork →** a behavior question (interactive) or a blocker
  (headless) — never a silently invented flow.

### The easy-assumptions ledger gate (interactive easy, between the two passes)

At interactive `easy`, every C fork inferred under the rule above is an assumption made **for**
the user — the ledger case in
[`../_shared/interview-depth.md`](../_shared/interview-depth.md) («The assumptions ledger»). In
`ux-flows` that ledger is **one batch behavior-decision gate**, not a diagram-approval step:

1. **During the behavior-resolution pass** (protocol step 3), collect every permitted easy
   assumption in memory as a provisional `UXD-NN` row (Source `easy assumption`, one
   independent fork per row).
2. **Before finalizing/writing any flow on top of those assumptions**, surface them as the ONE
   ledger `AskUserQuestion` — the batch «here is what I assumed» veto/accept opportunity.
3. **All accepted →** the provisional UXD rows become resolved as recorded; generate, validate
   and prose-describe the flows normally.
4. **One or more vetoed →** ask a concrete behavior question **only for the vetoed decisions**
   (plausible alternatives from the feature context — the C-fork shape above, never «Accept /
   Fix / Save-as-OQ / Drop this flow?»), update those UXD rows (Source `user-confirmed`), then
   generate the affected flows.
5. **Zero easy assumptions collected →** do not manufacture a ledger question — proceed directly
   to flow generation.

The user is approving or changing **inferred behavior**, never approving Mermaid; the flows
themselves are never re-confirmed after this gate (the no-manufactured-approval-stop rule
holds). At `medium`/`hard` there is no ledger — those levels asked each real fork directly; a
headless `easy` run skips the gate per the headless rule above.

### D — upstream-contradiction handling (deterministic)

When current input requests behavior that contradicts an explicit **retained** spec requirement:

1. **Surface the requested behavior.**
2. **Surface the exact conflicting US/AC** (quote the retained line).
3. **State that `ux-flows` cannot rewrite the canonical spec** — `spec.md` is the retained
   authority (it gates this skill; the same higher-authority rule `design` applies to UXD rows).
4. **Do not write a flow that contradicts the retained spec** — at any `status`, draft included.
5. **Do not record the conflicting requested behavior as an accepted `UXD-NN`** row.
6. **Do not claim the artifact is complete / ready for downstream `design`** while the conflict
   remains unresolved — no self-check-pass claim, no normal `/sdd:design` handoff.

**Interactive run — offer the real resolution:**

- **retain the existing spec behavior** (the flow is drawn per spec) — only after the user
  explicitly chooses this; or
- **amend the requirement upstream** via `clarify`/`specify` — the current instruction requesting
  the contradictory new behavior is an **amendment request**, not permission to silently ignore
  it and continue under the old spec. If the instruction already clearly requests the new
  behavior, stop the stage and direct upstream; do not treat retention as the default.

**Headless run with an explicit conflicting requested behavior** — the deterministic outcome is a
**blocker + upstream redirect** (`clarify`/`specify`), never a normal handoff. Never silently
invent a requested-behavior UXD, and never draw a contradictory flow merely because the artifact
stays `draft`.

**The final artifact must never contain a flow contradicting an explicit retained AC.**

## Depth in ux-flows

- **Easy** — derive directly specified behavior; autonomously resolve low-risk/reversible
  conventions; record meaningful assumptions; do not ask just to approve generated flows; a
  material fork is inferred **only** under the C fork-resolution rule above (strong conventional
  default + reversible + statable rationale → provisional `UXD-NN`, Source `easy assumption`,
  batched through the assumptions-ledger gate before the flows are finalized in an interactive
  run — recorded directly in a headless run); a genuinely un-inferable / material behavior
  still **cannot be silently invented** — ask it (interactive) or surface it as a blocker
  (headless).
- **Medium** — identify material user-visible forks; ask **only those real UX questions**; derive
  everything else; **no mandatory per-flow confirmation**.
- **Hard** — actively hunt for hidden UX forks: *post-success destination, active-context
  selection, retry behavior, cancel/back behavior, destructive-action recovery, automatic
  progression, modal vs navigational continuation when flow-significant*. Ask concrete behavioral
  alternatives; still do not ask generic approval questions for already-resolved flows.

Hard means **better UX discovery**, not more «approve diagram?» prompts.

## Protocol

1. **Gate + read.** `test -f docs/features/<slug>/spec.md` → missing = refuse with the pointer
   above. Read spec §1 (context), §4 (user stories — which touch a UI?), §5 (ACs), `CONTEXT.md`
   glossary, and `docs/design-system.md` (posture + tool; note its absence for the handoff).
2. **Set the depth dial + platform.** Read `interview_depth` from `.claude/sdd.local.md` (else
   medium); unless `--depth=` was passed, ask ONE depth-selection `AskUserQuestion` per
   [`../_shared/ask-style.md`](../_shared/ask-style.md), then confirm the **platform posture** in
   the same call (second question): the design-system posture as «(Recommended)», deviation
   allowed + recorded with its why. Depth governs the fork-hunting + question volume
   (→ the Depth section above and [`../_shared/interview-depth.md`](../_shared/interview-depth.md));
   coverage never shrinks.
3. **Behavior-resolution pass — for each UI-touching §4 user story, resolve its behavior before
   anything is drawn:**

   1. **Derive the behavior skeleton** from §4 + §5.
   2. **Classify** each meaningful transition/branch per the behavior-classification pass (A–D).
   3. **Resolve the required UX forks** according to the C fork-resolution rule above
      (interactive: strong-default + reversible forks may be inferred as easy assumptions;
      genuinely un-inferable forks are asked; headless: prompt-supplied → user-confirmed,
      inferable → easy assumption, un-inferable + unresolved → surface/block). D contradictions
      are handled per the deterministic D pass above.
   4. **Collect every flow-altitude interaction decision** as a `UXD-NN` row (in memory at
      interactive `easy` — they are provisional until the ledger gate below confirms them;
      resolved directly at medium/hard and in a headless run). One independent fork per row —
      do not bundle two unresolved behaviors into one id; no rows for trivial AC-derived
      steps.
   5. **Note provisional SCR needs** (the screens each story's behavior will visit) — the
      inventory is finalized in step 5 from the resolved behavior.

   A backend-only user story is listed as out of scope, not drawn.
4. **Easy-assumptions ledger gate (interactive easy only — zero collected assumptions → skip
   this step).** Run the ledger gate exactly per the section above: surface the provisional
   easy-assumption UXD rows as ONE batch behavior-decision question; on acceptance they become
   resolved; on a veto ask the concrete behavior alternatives **only** for the vetoed decisions
   and update those rows. This is the only easy-level batch stop — it approves/changes inferred
   **behavior**, never diagrams (medium/hard already asked their real forks in step 3; a
   headless run has no ledger question at all). Once this gate is through, no per-flow
   approval is manufactured downstream.
5. **Flow-generation pass — for each UI-touching §4 user story, from its resolved behavior:**

   1. **Finalize the SCR inventory** — every screen the resolved behavior visits gets/keeps a
      `SCR-NN` row (purpose/entry/exit); flow nodes reference the SCR ids.
   2. **Write the Mermaid `flowchart`** into `docs/features/<slug>/ux-flows.md` (from
      [`./templates/ux-flows.md`](./templates/ux-flows.md)).
   3. **Parse-check the block** per
      [`../_shared/mermaid-check.md`](../_shared/mermaid-check.md).
   4. **Explain the happy path + every branch in prose** — per
      [`../_shared/diagram-presentation.md`](../_shared/diagram-presentation.md), never raw
      mermaid.
   5. **Continue to the next flow.** No manufactured approval stop: once its behavior is
      resolved (step 3, + the ledger gate at interactive easy), a flow is written and
      described, not re-confirmed. The user can still interrupt at any point («Change US-01 …»)
      — the skill just does not invent an approval gate where no decision remains.

   The interaction decisions resolved above are also written to the file's
   `## Interaction decisions` section as part of this pass.
6. **Fill the AC map + write + commit.** Complete the AC-coverage table (every UI-touching §5 AC →
   flow/node/branch, or an explicit `N/A: <reason>`), re-validate every mermaid block, stamp
   `updated_at`, propose commit `ux-flows: <slug>`.
7. **Structural self-check** — per [`../_shared/self-check.md`](../_shared/self-check.md): re-read
   the file from disk and verify **4 items**: (1) every UI-touching §4 user story has a flow;
   (2) every flow node's SCR id exists in the inventory (and every inventory row appears in ≥1
   flow); (3) every UI-touching §5 AC appears in the coverage table with a flow/branch or an
   explicit N/A; (4) every mermaid block parses. Fix + re-check ≤2 cycles; surface anything
   unresolved.
8. **Handoff.** Emit the **stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md)
   — *What I did* (incl. «self-check: 4/4 pass»; + «`docs/design-system.md` absent — run
   `/sdd:design-system`» when it was) + *Review* (`docs/features/<slug>/ux-flows.md`) + *Run next*:
   `/clear`, then `/sdd:design <slug>` (it reads these flows as target-surface evidence).

## Definition of Done

- `docs/features/<slug>/ux-flows.md` exists: platform decisions, the interaction-decision ledger,
  the SCR-NN inventory, one flow per UI-touching §4 user story (happy + AC-demanded branches), the
  AC-coverage table — zero silently uncovered UI ACs.
- Every flow was written, parse-validated and described in prose. Every material interaction
  behavior not fixed by the spec was either resolved explicitly, recorded as a permitted
  easy-assumption UXD row (inferable + reversible per the C fork-resolution rule), or surfaced as
  an upstream blocker — and, in an interactive easy run, the inferred assumptions passed the
  batch assumptions-ledger gate before any flow was finalized on top of them. No unresolved
  behavioral fork was silently turned into flow behavior, and no arbitrary UX choice was
  invented merely because asking was unavailable.
- No flow contradicts an explicit retained AC — at any `status`, draft included — and no
  spec-contradicting requested behavior is recorded as an accepted UXD row.
- No visual design leaked in: no component names, no layout, no styling — flow altitude only
  (screens is where states + components live).

## Anti-patterns

- **Drawing screens here.** Components, states, layout belong to `screens`; this artifact is the
  movement between screens, not their content.
- **Deciding architecture here.** «SPA vs SSR», «this needs a websocket» — flag it as design input;
  `design` decides and declares `target_surfaces`.
- **Raw mermaid as the review channel** — the anti-pattern
  [`diagram-presentation.md`](../_shared/diagram-presentation.md) exists to kill.
- **Manufacturing an approval stop.** Asking «Accept / Fix / OQ / Drop this flow?» when the flow's
  behavior is already pinned by the spec or a resolved fork — the question should only ever be
  about unresolved *behavior*. (The easy-assumptions ledger gate is the one legitimate batch
  stop, and it is a behavior-decision batch — never a diagram approval.)
- **Asking a domain choice as an approval question.** «What should happen after the Project is
  successfully created?» is a real question; «Accept this flow?» standing in for it is not.
- **Silently overriding `spec.md`.** A requested behavior that contradicts an explicit AC is
  surfaced, never drawn over; the artifact never contradicts a retained AC — a `draft` status is
  not cover for a contradictory flow.
- **Inventing a material fork because asking is unavailable.** Headless or not, a genuinely
  ambiguous material fork is surfaced as a blocker (or answered by the prompt), never resolved by
  an arbitrary pick.
- **Bundling two unresolved forks into one `UXD-NN` row.** Resolve each independently.
- **A `UXD-NN` row for every trivial AC-derived step.** Only flow-altitude interaction choices
  that add useful provenance get an id.
- **Skipping backend-only stories silently.** List them as out of scope with one line — the reader
  must see they were considered.
- **Blocking on a missing design-system.** Its absence degrades (code-mode assumptions + a handoff
  recommendation), never blocks the flow work.

## References & template

- [`./templates/ux-flows.md`](./templates/ux-flows.md) — output scaffold; inline comments are the
  generation contract.
- [`../_shared/diagram-presentation.md`](../_shared/diagram-presentation.md) ·
  [`../_shared/mermaid-check.md`](../_shared/mermaid-check.md) — prose presentation + parse-validation
  (the approval policy itself is this skill's, above).
- [`../_shared/size-matrix.md`](../_shared/size-matrix.md) — the N/A condition (no human-facing UI)
  evaluated by the upstream handoff.
- [`../_shared/interview-depth.md`](../_shared/interview-depth.md) — the depth dial set in step 2;
  ux-flows' per-level behavior is defined in the «Depth in ux-flows» section above.
