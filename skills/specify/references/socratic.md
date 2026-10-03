# specify — delta over the shared Socratic loop

Read [`../../_shared/socratic-loop.md`](../../_shared/socratic-loop.md) for the canonical 4-state machine, edits-log, and disk-write discipline. specify supplies only the deltas below.

## Sections walked (in order)

§4 User stories → §5 Acceptance criteria → §6 NFR → §7 KPI rows. §1–§3 are drafted and shown but not per-item walked (they have no decision set — the user edits them inline if needed).

## Decision-types

- **User story** (§4) — Approve / Edit / Drop / Save-as-OQ. Dropping a US that owns the only AC of a coverage type triggers the §5 coverage gate.
- **Acceptance criterion** (§5) — the 4-state machine **plus a 5th option «Add another AC»** (user dictates a new AC; skill drafts it in business form and runs a one-question mini-batch on it). Dropping / OQ-migrating the **last AC of a retained §4 user story** fires the use-case floor below (regenerate an AC for that US).
- **NFR row** (§6) — Approve / Edit (change the number or measurement) / Save-as-OQ (number is TBD, owner+due). A bare adjective («fast») is never Approvable — force a number or an OQ. Exception: the sourced **measurement N/A** (per [`draft-generation.md`](./draft-generation.md) — the scenario type makes the aspect meaningless, e.g. latency on a walking skeleton); it replaces the row only as an explicit, sourced line with its §8 revisit, never as a silent drop.
- **KPI row** (§7) — Approve / Edit / Drop / Save-as-OQ. A row is not Approvable unless metric, why it matters, source/event, baseline, target/timebox, decision threshold, owner, and review timing are filled. An unknown or future-measured baseline forces a concrete source/event plan plus an OQ with owner+due; a bare `TBD` is never Approvable. The section-level alternative: the **measurement N/A** (per [`draft-generation.md`](./draft-generation.md)) — when the scenario type makes outcome measurement not yet meaningful, §7 resolves to its explicit, sourced `Measurement: N/A` line + a §8 revisit OQ instead of rows; propose it only when the source artifact (§1 ¶3 / §3 / discovery / interview answer) actually says so, and never use it to rescue rows nobody filled.

## Per-skill gate — §5 coverage floors (two, both re-checked after every resolution)

After every §5 resolution, re-check **both** floors below (OQ-migrated AC do NOT count toward either — they live in §8 now). Both are the specify analogue of `design`'s blast-radius gate; both hold at every interview depth.

1. **Coverage-type floor.** ≥1 AC of each of the 5 coverage types (happy / error / authorization / domain invariant / cross-context) still stands after drops + OQ-migrations. The one waiver: authorization may be satisfied by its explicit, sourced `Authorization: N/A` line (per [`draft-generation.md`](./draft-generation.md) — an authoritative upstream artifact excludes auth or establishes a trust boundary; the N/A line names that source). A silent gap in any type is a floor violation — regenerate a replacement AC and run a one-question mini-batch. Dropping the last authorization AC does **not** auto-invoke the waiver — the N/A must be re-established against the upstream artifact, else regenerate the AC.
2. **Use-case floor (§4 US → ≥1 §5 AC).** **Every *retained* §4 user story still has ≥1 acceptance criterion.** If a Drop / OQ-migration leaves a retained US with no AC, regenerate (or use the «Add another AC» option) an AC for that US and run a one-question mini-batch — a user story with no AC is incomplete and silently breaks the downstream `sequences` use-case coverage and `review`'s end-to-end trace. (Dropping the **whole** US is a legitimate de-scope and does not fire this floor — only a retained US losing its last AC does.) This also applies at **draft time**: if the initial §5 draft gave some §4 US no AC, add one before the walk begins.

## Open-Questions table

`save_as_oq` rows land in **§8 Open questions** as a checkbox line: `- [ ] <headline>? — owner: <…>, due: <…>`. Owner + due mandatory; missing either downgrades to Drop.
