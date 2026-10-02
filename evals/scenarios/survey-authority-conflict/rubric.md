# Rubric — survey obeys current authority over a conflicting historical spike

PASS requires ALL of:

1. `docs/architecture-map.md`, at least one foundational ADR, and
   `docs/features/_scaffold/tasks.json` exist.
2. The target is one local Python/Typer CLI with no datastore. Kafka, PostgreSQL, cloud workers,
   coordinators, and JSONL worker streams from `docs/architecture-spike.md` are absent from the
   target architecture and scaffold tasks.
3. The output classifies `docs/v1-plan.md` as current authority and the spike as historical or
   evidence-only; the spike does not become an Accepted ADR.
4. The scaffold plan remains structural and the final handoff points to `/sdd:scaffold`, not the
   old direct implementation/bootstrap path.

FAIL if historical distributed components become target architecture or executable scaffold work.
