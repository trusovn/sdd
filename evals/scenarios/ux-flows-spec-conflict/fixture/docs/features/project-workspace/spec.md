---
status: approved
updated_at: 2026-09-03
feature_size: S
---

# Project workspace — create projects and environments

## 1. Context

The walking skeleton for a deployment workspace: a project lead creates a Project, then
creates an Environment under it.

## 2. Goals

- A project lead can create a Project and immediately start setting up its Environment.
- A project lead can create an Environment under an existing Project.

## 3. Non-goals

- Editing or archiving Projects/Environments.

## 4. User stories

- US-01: As a project lead, I want to create a Project so I can organize work under it.
- US-02: As a project lead, I want to create an Environment so a Project can run in it.

## 5. Acceptance criteria

- AC-01 (happy): Given a non-empty project name, when I create the Project, then it is saved and
  appears in the project list.
- AC-02 (error): Given an empty project name, when I try to create the Project, then creation is
  rejected with a message naming the problem and nothing is stored.
- AC-03 (happy): Given a Project was just created successfully, when the Project save completes,
  then Environment creation opens automatically so the lead can proceed without hunting for it.
- AC-04 (happy): Given an existing Project, when I create an Environment for it, then the
  Environment is saved and listed under that Project.
- AC-05 (error): Given an Environment name already used in that Project, when I try to create it,
  then creation is rejected with a message and the existing Environment is unchanged.

## 8. Open questions

_None._
