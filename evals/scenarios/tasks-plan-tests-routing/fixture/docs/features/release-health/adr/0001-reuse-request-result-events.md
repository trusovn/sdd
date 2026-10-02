---
status: Accepted
---

# 0001 — Reuse request-result events

## Context

Release health needs a trustworthy error-rate source without adding a second telemetry path.

## Decision

Calculate release health from the existing request-result events and require a freshness check
before treating a first-hour window as complete.

## Consequences

No new telemetry transport is needed. Delayed events must produce an incomplete result rather
than a healthy result.
