# specify — delta over the shared critic

Read [`../../_shared/critic.md`](../../_shared/critic.md) for the canonical dispatch and F1–F6 skeleton. specify supplies only the deltas below; the skill fills the placeholders and dispatches one clean-context `Agent`.

## Placeholders

- **`{{ARTIFACT_NAME}}`** = "Product spec plus conditional domain discovery".
- **`{{DRAFT}}`** = the in-memory `spec.md` draft plus the in-memory `discovery.md` draft when the discovery gate fired.
- **`{{EDITS_LOG}}`** = the step-7 edits-log.
- **`{{UPSTREAM_FILES}}`** (the critic Reads these itself):
  - `docs/features/<slug>/CONTEXT.md` — canonical glossary (roles, domain terms).
  - `docs/features/<slug>/discovery.md` — only when it existed before this run; a new discovery draft is inlined in `{{DRAFT}}` instead.
  - any reference module / doc the user named in step 5 (paths only).

## F5 structural floor (this artifact)

- §4 holds ≥1 US per glossary role + per §2 goal.
- §5 holds ≥1 AC of each of the 5 coverage types **after** drops + OQ-migrations — authorization may instead carry its explicit, sourced `Authorization: N/A` line (per [`draft-generation.md`](./draft-generation.md)); flag a missing authorization AC when no sourced N/A line stands in for it, and flag an N/A whose cited upstream artifact does not actually exclude auth or establish the trust boundary.
- §6 NFR rows all carry a numeric target + measurement (no adjectives, no lone TBD) **or** a sourced measurement N/A line (per [`draft-generation.md`](./draft-generation.md)) with its §8 revisit — flag a bare omission, an unsourced N/A, or an aspect-scoped waiver that drops an aspect the scenario type does not actually make meaningless (accuracy/durability on a walking skeleton).
- §7 has ≥3 important KPI rows in table form; every row fills Metric, Why it matters, Source/event, Baseline, Target/timebox, Decision threshold, Owner, and When reviewed. An unknown or future-measured baseline is valid only with a concrete source/event plan plus a §8 owner+due. Flag vanity counters, source-less rows, and thresholds that only say «monitor», «track», or «review» without a condition and resulting decision. **Or**, when the scenario type makes outcome measurement not yet meaningful, §7 carries its explicit, sourced `Measurement: N/A` line **plus a §8 revisit OQ with owner + due** — a sourced N/A with no revisit, or live `discovery.md` §10 seeds silently discarded by the waiver, are both findings. A bare omission is never the waiver.
- §8 Open Questions has a row for every `save_as_oq` with owner + due.
- When discovery fired, its draft distinguishes verified facts, terminology/workflow norms,
  assumptions, unknowns/source gaps, edge cases, failure modes, risks, and measurement seeds; each
  authoritative/current claim is cited or marked `RESEARCH_LIMITED`; relevant findings visibly
  inform the spec rather than remaining dead documentation.

## F6 specialization — forbidden-token leak (the load-bearing check)

This is specify's primary F6. Scan §5 AC text for the forbidden tokens in [`draft-generation.md`](./draft-generation.md) (HTTP verbs, URL paths, status numerics, `module.error_name` strings, JSON fragments, SQL/driver constructs). **List every hit**, one bullet per AC line:

```
- **[F6] AC-NN contains forbidden tokens** — line: "<verbatim snippet>"; hits: <token1>, <token2>; suggested: rewrite into business form (actor-observable outcome) OR move the HTTP/error/schema detail to `api`.
```

Also flag any concrete technology name (datastore / broker / framework / library) appearing in §1–§3 — those belong to `design`.

## F1 specialization — approach drift

If the edits-log dropped/edited a US or AC tied to the committed approach in §1 ¶3, check that §1 ¶3 still states that approach accurately. A spec whose body no longer matches its own «committed approach» paragraph is drift.
