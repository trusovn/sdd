# Draft generation — per-section contract for specify step 6

The authoritative format for each section is the `<!-- instruction -->` comment in [`../templates/spec.md`](../templates/spec.md). This file is the operational glue: where content comes from and what is forbidden.

## Inputs in priority order

1. **`CONTEXT.md` `## Glossary`** — canonical for role names + domain terms. If anything contradicts it, the glossary wins.
2. **The interview** (step 2 capture + deep-dive) — the problem, the trigger, success criteria, constraints.
3. **The `discovery.md` draft** (when the discovery gate fires, including any pre-existing discovery) — verified facts, terminology/workflow norms, assumptions, unknowns/source gaps, edge cases, failure modes, risks, and measurement seeds.
4. **Ideation output** (step 3, when the depth dial runs it — medium/hard) — the chosen approach + its rationale → §1 ¶3.
5. **Channel outputs** (step 5) — reference-module patterns, doc/MCP/KB quotes → §1 ¶4 traceability only.

## Discovery-to-spec contract

`discovery.md` is durable evidence, not an appendix that may be ignored. Carry each relevant result
into the current eight-section spec schema:

- verified facts, terminology, and workflow norms → §1 Context;
- external constraints and scope boundaries → §1 Context, §3 Non-goals, or §6 NFR/security;
- edge cases and required business responses → §5 Acceptance criteria where observable;
- failure modes and risks → §5, §6, §6.1, or §8 according to whether they are behavior, quality,
  security/privacy, or unresolved decisions;
- measurement/KPI seeds → §7 Metrics/KPIs;
- assumptions, unknowns, and `RESEARCH_LIMITED` source gaps → §1 as explicit uncertainty or §8
  with an owner and due point.

Do not cite a discovery assumption as fact. Do not paste every finding mechanically: include the
findings that change the problem, scope, observable behavior, constraints, risk, measurement, or an
unresolved decision.

## §5 acceptance-criteria contract

AC describes a **business-observable outcome from the actor's perspective**, in Given/When/Then. **No upper cap** — propose as many as needed so **every §4 user story has ≥1 AC** and all five coverage types appear (authorization may instead carry the explicit, sourced N/A below — the only waiver). If a `Drop` / `Save as Open Question` during Socratic leaves a coverage type empty **or a retained §4 user story with no AC**, regenerate a replacement AC and run a mini-batch on it (the two coverage floors, see [`socratic.md`](./socratic.md)). The «every US has ≥1 AC» rule is a **re-checked floor**, not only a draft-time target — it's verified after every §5 resolution, so `sequences` and `review` downstream can rely on each use-case having a testable criterion.

Five coverage types, ≥1 each:

1. **happy** — actor does the main flow → system records the outcome and confirms.
2. **error** — actor submits invalid input → system blocks it and explains the reason (phrase as «system shows the actor that <field> must be <constraint>»).
3. **authorization** — actor lacks permission (cross-tenant / cross-role / not-owner) → system denies access or hides existence; rationale in business terms.
4. **domain invariant** — actor violates a named invariant → system blocks the action and names the invariant in plain language.
5. **cross-context** — actor's action depends on state in another bounded context → system enforces the cross-context rule.

### Authorization N/A — the only coverage waiver (strict)

Authorization analysis is **always performed**; only its AC is waivable, and only by an
**explicit, sourced N/A**. A bare omission is a floor violation. The waiver is legal **only
when an authoritative upstream artifact — the committed approach (§1 ¶3), §3 Non-goals,
`discovery.md`, or a governing product doc named as a step-5 channel — explicitly excludes
authentication/roles/permissions from this feature or establishes a trust boundary that makes
authorization inapplicable** (e.g. «one trusted operator in a controlled installation; auth
deferred to a later iteration»). The exclusion must already be on record upstream — **do not
invent it to fill the type**; if no artifact says it, ask and record it as a §3 non-goal first.
When the N/A holds, write it in §5 as its own line — `**Authorization: N/A — <reason> (source:
<artifact + §ref>)` — and mirror the trust boundary in §6.1 (AuthZ/AuthN impact + abuse cases
reduced to the boundary) and §3 (a non-goal fencing off auth). A scope boundary that is not
about *who may act* (per-tenant limits, feature flags, input validation) is **not** authorization
— do not mislabel it to satisfy the floor.

## Forbidden tokens in §5 AC (stack-agnostic, zero tolerance)

Checked by the critic's F6 and the pre-write regex scan:

- **HTTP verbs**: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`.
- **URL paths**: anything starting with `/` then a lowercase identifier (`/orders`, `/items/{id}`, `/api/v1/...`).
- **status-code numerics** in the AC body: `200`, `201`, `400`, `401`, `403`, `404`, `409`, `5xx`, `500`, `503`.
- **error-code strings** matching `[a-z_]+\.[a-z_]+` (e.g. `order.not_owner`, `validation.title_too_long`).
- **JSON fragments / payload bodies**: `{title, description}`, `{id, status: "draft"}`.
- **SQL / DB constructs**: `UNIQUE(...)`, `FK`, raw `INSERT`/`SELECT`/`UPDATE`, constraint names — and any **driver/ORM-specific error type** (the stack-agnostic generalization of the old Go-only `pq.*`).

The technical mapping for all of these lives in `api` (HTTP method/path/status, error-code strings, payload schemas) and `data-model` / `decide-adr` (DB constructs). The spec's AC is WHAT a user can observe, not HOW the system encodes it.

## Stack-agnostic hygiene for §1–§3

The product-level sections must not name a **concrete technology** — a specific datastore, message broker, framework, or library. Those are `design` decisions. The old SDLC skill hard-coded a Go/Postgres regex (`Postgres|Redis|Kafka|JSONB`…); the stack-agnostic rule is: flag any proper-noun product/library name in the WHAT/WHY sections and move it to the design stage.

## Measurement applicability — the §6/§7 N/A waiver (strict, the authorization-N/A genre)

Numeric §6 targets and §7 KPI rows exist so decisions stay measurable — but some scenarios make
quantitative measurement **not yet meaningful**: a walking skeleton (prove the end-to-end path
exists, not that it is fast), a throwaway prototype or spike, an exploratory internal tool, a
feature whose outcome cannot be observed yet. Fabricating latency targets or vanity KPIs for
such a scenario is worse than declining them — numbers nobody will read become noise every
downstream stage must carry.

The waiver is legal **only** as an **explicit, sourced N/A**, exactly the §5 authorization genre:

- **Never silent.** An empty §6 table, §7 placeholder rows, or a bare omission is a floor
  violation, not a waiver.
- **Sourced.** The waiver line names the upstream artifact that establishes the scenario type —
  the committed approach (§1 ¶3, e.g. «walking skeleton: end-to-end path before any tuning»),
  a §3 non-goal, `discovery.md`, or the captured interview answer. Do not invent the scenario
  type to dodge measurement work; if no source says it, ask and record it in §1 ¶3 or §3 first.
- **Recoverable.** §8 carries a revisit open question with owner + due (or a trigger such as
  «before the first user-facing release» / «when the skeleton gains real traffic»), so the
  waiver converts back into numbers instead of quietly becoming permanent.
- **Aspect-scoped for §6.** Waive only the aspects the scenario truly makes meaningless
  (latency/throughput on a walking skeleton) and keep the ones that still bind (accuracy,
  durability, a safety guarantee). A whole-table §6 waiver needs the scenario type to justify
  every dropped row.
- **Honest toward discovery.** Live `discovery.md` §10 measurement seeds are evidence that
  measurement IS applicable — resolve each seed into a §7 row or defer it explicitly; the waiver
  may not silently discard them.

When the waiver holds, write it as its own line — `**Measurement: N/A — <reason> (source:
<artifact + §ref>)` — in place of the waived §7 table, or under the kept rows for an
aspect-scoped §6 waiver — and mirror the revisit in §8. Every downstream stage recognizes the
sourced line instead of re-flagging or re-inventing: `clarify`'s unmeasured-NFR class,
`design`'s §1 quality goals + §10 scenarios, `plan-tests`' measurement-readiness section.

## §7 product-measurement contract

Draft §7 as the compact KPI table in [`../templates/spec.md`](../templates/spec.md). Use the interview success criteria, discovery measurement seeds, ideation outcome metrics, and identified failure signals. Include only important product-outcome KPIs; do not add vanity counters to fill the table. When the scenario type makes outcome measurement not yet meaningful, apply the sourced measurement N/A above instead — never placeholder or vanity rows.

Each row requires: Metric, Why it matters, Source/event, Baseline, Target/timebox, Decision threshold, Owner, and When reviewed. The source/event must be something the team can actually observe, such as an analytics event, log, support tag, survey, or review ritual. The decision threshold must pair a condition after the timebox with a resulting choice such as ship, continue, iterate, rollback, stop, or investigate; «monitor» alone is not a decision. `Baseline = 0` is valid only when the current baseline is genuinely zero. An unknown or future-measured baseline is allowed only when the row says how it will be measured and §8 carries an owner+due to establish it.

## Pre-write hygiene (before Socratic)

- §4 US roles use CONTEXT glossary terms verbatim.
- §3 Non-goals each carry a reason (no inventing).
- §1 ¶3 states the committed approach without losing the vector.
- §5 has ≥1 of each coverage type (authorization may carry its explicit, sourced N/A — the only waiver) and 0 forbidden tokens (self-scan; the critic + regex are the backstop).
- §6 targets are numeric, or the aspect carries a sourced measurement N/A (above); §7 has ≥3 important KPI rows, or the sourced measurement N/A stands in place of the table — with no blank source/event, owner, decision threshold, or review timing; an unknown or future-measured baseline has a concrete baseline plan and matching §8 owner+due.
- When discovery fired, every relevant discovery result maps to a spec section, and no
  `RESEARCH_LIMITED` item is presented as verified fact.
