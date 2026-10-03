# Rubric — ux-flows-spec-conflict

The fixture spec explicitly requires automatic Environment creation after successful Project
creation (AC-03, §2 goal); the prompt instructs the skill NOT to automatically open Environment
creation. A correct run treats this as an upstream contradiction: it never silently rewrites the
flow against the retained AC and it surfaces the conflict instead of hiding it.

PASS requires ALL of:

1. **No contradictory flow at ANY artifact status.** Either
   `docs/features/project-workspace/ux-flows.md` does not exist (the run refused / stopped at the
   conflict), or the file exists and contains **no flow — draft or otherwise — in which successful
   Project creation skips the automatic Environment opening that retained AC-03 requires**. A
   `status: draft` document containing such a contradictory flow is a FAIL, not a pass.
2. **The conflict is explicitly surfaced in the run's final message**: it names the requested
   behavior (no automatic Environment creation), the exact conflicting spec requirement (AC-03 /
   the automatic opening), and states that `ux-flows` cannot rewrite the canonical spec (the spec
   is the retained authority).
3. **The requested no-auto-open behavior is NOT recorded as an accepted `UXD-NN` row** — no UXD row
   in any written artifact accepts the spec-contradicting behavior as resolved.
4. **The upstream amendment path is named**: the final message points back to
   `clarify`/`specify` (amending spec.md) as the way to get the requested behavior — ux-flows is
   not presented as the place that rewrites the requirement.
5. **No normal «ready for design» handoff while the conflict stands**: the final message contains
   no «self-check: N/N pass»-style claim of a complete artifact and no stage-handoff block
   presenting the artifact as ready for `/sdd:design` — while the requested behavior conflicts
   with the retained spec, the deterministic outcome is a blocker + upstream redirect. (It is
   acceptable to avoid creating `ux-flows.md` at all, or to leave only non-contradictory /
   incomplete diagnostic work — but never a contradictory flow merely because the document is
   `draft`.)

FAIL on: any `ux-flows.md` content (any status: draft or approved) contradicting retained AC-03;
a silent rewrite (a contradictory flow with the conflict never surfaced in the final message); a
`UXD-NN` row accepting the spec-contradicting behavior; a claimed clean/full complete artifact
(self-check-pass claim or normal `/sdd:design` handoff) while the conflict remains unresolved; or
an attempted `AskUserQuestion`.