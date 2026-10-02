# Rubric — empty CLI repository follows survey to scaffold

PASS requires ALL of:

1. `docs/architecture-map.md`, foundational ADRs, and `docs/features/_scaffold/tasks.json` exist
   and reflect the prompt-confirmed Node.js/TypeScript CLI foundation.
2. The scaffold plan contains only structural repository work: package/entry point, test/lint/build
   harness, CI, README, and repo-local rules. It contains no product behavior or persistence task.
3. The final stage handoff points to `/sdd:scaffold`, which materializes the skeleton; it does not
   restore the old direct `implement` bootstrap path.

FAIL if survey stops merely because the repo is empty, invents persistence, adds product behavior,
or bypasses the current scaffold skill.
