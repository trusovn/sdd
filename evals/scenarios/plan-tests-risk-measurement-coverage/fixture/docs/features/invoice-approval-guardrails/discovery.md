# Discovery — invoice-approval-guardrails

## 7. Edge Cases

| Edge case | Expected product behavior | Where to carry it |
|---|---|---|
| A vendor hold arrives after invoice review starts | Re-check before release | AC-05 |

## 8. Failure Modes

| Failure mode | User/business impact | Detection signal | Mitigation seed |
|---|---|---|---|
| Stale vendor state permits release | Non-compliant payment | freshness metric | re-check at release |
| Denied attempt lacks audit evidence | Abuse cannot be reconstructed | reconciliation gap | record denials |

## 9. Risk Register

| ID | Risk | Severity | Trigger | Handling or next decision | Owner | Status |
|---|---|---|---|---|---|---|
| RISK-01 | Stale vendor-compliance state permits invalid release | High | hold changes during review | verify release re-check and freshness signal | Tech Lead | Open |
| RISK-02 | Denied attempts are missing from audit evidence | Medium | audit write delayed or lost | verify denial evidence and sampling | Finance Auditor | Open |
| RISK-03 | Conservative holds delay legitimate invoices | Low | false-positive holds | monitor pilot review time | Finance Ops PM | Open |

## 10. Measurement / KPI Seeds

| Signal | Why it matters | Possible source/event | Baseline status | Decision it informs |
|---|---|---|---|---|
| Blocked releases | Detect unauthorized attempts | `invoice_release_blocked` | no current event | rollback/iterate |
| Review duration | Detect workflow delay | `invoice_review_completed` | establish in pilot | continue/iterate |
| Audit reconciliation | Detect missing evidence | reconciliation report | no current report | continue/stop |
