---
status: Draft
owner: "<feature owner>"
updated_at: "<today YYYY-MM-DD>"
trigger: "<trigger reasons>"
---

# Discovery - <slug>

<!-- instruction:
Write this artifact only when specify's discovery gate fires. Keep verified facts, assumptions,
unknowns, and source gaps distinct. Prefer authoritative/current sources. If required research
cannot be completed, use the exact marker RESEARCH_LIMITED and never invent a citation. Keep
competitive research out; it belongs to the researcher/ideation flow. -->

## 1. Why Discovery Was Needed

<!-- instruction: Name every applicable trigger and its planning consequence. -->

- <trigger and why it matters>

## 2. Verified Domain Facts

<!-- instruction: Only sourced facts belong here. An unverified claim is an assumption or source
gap, not a fact. -->

| Fact | Authoritative source | Planning impact |
|---|---|---|
| <verified rule, standard, or constraint> | <citation/path and access date> | <scope/spec consequence> |

## 3. Terminology And Workflow Norms

<!-- instruction: Record canonical domain language and normal actor/object/state flow. -->

| Term or norm | Meaning or normal flow | Source |
|---|---|---|
| <term or norm> | <plain-language meaning> | <citation/path or RESEARCH_LIMITED> |

## 4. Assumptions

<!-- instruction: Working beliefs that are not verified facts. Every material assumption needs an
owner and a decision point because being wrong could change scope or behavior. -->

| Assumption | Impact if wrong | Owner | Revisit by |
|---|---|---|---|
| <assumption> | <scope/behavior impact> | <role/name> | <stage/date> |

## 5. Unknowns And Source Gaps

<!-- instruction: Separate an unknown question from why evidence is missing. Use RESEARCH_LIMITED
whenever authoritative research was required but could not be completed. -->

| Unknown | Why it matters | Source gap / next evidence | Owner |
|---|---|---|---|
| <unknown> | <decision impact> | <RESEARCH_LIMITED - reason, or evidence to obtain> | <role/name> |

## 6. Authoritative Sources

<!-- instruction: List sources actually used and the facts they support. Do not list a search result
that was not inspected. Write `RESEARCH_LIMITED - <reason>` when no authoritative source was
available. -->

- <source title> - <URL/path/query>, accessed <YYYY-MM-DD>, supports <facts>

## 7. Edge Cases

| Edge case | Expected product behavior | Where to carry it |
|---|---|---|
| <domain exception or unusual actor/state> | <business response> | <spec AC / NFR / open question> |

## 8. Failure Modes

| Failure mode | User/business impact | Detection signal | Mitigation seed |
|---|---|---|---|
| <operational/product failure> | <impact> | <observable signal> | <prevention or response> |

## 9. Risk Register

<!-- instruction: Preserve risks that later specification, design, test planning, or rollout must
handle. Status is Open, Accepted, or Mitigated. -->

| ID | Risk | Severity | Trigger | Handling or next decision | Owner | Status |
|---|---|---|---|---|---|---|
| RISK-01 | <risk> | <High/Medium/Low> | <what makes it real> | <action/decision> | <role/name> | <Open/Accepted/Mitigated> |

## 10. Measurement / KPI Seeds

<!-- instruction: These are observable candidates for spec §7, not final KPIs. Connect every seed
to a success claim, assumption, failure mode, or risk. -->

| Signal | Why it matters | Possible source/event | Baseline status | Decision it informs |
|---|---|---|---|---|
| <metric or qualitative signal> | <linked claim/risk> | <event/metric/review source> | <known or plan to establish> | <ship/iterate/stop/investigate> |
