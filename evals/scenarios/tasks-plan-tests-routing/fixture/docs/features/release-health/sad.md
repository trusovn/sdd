---
status: approved
feature_size: S
target_surfaces: [backend-service]
---

# SAD — release-health

## 1. Introduction and goals

Calculate first-hour release health from the existing request-result event stream.

## 2. Constraints

Reuse the existing telemetry reader and deployment identifier.

## 3. Context and scope

The existing operator endpoint reads health calculated by the release service.

## 4. Solution strategy

Add a release-health calculation to the existing release service.

## 5. Building blocks

The release service reads request-result events, checks window completeness, and returns the
measured error rate plus healthy, unhealthy, or incomplete status.

## 6. Runtime

The operator requests health; the service loads first-hour events, rejects an incomplete window,
calculates the error rate, and compares it with the 1% threshold.

## 7. Deployment

<!-- N/A: existing deployment unit. -->

## 8. Crosscutting

Time windows use UTC and include their start and end timestamps in the result.

## 9. Architecture decisions

| ADR | Decision | Status |
|---|---|---|
| [0001](adr/0001-reuse-request-result-events.md) | Reuse request-result events for release health | Accepted |

## 10. Quality requirements

The same event window always yields the same status.

## 11. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Delayed events hide failures | high | return incomplete until the event-freshness check passes |

## 12. Glossary

Complete window — a first-hour event window whose freshness check has passed.
