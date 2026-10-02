# Rubric — tasks always routes through plan-tests

The fixture is a quick-route feature with an important retained risk and KPI. Its task convention
requires each generated DoD to name a specific test. PASS requires ALL of:

1. `docs/features/release-health/tasks.json` exists and is valid JSON; every task has a non-empty
   `dod`, and every `dod` names a test or test command.
2. The generated task markdown and tracker artifacts required by the tasks skill exist.
3. The final stage-handoff routes next to `/sdd:plan-tests release-health`. It may mention that
   `/sdd:implement release-health` follows the plan, but it must not offer or take a direct
   tasks-to-implement skip.
4. The handoff preserves quick-route behavior by saying the test plan will be the lightweight
   inline form in `spec.md`; it does not request a separate `test-plan.md`.

FAIL if naming tests in every task DoD causes `plan-tests` to be auto-skipped, offered as an N/A
skip, or replaced by a direct `/sdd:implement release-health` next step.
