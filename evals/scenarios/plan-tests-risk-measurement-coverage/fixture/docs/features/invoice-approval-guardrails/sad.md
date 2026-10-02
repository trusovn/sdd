---
status: Draft
owner: "Tech Lead"
feature_size: "M"
target_surfaces: ["backend-service"]
---

# SAD — invoice-approval-guardrails

## 6. Runtime view

The invoice service checks current vendor compliance before recording release or denial in the
audit log.

## 11. Risks / technical debt

| ID | Risk / debt | Severity | Status | Handling |
|---|---|---|---|---|
| SAD-R1 | Approval workflow and vendor compliance can disagree during release | High | Open | re-check latest compliance state before clearing |
| SAD-R2 | Audit events are eventually consistent | Medium | Accepted | sample evidence before rollout and monitor reconciliation after rollout |
