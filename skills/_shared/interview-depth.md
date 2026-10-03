# Interview depth — easy / medium / hard (the depth dial)

> **Reference-only.** Not a skill. The Q&A skills (`specify`, `clarify`, `design`, `interview`, `ux-flows`) read
> this for the canonical three levels and how each adapts. The dial tunes **how much the skill decides on
> its own vs. interrogates you** — question volume, autonomy, which analyses run, and how each diagram is
> handled. It does **not** tune *completeness*:
> every acceptance criterion is still covered at every level (see the coverage floor below).

## TL;DR (короткий вступ українською)

«Депт-діал» — один регулятор на запуск скіла: **easy / medium / hard**.

- **easy** — скіл сам ухвалює більшість рішень із розумними дефолтами, питає тільки незворотні / високоризикові, і **виписує припущення, які зробив**, щоб ти міг їх ветувати. Менше аналізу, діаграми пишуться + підсумок (без поштучного питання).
- **medium** — поточний збалансований сократичний прохід (дефолт).
- **hard** — проходимо **кожне** рішення; кожне `AskUserQuestion` виводить trade-off на передній план; повний набір ідейних аналізів (research / approaches / perspectives / devil's-advocate); edge-cases копаємо глибше.

Повнота (покриття кожного AC) **не залежить** від рівня — easy теж покриває всі AC, просто менше питає *як саме*.

---

## How the level is chosen (every consuming skill, step 1)

A consuming skill resolves the level once, at the top of its run, in this precedence (highest wins):

1. **A `--depth=easy|medium|hard` argument** passed on the invocation, if present — silent, no question.
2. **The opening `AskUserQuestion`** — ONE depth-selection question, phrased per [`ask-style.md`](./ask-style.md) (explanatory + every term glossed). Its **default option** (the «(Recommended)» first option) is:
   - the `interview_depth` value from `.claude/sdd.local.md` if that file exists and sets it, else
   - **medium**.
   The user can always override per run — the saved default only pre-selects the recommendation; it never skips the question (unless `--depth=` was passed).

`interview_depth` is a **plugin-wide** setting (documented with the rest in [`settings-file.md`](./settings-file.md)), not implement-only. The settings file is **created with documented defaults by the first of six skills to run** — `interview` / `survey` / `roadmap` / `scaffold` / `specify` / `implement`, each as its opening protocol step — so later Q&A skills read a real file; a reader that still finds it missing defaults the question to medium. There is **no hard dependency** on `implement` having run first (the create step is the same documented template wherever it fires), and the value is changed only by [`../config/SKILL.md`](../config/SKILL.md).

The opening question is also where the skill states what the level will *do* to this run («easy → I'll decide the reversible calls myself and list my assumptions; hard → I'll walk every decision and run the full analysis suite»), so the user picks with eyes open.

## What each level governs (the axes)

| Axis | **easy** | **medium** (default) | **hard** |
|---|---|---|---|
| **Question volume + autonomy** | Skill decides the reversible / low-stakes calls itself with sensible defaults; asks ONLY the irreversible / high-blast-radius / genuinely-un-inferable ones. **States every assumption it made** (an assumptions ledger) so the user can veto. | The balanced Socratic walk — one `AskUserQuestion` per real decision, trivial convention-defaults bundled. | Walks **every** decision; each question **foregrounds the trade-off** (what you gain / lose / the hidden catch); probes edge cases harder. |
| **Ideation analyses** (`specify` step 3) | Skip the suite — deep-dive answers only. | `researcher` (competitive/web) + `devils-advocate`. | Full suite: `researcher` + `strategist` (3 approaches) + `analyst` (multi-perspective) + `devils-advocate`, then the Claude-proposed RICE/feasibility confirm. |
| **Diagram handling — decision-validation diagrams** (`design` C4 §3/§5; `sequences` flows, currently) | Write + **one-line prose summary** per diagram, then proceed — no per-diagram question (presentation per [`diagram-presentation.md`](./diagram-presentation.md); the ledger catches vetoes). | Prose description + `AskUserQuestion` confirm **per diagram** (the skill's own four-state flow validation). | Prose description + confirm per diagram, **plus deeper probing** of the decisions the diagram exposes (never raw Mermaid). |
| **Diagram handling — behavior-resolution flows** (`ux-flows`) | **Infer a material UX fork only when it has a reasonably strong conventional/default answer, is reversible/low-risk, and the rationale can be stated** — record each as a `UXD-NN` row (Source «easy assumption»); a genuinely ambiguous/un-inferable material fork is still asked even at easy, or surfaced as a blocker when headless. Never pick an arbitrary UX choice just because asking is unavailable. | Ask the **meaningful unresolved UX forks** (one `AskUserQuestion` per fork that changes the flow); don't re-ask behavior already pinned by the spec. | **Actively hunt** for UX forks — run the adversarial sweep, surface every branch the ACs imply, and ask each one. |
| **Edge-case / ambiguity probing** | Only the edges that change the blast radius. | The spec's stated error/authz/edge criteria. | Adversarial — hunt for unstated edges, run the full `devils-advocate` pass, push on every «what if». |

Read the axes together, not in isolation: **easy** is «trust the defaults, show me what you assumed»; **medium** is «walk the real decisions with me»; **hard** is «interrogate me, run everything, leave nothing un-probed». The dial scales *effort spent asking*, not *effort spent being correct*. Diagram handling differs by what the diagram is *for*: a **decision-validation diagram** renders a decision the skill owns (confirm the decision), while a **behavior-resolution flow** renders UX behavior that must be pinned down (ask the unresolved forks).

## The assumptions ledger (easy only)

At `easy`, every decision the skill made **for** the user (instead of asking) is recorded as a one-line ledger entry and surfaced together before the write-point:

```
- Assumed: <decision> = <chosen value>  — because <default rationale>.  [veto?]
```

The user gets ONE `AskUserQuestion` to veto/adjust the ledger as a batch (or accept all). An assumption the user vetoes becomes a real question (medium-style) for that one item. This is the easy-level safety net: autonomy without silent commitment — the user sees every default before it's locked, just not as N separate prompts. (At medium/hard there is no ledger — those levels asked the question directly.)

## The coverage floor is depth-independent (correctness, not a preference)

Depth tunes **how many questions** and **how much autonomy** — never **what gets covered**. The completeness guarantees hold at **every** level:

- Every spec §4 user story has ≥1 acceptance criterion (the **use-case floor**); §5 keeps ≥1 AC of each of the 5 coverage types (`specify` — authorization may instead carry its explicit, sourced `Authorization: N/A` line, the only waiver).
- Every §4 user story maps to ≥1 flow, and every §5 AC maps to a flow, a branch, or an explicit N/A (`sequences` use-case + AC→flow coverage check).
- Every user story + AC traces end-to-end spec → sequences → data-model → api → tasks → implement (`review`).

`easy` reaches these by **deciding** the «how» with defaults and listing them in the ledger; `hard` reaches them by **asking**. The destination is identical. A skill must never drop an AC, a coverage type, or a flow because the level is `easy` — that's a correctness bug, not a depth choice. If easy can't infer the «how» for a coverage-relevant decision, that decision is one of the «irreversible / un-inferable» ones it **must** ask about regardless of level.

## Per-skill adaptation (the delta each consuming skill applies)

- **`specify`** — the level gates step 3's ideation suite (table above) and the volume of the step-2 deep-dive + step-7 Socratic validation. The §5 coverage gates (≥1 of each of the 5 AC types — authorization waivable only by its explicit, sourced `Authorization: N/A` line — **and ≥1 AC per §4 user story** — the use-case floor) are **floor, not dial** — enforced at every level.
- **`clarify`** — the level gates how aggressively the self-sweep + `devils-advocate` hunt (easy: only build-divergence that changes behavior, with assumptions stated; hard: adversarial, every fork surfaced) and the per-finding question volume. Every surfaced ambiguity is still Resolved or Deferred at every level — none dangling.
- **`design`** — the level gates the per-section Socratic question volume (easy: decide convention-defaults itself + ledger, ask only blast-radius decisions; hard: walk every decision, foreground each trade-off) and the C4 diagram handling (decision-validation diagrams — table above; presentation per [`diagram-presentation.md`](./diagram-presentation.md), confirmation via design's own four-state loop). The blast-radius → ADR gate and the §11 owner+due rule are floors, enforced at every level.
- **`sequences`** — the level (read from settings; `sequences` asks no depth question of its own) gates the per-flow confirmation policy in step 6: `easy` → write + summarize into the ledger; `medium`/`hard` → per-flow Accept / Fix / Save-as-OQ / Drop (decision-validation diagrams — table above). The §4/§5 coverage floor is enforced at every level.
- **`ux-flows`** — the level gates the behavior-resolution pass (behavior-resolution flows — table above): `easy` → derive spec-determined + safe-derivation behavior, and a **material fork is inferred only when it has a strong conventional default, is reversible, and the rationale can be stated** — recorded as a `UXD-NN` row (Source «easy assumption»); a prompt-supplied UX decision is `user-confirmed`; a genuinely un-inferable material fork is **asked even at easy** (interactive) or surfaced as a blocker (headless), never silently invented; `medium` → identify and ask only the material user-visible forks, no per-flow confirmation; `hard` → actively hunt the hidden-fork checklist (post-success destination, active-context selection, retry, cancel/back, destructive-action recovery, automatic progression, modal vs navigational continuation) and ask concrete behavioral alternatives — never generic «approve this flow?» prompts. The structural floor (every §4 story + §5 AC covered, every mermaid parses) holds at every level.
- **`interview`** (the pre-spec idea stress-test) — the level maps to a question budget + posture: **easy** → 3–4 questions (decide-for-you: one pass on intent, one sharp tradeoff, one angle); **medium** → 6–10 (balanced, full three phases); **hard** → 10–15 (interrogate-me: drill every assumption, run more probing frames). Inside a git repo it writes `docs/idea-brief.md` (8 sections); outside one it stays talk-only. Either way there is no assumptions ledger — the budget and posture are the whole delta.

A consuming skill adds a one-line pointer to this file at its depth-selection step and otherwise reads the level as a parameter into its existing loop — it does not re-implement the dial.
