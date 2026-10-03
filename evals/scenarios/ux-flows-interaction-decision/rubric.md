# Rubric — ux-flows-interaction-decision

The fixture is a walking-skeleton workspace spec (`project-workspace`: US-01 Create Project,
US-02 Create Environment) whose post-success transition is deliberately unspecified; the prompt
supplies the intended interaction decision (no automatic Environment creation; the new Project
becomes active). A correct headless run records the decision in the UXD ledger and draws flows
that honor it, without ever asking.

PASS requires ALL of:

1. `docs/features/project-workspace/ux-flows.md` exists with the template's sections: Platform
   decisions, Interaction decisions, Screen inventory, Flows, AC coverage.
2. `## Interaction decisions` carries a `UXD-01` row recording the explicit interaction decision
   — successful Project creation does NOT automatically open or prompt Environment creation —
   with a valid Source value (`user-confirmed`, matching the prompt's stated decision) and
   `Applies to` naming US-01 (or equivalent). The row never contradicts a retained AC.
3. US-01's flow ends at the intended Project state (the newly created Project active / its
   context visible — per the prompt), not on an unrelated surface.
4. No automatic edge runs from successful Project creation into Environment creation — US-01's
   happy path does not auto-start or auto-prompt the Environment flow, in the mermaid source AND
   in the prose account.
5. US-02 still exists as its own flow (Environment creation remains separately available), with
   its AC-demanded error branch (duplicate-name rejection, AC-04).
6. The Screen inventory uses `SCR-NN` ids and every SCR id referenced by a flow node exists in
   the inventory (the Environment screen may exist as a separate reachable screen — it is just
   not the automatic exit of US-01).
7. The AC-coverage table maps **every** §5 AC (AC-01…AC-04) to a flow/node/branch or an explicit
   N/A with a one-line reason.
8. Every diagram is a mermaid `flowchart` and parses — balanced syntax, no orphan nodes; each
   flow is followed by a prose account of its path + branches.
9. The run committed its work, and the final message contains the stage-handoff block
   (What I did / Review before continuing / Run next) forwarding to `/sdd:design project-workspace`.

FAIL on: a refusal, an attempted `AskUserQuestion`, a missing or unparseable mermaid block, a
missing UXD-01 row or a UXD row contradicting a retained AC, an automatic US-01 → Environment
edge in the diagram or its prose, US-02 missing or merged into US-01, an SCR id referenced but
absent from the inventory, an AC absent from the coverage table, or a missing handoff block.
