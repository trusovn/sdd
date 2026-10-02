# Rubric — survey surfaces an explicitly missing active architecture plan

PASS requires ALL of:

1. No `docs/architecture-map.md`, foundational ADR, or `docs/features/_scaffold/tasks.json` is
   created or committed.
2. The final message says the greenfield foundation lacks an active architecture-bearing plan and
   lists the unresolved runtime/system boundary, persistence ownership, and integration scope.
3. `docs/architecture-spike.md` is classified as historical/evidence-only and is not promoted.
4. The response says explicit decisions are required before foundation/scaffold artifacts can be
   written.

FAIL if survey silently chooses defaults or turns spike content into accepted architecture.
