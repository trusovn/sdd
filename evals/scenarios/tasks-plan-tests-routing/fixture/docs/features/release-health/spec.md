---
status: approved
---

# Release health

## 1. Context

Operators can deploy a release, but they cannot tell whether its error rate stayed healthy during
the first hour. The service already emits request-result events.

## 2. Goals

- Show operators whether the current release remains inside its agreed error-rate threshold.

## 3. Non-goals

- Automated rollback.
- A new telemetry transport.

## 4. User stories

- US-01: As an operator, I can inspect first-hour release health so I can decide whether to keep
  or roll back the release.

## 5. Acceptance criteria

- AC-01 (happy): Given a release with an error rate below 1%, when the operator checks release
  health, then the release is reported healthy with the measured rate and observation window.
- AC-02 (boundary): Given a release with an error rate at or above 1%, when the operator checks
  release health, then the release is reported unhealthy with the measured rate.

## 6. Non-functional requirements

### 6.1 Security and risk register

| Risk | Severity | Treatment |
|---|---|---|
| RISK-01 — delayed request-result events can make a bad release look healthy | High | verify event freshness and expose incomplete windows before release decisions |

## 7. KPIs

| ID | Metric | Source/event | Baseline | Target/timebox | Decision threshold | Owner | When reviewed |
|---|---|---|---|---|---|---|---|
| KPI-01 | releases with complete first-hour health evidence | request-result event | unknown; measure current completeness before implementation | 99% within 30 days | below 99% triggers instrumentation repair before rollout expands | SRE lead | weekly during rollout |

## 8. Open questions

(none)
