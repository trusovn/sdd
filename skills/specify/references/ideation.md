# Discovery + ideation orchestration — specify step 3

For a feature that's a real bet, the deep-dive answers aren't enough to commit to an approach. This pass grounds the committed approach in **§1 ¶3** of the spec. It is **read-only research + named subagents + user confirms** — nothing is written until the spec is. Everything stays at **product level**: no concrete datastore / broker / framework / library names (those are `design` decisions); every subagent is told the same.

Two independent gates apply. The **discovery gate** runs `domain-investigator` at any depth when authoritative domain evidence is needed. The **interview-depth dial** ([`../../_shared/interview-depth.md`](../../_shared/interview-depth.md)), with feature **size** as a secondary trimmer, controls competitive/product ideation. Each named subagent receives a clean, isolated context and uses the dispatch/fallback contract in [`../../_shared/agent-roster.md`](../../_shared/agent-roster.md).

## Discovery gate (any depth)

Run `domain-investigator` when any condition applies: unfamiliar or specialized domain; regulation;
safety, security, or privacy sensitivity; operationally high-risk behavior; dependence on external
rules, standards, regulations, or current authoritative facts; or a material scope assumption that
could be wrong. This is source grounding, so `--depth=easy` does not suppress it.

## When each agent runs (depth × size)

| Depth | What runs |
|---|---|
| **easy** | **Skip ideation.** No ideation subagents. If discovery fires, run only `domain-investigator`. |
| **medium** (default) | `researcher` (competitive / web) **+** `devils-advocate` (failure modes), plus `domain-investigator` only if discovery fires. |
| **hard** | **Full suite:** `researcher` **+** `strategist` (3 approaches) **+** `analyst` (multi-perspective) **+** `devils-advocate`, then **RICE + feasibility**; add `domain-investigator` only if discovery fires. |

**Size is the secondary signal**, never the primary gate: the user's chosen depth wins, and size only *trims volume* within it — an XS/S feature at hard still runs the suite, but the `researcher` table may legitimately be one `N/A — internal tool` row and the RICE pass stays terse. (Pre-1.7 this pass was gated by size alone — "M/L/XL only". Depth is now the gate; size is the trimmer.)

## The dispatches

The dispatching prompt is the **only channel** to a clean-context agent (per the shared agent contract). For every agent below, inline the **captured idea (verbatim baseline)** + the **step-2 deep-dive answers** + any **`CONTEXT.md` path**. For `domain-investigator`, also inline the trigger reasons, user-provided source paths, material assumptions, and claims that must not be treated as verified.

1. **`domain-investigator`** (`sdd:domain-investigator`) — *discovery gate only, any depth.* Investigates authoritative rules, terminology/workflow norms, external constraints, operational failures, edge cases, risks, and measurement seeds. It explicitly separates verified facts, assumptions, unknowns, and source gaps. It does **not** investigate competitors or solution categories. **Fallback:** `general-purpose` with the same source tools; when authoritative research cannot be completed, preserve `RESEARCH_LIMITED`.
2. **`researcher`** (`sdd:researcher`) — *medium + hard.* Competitive + adjacent-solution research with web access. Returns a cited table (Product · URL · Features · Value 1–5 · Gap), each row footnoted with date + query, plus a one-line synthesis of the biggest gap. **Fallback:** a `general-purpose` Agent given the same prompt and `WebSearch`/`WebFetch`. **If web access is unavailable** in this run, accept its `RESEARCH_LIMITED` output and carry the gap as a noted gap — never invent competitors to fill the table.
3. **`strategist`** (`sdd:strategist`) — *hard only.* Generates the three strategic approaches — A Simplicity / B Differentiation / C Balanced — each with Name · Thesis · For-whom · Outcome-metric · Key-trade-off · Effort-signal.
4. **`analyst`** (`sdd:analyst`) — *hard only.* Multi-perspective review (Engineer / Executive / UX lenses) **of `strategist`'s three approaches** → a 3×3 synthesis matrix (+/0/−, ≤6-word justifications) + one synthesis line per approach.
5. **`devils-advocate`** (`sdd:devils-advocate`) — *medium + hard.* Run it in failure-mode mode: find 5–10 attack vectors with production signals. **Fallback:** `general-purpose` with the same prompt.

> Ordering at hard: dispatch triggered `domain-investigator` + `researcher` + `strategist` + `devils-advocate` together; once `strategist` returns, dispatch `analyst`. At medium: dispatch triggered `domain-investigator` + `researcher` + `devils-advocate` together. At easy: dispatch only a triggered `domain-investigator`.

## RICE + feasibility (hard only — Claude-proposed, `AskUserQuestion` confirm)

These stay **inline** (computed from the upstream signals + confirmed with the user — not a subagent):

6. **Claude-proposed RICE.** Compute from upstream: Reach ← user segments; Impact ← problem severity + `analyst`'s Executive lens; Confidence ← inverse of unresolved TBDs; Effort ← the approaches' effort signal. Compute `R × I × C / E`. Confirm each number with the user (`Confirm` / `Adjust up` / `Adjust down` / `Mark TBD`) — never make the user invent the numbers (the «calculator game» anti-pattern). Phrase per [`../../_shared/ask-style.md`](../../_shared/ask-style.md).
7. **Feasibility (read-only repo scan + confirm).** Scan the repo for adjacent shipped features. Propose three checkboxes — Tech / Skills / Time — each justified by a cited adjacent feature. Confirm each (`Confirm ☑` / `Flip to ☐ — reason` / `TBD`).

## Recommendation → §1 ¶3

Claude picks one approach and writes a 3–5 sentence rationale, then confirms it with the user (`Accept` / `Pick different` / `Mark TBD`). The accepted approach becomes **§1 ¶3** of the spec. What the rationale must cite depends on what ran:

- **hard** — cite all four upstream signals: the RICE score, the feasibility state, ≥1 `analyst` synthesis-matrix cell, and ≥1 `researcher` competitive gap.
- **medium** — cite the `researcher` gap + `devils-advocate`'s sharpest vector + the deep-dive's success criterion (no RICE/matrix exist to cite). Still a real, confirmed recommendation — just lighter.
- **easy** — §1 ¶3 states the approach Claude inferred from the deep-dive, surfaced in the assumptions ledger; the user's veto/accept on the ledger *is* the confirm.

## How the outputs feed the spec

- **`domain-investigator` findings** → `discovery.md`; verified facts and workflow constraints shape §1 Context, §3 Non-goals, and §6/§6.1 constraints; edge cases and failure modes seed §5/§6; risks and measurement seeds inform §7; assumptions, unknowns, and source gaps remain visible in §1 or §8. `RESEARCH_LIMITED` never becomes an uncited fact.
- **`researcher` gap** → cited in the §1 ¶3 recommendation; a competitor's deliberate omission may seed a §3 Non-goal.
- **`strategist` approaches** → the option set the recommendation chooses from (and the runners-up seed §8 if the user wants them tracked).
- **`analyst` matrix** → cited in §1 ¶3; a consistently `−` lens flags a §6 NFR or §11 risk to watch.
- **`devils-advocate` vectors** → the sharpest one is reserved for §6.1 Security/privacy + abuse cases (or §11 Risks); the rest seed §8 Open questions.
- **RICE / feasibility** → cited in §1 ¶3; the RICE score also feeds the roadmap's Next-ordering when `specify` registers the feature.

## Discipline

- **Depth gates ideation, not discovery.** Easy skips competitive/product ideation, but a material domain-risk trigger still requires source grounding.
- **Three approaches, not one** (at hard depth). One approach means the decision is already taken — nothing to evaluate. **All three perspectives** (at hard depth) — Engineer-only is blind to business/UX; Executive-only is blind to cost.
- **The adversary runs from clean context** — otherwise it inherits the upstream optimism.
- **Product-level only** — no concrete stack in any analysis or in §1 ¶3. Tech belongs to `design`.
- **Never invent** competitors or RICE numbers to fill the pass — better an honest `N/A — internal tool` row or a `Mark TBD` than fabricated research.
- **Planning-mode-friendly:** the whole pass is read-only. If the skill started in plan mode, keep everything in session memory and let the spec write happen after `ExitPlanMode`.
