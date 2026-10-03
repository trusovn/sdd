# Rubric — ux-flows-code-mode

The fixture commits `docs/design-system.md` (`tool: code`, **mobile-first** posture) and a UI
feature spec (`saved-searches`: 3 user stories, 6 ACs incl. error / authorization /
duplicate-name / empty-state). A correct headless run (`--depth=easy`) derives the flows without
asking anything and hands off forward to `design`.

PASS requires ALL of:

1. `docs/features/saved-searches/ux-flows.md` exists and carries the template's sections:
   Platform decisions, Interaction decisions, Screen inventory, Flows, AC coverage.
2. Every diagram is a mermaid `flowchart` (never a `sequenceDiagram`) and parses — balanced
   syntax, no orphan nodes; each flow is followed by a prose account of its path + branches.
3. The Screen inventory uses `SCR-NN` ids, and every SCR id referenced by a flow node exists in
   the inventory.
4. Each of US-1 / US-2 / US-3 has a flow, and the error / authorization / duplicate-name /
   empty-state ACs (AC-2 / AC-3 / AC-4 / AC-5) appear as alt/error branches or nodes — never
   silently missing.
5. The AC-coverage table maps **every** §5 AC (AC-1…AC-6) to a flow/node/branch, or an explicit
   N/A with a one-line reason.
6. The Platform decisions section reflects **mobile-first** (from `docs/design-system.md`) — not
   desktop-first, not re-asked, no contradiction of the committed posture.
7. Every resolved flow-altitude interaction choice carries a `UXD-NN` row in Interaction
   decisions with a valid Source value (`user-confirmed` / `easy assumption` / `spec §<ref>`), and
   no `UXD-NN` row records behavior contradicting a retained AC. A `UXD-NN` row that pins
   post-success / navigation behavior (e.g. an explicit exclusion) is **preserved in the flows** —
   no flow re-introduces a transition the ledger excluded.
8. The run committed its work, and the final message contains the stage-handoff block
   (What I did / Review before continuing / Run next) forwarding to `/sdd:design saved-searches`.

FAIL on: a refusal, an attempted `AskUserQuestion`, a missing or unparseable mermaid block, a
user story with no flow, an AC absent from the coverage table, a desktop-first assumption, a
UXD row contradicting a retained AC, a flow re-introducing a transition a UXD row excluded, or a
missing handoff block.
