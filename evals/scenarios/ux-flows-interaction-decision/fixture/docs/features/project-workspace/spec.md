---
status: approved
updated_at: 2026-09-03
feature_size: S
---

# Project workspace — create projects and environments

## 1. Context

The walking skeleton for a deployment workspace: a project lead creates a Project, then can
create an Environment under it. The spec establishes Project creation but deliberately leaves
the post-success transition (does Environment creation auto-start? does the new Project become
active?) unspecified — that interaction behavior is resolved by `ux-flows`.

## 2. Goals

- A project lead can create a Project and see it in the project list.
- A project lead can create an Environment under an existing Project.

## 3. Non-goals

- Editing or archiving Projects/Environments.
- Sharing Projects between accounts.

## 4. User stories

- US-01: As a project lead, I want to create a Project so I can organize work under it.
- US-02: As a project lead, I want to create an Environment so a Project can run in it.

## 5. Acceptance criteria

- AC-01 (happy): Given a non-empty project name, when I create the Project, then it is saved and
  appears in the project list.
- AC-02 (error): Given an empty project name, when I try to create the Project, then creation is
  rejected with a message naming the problem and nothing is stored.
- AC-03 (happy): Given an existing Project, when I create an Environment for it, then the
  Environment is saved and listed under that Project.
- AC-04 (error): Given an Environment name already used in that Project, when I try to create it,
  then creation is rejected with a message and the existing Environment is unchanged.

## 6. Non-functional requirements

- Creating a Project completes within 1 second on a mid-range laptop (p95, measured in the web
  app's performance monitoring).

## 7. KPIs

- ≥ 50% of signed-in leads who create a Project also create an Environment within 30 days.

## 8. Open questions

_None._
