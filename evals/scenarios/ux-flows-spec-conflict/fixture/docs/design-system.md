---
status: Living
tool: code
figma_file: ""
pen_file: ""
updated_at: 2026-09-01
---

# Design system — workspace

> The project's design canon — tool, posture, tokens, component inventory. Produced by
> `design-system`; read by `ux-flows` (posture) and `screens` (tool + inventory).

## Platform posture

- **Posture:** desktop-first — project leads work on laptops.

## Design tool

- **Tool:** code — screens are specified as inline markdown wireframes in each feature's screens.md

## Component inventory

| Component | Source | States it supports | Notes |
|---|---|---|---|
| Button | `web/src/components/Button.tsx:1` | default / disabled / loading | primary + ghost variants |
| Input | `web/src/components/Input.tsx:1` | default / error / disabled | inline validation message |
| Toast | `web/src/components/Toast.tsx:1` | info / error | auto-dismiss 4s |
