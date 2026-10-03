# Diagram presentation — how to make a Mermaid diagram inspectable by a human

> **Reference-only.** Not a skill. Any skill that produces a Mermaid diagram and needs a human to
> review it (`design` C4 §3/§5, `sequences` §6 flows, `ux-flows` flowcharts; others may adopt it)
> follows this. The rule it enforces: **never paste raw Mermaid source into the terminal as the
> thing to review.** Raw `sequenceDiagram` / `C4Context` source is unreadable in a chat box — the
> user can't judge a flow from `participant A as …` lines. Make the diagram inspectable by a
> **plain-language description** of what it shows, while the actual source lands in the file (where
> Obsidian renders it) and, if a renderer is available, an image.

## Why

A dogfood run pasted raw `sequenceDiagram` blocks as the confirmation prompt. The user can't read arrows-as-text; they approve blind or get frustrated. The fix separates two concerns: the **source** goes where it renders (the `.md` file, an optional image), and the **review surface** is prose the user can actually evaluate.

This composes with [`mermaid-check.md`](./mermaid-check.md) (which answers «does it parse?») and [`interview-depth.md`](./interview-depth.md) (which answers «how much should be asked, for which skill type?»). This file answers only «how do I present a diagram so a human can inspect it?».

## Procedure (per diagram)

1. **Write the diagram to its file first.** The `sad.md` §6 flow, the §3 C4Context block, etc. — that's where Obsidian renders it natively, so writing-first means the user can flip to the rendered view immediately. (This reverses the old «show then write» order: in practice «show» dumped raw source. Write-first makes the file the render surface.)
2. **Validate it parses** per [`mermaid-check.md`](./mermaid-check.md) (render-parse with `mmdc` if available, else the structural lint). A diagram that doesn't parse is never presented — fix it first.
3. **Explain it in prose** — the review surface is a plain-language account of what the diagram shows, not its source. Name the participants in words and walk the flow as a sentence or two, **including the key branches**. Example for a sequence flow:
   > «Flow 1 — read preferences: the member asks for their prefs → the handler asks the service → the service reads the store; if there's no saved row, it returns the on-by-default state instead of an error.»
   For a C4 view: «The Context shows the member and the admin talking to the Preferences system, which depends on the existing Identity system for who's-allowed and writes to one datastore.» Cover every actor/participant and every `alt`/`else` branch in words.
4. **Render an image if a renderer is available.** If `mmdc` (mermaid-cli) is on PATH (or `npx -y @mermaid-js/mermaid-cli`), **also** render the block to an image and reference its path so non-Obsidian users can see it too:
   ```bash
   mmdc -i docs/features/<slug>/sad.md -o docs/features/<slug>/_diagrams/<name>.png 2>&1   # one image per diagram, or per file
   ```
   Mention the path in the prose («rendered to `_diagrams/flow-1.png`»). If no renderer is available, the file + the prose description are enough — say so, don't block (graceful fallback, like the `mmdc` path in `mermaid-check.md`).

## Approval policy belongs to the consuming skill

This reference defines **presentation only**. After write → validate → prose-description, the **caller** decides what happens next. The caller decides whether the diagram:

- **requires explicit approval** — the skill asks the user to confirm it (e.g. design's four-state decision-validation on the C4 views, sequences' per-flow Accept / Fix / Save-as-OQ / Drop);
- **follows an already-resolved decision** and needs only a summary — the diagram merely renders a choice the user already made, so a one-line recap is enough;
- **or exposes unresolved domain behavior** that must be decided before the diagram is finalized — the skill asks about those forks, not about the drawing itself.

Do not infer approval semantics from this file. Depth policy (easy / medium / hard), question phrasing, and the 4-state action set live in their owning documents: [`interview-depth.md`](./interview-depth.md), [`ask-style.md`](./ask-style.md), [`socratic-loop.md`](./socratic-loop.md).

## Discipline

- **Never** make the raw Mermaid source the default review surface — that's the anti-pattern this file exists to kill. (If the user explicitly asks to see the source, show it; but the *default* channel is prose.)
- **Write before you present** — the file is the render surface; presenting before writing means there's nothing for the user to flip to.
- **Describe every branch**, not just the happy path — an `alt`/`else`/dead-letter branch the prose skips is a branch the user cannot inspect, review, or verify (whatever the caller's approval policy then does with it).
- **Validate before you describe** — never describe (or render an image of) a diagram that doesn't parse; fix it per `mermaid-check.md` first.
- The prose is for the user; the source is for the file and `data-model`/downstream. Keep the two channels separate.

## Where each skill calls this

- `design`     → presentation + design-owned decision confirmation (the §3/§5 C4 views walk design's existing four-state machine at medium/hard)
- `sequences`  → presentation + sequences-owned runtime-flow confirmation (per-flow Accept / Fix / Save-as-OQ / Drop at medium/hard)
- `ux-flows`   → presentation after UX behavior has been resolved (flows are behavior-resolution evidence, not architectural decisions)

Each keeps only a one-line «present per [`diagram-presentation.md`]» pointer; the presentation procedure lives here, the approval policy lives with the owning skill.
