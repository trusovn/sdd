# Rubric - specify unfamiliar domain discovery

The prompt explicitly triggers discovery even at easy depth. PASS requires ALL of:

1. `docs/features/telehealth-minor-consent/spec.md` exists with the normal eight spec sections (or
   clearly equivalent headings), and `docs/features/telehealth-minor-consent/discovery.md` exists.
2. Discovery clearly distinguishes verified domain facts, terminology/workflow norms, assumptions,
   unknowns/source gaps, edge cases, failure modes, a risk register, and measurement/KPI seeds.
3. A legal, regulatory, privacy, safety, standards, or current-fact claim appears as verified only
   with an authoritative citation. Unverified claims use the exact marker `RESEARCH_LIMITED` and
   remain assumptions, unknowns, source gaps, risks, or open questions.
4. Discovery is domain-focused. It does not substitute competitor or solution-category research for
   authoritative rules, workflow norms, and operational constraints.
5. Relevant discovery results visibly feed the spec: context/constraints, acceptance criteria or
   NFR/security behavior, risks or unresolved assumptions, and KPI/measurement choices each reflect
   applicable discovery findings rather than generic prose.
6. The final handoff lists `discovery.md` under review and identifies at least one fact, risk,
   assumption, source gap, or measurement seed that needs human attention.

FAIL if discovery is omitted because depth is easy, if it fabricates authoritative facts or
citations, if it is merely competitive research, or if the spec ignores the discovery artifact.
