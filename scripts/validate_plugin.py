#!/usr/bin/env python3
"""Validate the SDD Claude Code plugin.

Checks the plugin manifest + marketplace manifest agree on name / version / description,
that the version is semver, and that every triggering skill and agent carries the required
frontmatter. Run from the repo root:

    python3 scripts/validate_plugin.py

Exits non-zero on the first category of failures (CI gate). Prints one line per check.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")

errors: list[str] = []
checks = 0


def check(ok: bool, ok_msg: str, fail_msg: str) -> bool:
    global checks
    checks += 1
    if ok:
        print(f"  ok   {ok_msg}")
    else:
        print(f"  FAIL {fail_msg}")
        errors.append(fail_msg)
    return ok


def flat(path: Path) -> str:
    """Whitespace-normalised body, lowercased — for contract-phrase substring tests.

    A contract phrase like «stage-handoff block» is prose, so a writer is free to
    wrap it across a line. A raw substring test then fails on a purely typographic
    choice, which is exactly what turned the v2.1.0 release red. Collapse every run
    of whitespace to a single space before testing.
    """
    return " ".join(path.read_text().split()).lower()


def load_json(rel: str):
    path = ROOT / rel
    if not path.exists():
        errors.append(f"{rel} is missing")
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        errors.append(f"{rel} is not valid JSON: {exc}")
        return None


def read_frontmatter(path: Path) -> dict[str, str]:
    """Return the top-level scalar keys of a leading --- YAML frontmatter block."""
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    fm: dict[str, str] = {}
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm


def markdown_tables(path: Path) -> list[tuple[str, tuple[str, ...], list[tuple[str, ...]]]]:
    """Return Markdown tables as (section heading, header cells, body rows)."""
    lines = path.read_text().splitlines()
    tables: list[tuple[str, tuple[str, ...], list[tuple[str, ...]]]] = []
    heading = ""
    i = 0

    def cells(line: str) -> tuple[str, ...]:
        return tuple(re.sub(r"[`*_]", "", cell).strip().lower()
                     for cell in line.strip().strip("|").split("|"))

    def separator(line: str) -> bool:
        parts = cells(line)
        return bool(parts) and all(re.fullmatch(r":?-{3,}:?", part) for part in parts)

    while i < len(lines):
        heading_match = re.match(r"^#{1,6}\s+(?:\d+(?:\.\d+)*\.?\s+)?(.+?)\s*$", lines[i])
        if heading_match:
            heading = re.sub(r"[`*_]", "", heading_match.group(1)).strip().lower()
        if (lines[i].lstrip().startswith("|") and i + 1 < len(lines)
                and separator(lines[i + 1])):
            header = cells(lines[i])
            rows: list[tuple[str, ...]] = []
            i += 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            tables.append((heading, header, rows))
            continue
        i += 1
    return tables


def markdown_headings(path: Path) -> set[str]:
    """Return normalised Markdown heading names without numeric section prefixes."""
    headings: set[str] = set()
    for line in path.read_text().splitlines():
        match = re.match(r"^#{1,6}\s+(?:\d+(?:\.\d+)*\.?\s+)?(.+?)\s*$", line)
        if match:
            headings.add(re.sub(r"[`*_]", "", match.group(1)).strip().lower())
    return headings


def table_row(path: Path, first_cell: str) -> tuple[str, ...]:
    """Return the first table row whose first cell matches first_cell."""
    wanted = first_cell.lower()
    for _heading, _header, rows in markdown_tables(path):
        for row in rows:
            if row and row[0] == wanted:
                return row
    return ()


def main() -> int:
    print("== manifests ==")
    plugin = load_json(".claude-plugin/plugin.json")
    market = load_json(".claude-plugin/marketplace.json")
    if plugin is None or market is None:
        for e in errors:
            print(f"  FAIL {e}")
        print(f"\nFAILED: {len(errors)} error(s)")
        return 1

    # --- plugin.json: name / version / description ---
    name = plugin.get("name", "")
    version = plugin.get("version", "")
    desc = plugin.get("description", "")
    check(name == "sdd", "plugin name is 'sdd'", f"plugin name is {name!r}, expected 'sdd'")
    check(bool(SEMVER.match(version)), f"plugin version {version!r} is semver", f"plugin version {version!r} is not semver X.Y.Z")
    check(len(desc) >= 50, f"plugin description present ({len(desc)} chars)", f"plugin description too short ({len(desc)} chars)")
    check(bool(plugin.get("license")), "plugin declares a license", "plugin.json has no license")
    auth = plugin.get("author")
    auth_name = auth if isinstance(auth, str) else (auth.get("name") if isinstance(auth, dict) else None)
    check(bool(auth_name), "plugin declares an author", "plugin.json has no author")

    # --- manifest schema FIELD TYPES (Claude Code's loader rejects wrong types) ---
    repo = plugin.get("repository")
    check(repo is None or isinstance(repo, str),
          "plugin repository is a string (or absent)",
          "plugin.json `repository` must be a STRING URL, not an object {type,url} — Claude Code's manifest schema rejects the object form")
    check(plugin.get("homepage") is None or isinstance(plugin.get("homepage"), str),
          "plugin homepage is a string (or absent)", "plugin.json `homepage` must be a string")
    check(auth is None or isinstance(auth, (str, dict)),
          "plugin author is a string or object (or absent)", "plugin.json `author` must be a string or object")

    # --- marketplace.json: agrees with plugin.json on name / version / description ---
    print("== marketplace ==")
    plugins = market.get("plugins", [])
    entry = next((p for p in plugins if p.get("name") == "sdd"), None)
    if check(entry is not None, "marketplace lists the 'sdd' plugin", "marketplace.json has no plugin named 'sdd'"):
        check(entry.get("version") == version,
              f"marketplace version matches plugin.json ({version})",
              f"marketplace version {entry.get('version')!r} != plugin.json {version!r}")
        check(bool(entry.get("description")), "marketplace entry has a description", "marketplace 'sdd' entry has no description")
        check(bool(entry.get("source")), "marketplace entry has a source", "marketplace 'sdd' entry has no source")

    # --- cross-tool manifests: the Codex + Cursor mirrors carry the same name + version ---
    # v1.9.0 ships .codex-plugin/ + .agents/plugins/ (Codex CLI) and .cursor-plugin/ (Cursor);
    # a version bump that misses one of them would silently publish a stale manifest.
    print("== cross-tool manifests ==")

    def load_tool_manifest(rel: str):
        path = ROOT / rel
        if not check(path.exists(), f"{rel} exists", f"{rel} is missing"):
            return None
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            check(False, "", f"{rel} is not valid JSON: {exc}")
            return None

    for rel in (".codex-plugin/plugin.json", ".cursor-plugin/plugin.json"):
        data = load_tool_manifest(rel)
        if data is None:
            continue
        check(data.get("name") == "sdd", f"{rel} name is 'sdd'",
              f"{rel} name is {data.get('name')!r}, expected 'sdd'")
        check(data.get("version") == version,
              f"{rel} version matches plugin.json ({version})",
              f"{rel} version {data.get('version')!r} != plugin.json {version!r}")

    codex_market = load_tool_manifest(".agents/plugins/marketplace.json")
    if codex_market is not None:
        check(codex_market.get("name") == "sdd",
              ".agents marketplace name is 'sdd'",
              f".agents marketplace name is {codex_market.get('name')!r}, expected 'sdd'")
        cm_entry = next((p for p in codex_market.get("plugins", []) if p.get("name") == "sdd"), None)
        check(cm_entry is not None and bool(cm_entry.get("source")),
              ".agents marketplace lists the 'sdd' plugin with a source",
              ".agents/plugins/marketplace.json has no 'sdd' plugin entry with a source")
        # Codex CANNOT install a plugin whose local path is the marketplace root: it strips `./`
        # and rejects the empty remainder (codex-rs marketplace.rs, resolve_local_plugin_source_path)
        # — the entry is silently skipped and the marketplace lists zero plugins. The self-marketplace
        # therefore must use the git `url` object form pointing back at this repo.
        cm_src = (cm_entry or {}).get("source")
        check(isinstance(cm_src, dict) and cm_src.get("source") == "url"
              and str(cm_src.get("url", "")).startswith("https://github.com/"),
              ".agents marketplace 'sdd' source is the git url form (root-local './' is uninstallable in codex)",
              f".agents marketplace 'sdd' source must be {{'source': 'url', 'url': 'https://github.com/…'}} — "
              f"codex silently skips a root-local './' plugin; got {cm_src!r}")

    installer = ROOT / "install.sh"
    check(installer.exists() and installer.read_text().startswith("#!/usr/bin/env bash"),
          "install.sh exists and is a bash script (#!/usr/bin/env bash)",
          "install.sh is missing or lacks the #!/usr/bin/env bash shebang")

    VALID_MODELS = {"haiku", "sonnet", "opus", "fable", "inherit"}
    VALID_EFFORTS = {"low", "medium", "high", "xhigh", "max"}
    agent_names = {p.stem for p in (ROOT / "agents").glob("*.md")}

    def parse_list(v: str) -> list[str]:
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = v[1:-1]
        return [x.strip() for x in v.split(",") if x.strip()]

    def check_profile(label: str, fm: dict, require: bool, require_agents: bool = False):
        """Validate model/effort/agents attributes if present (required on skills)."""
        m, e = fm.get("model"), fm.get("effort")
        if require:
            check(m is not None, f"{label} declares model", f"{label} is missing the model attribute")
            check(e is not None, f"{label} declares effort", f"{label} is missing the effort attribute")
        if require_agents:
            check(fm.get("agents") is not None,
                  f"{label} declares agents",
                  f"{label} is missing the agents attribute (use `agents: []` when it spawns none)")
        if m is not None:
            check(m in VALID_MODELS or "-" in m or "." in m,
                  f"{label} model {m!r} is valid", f"{label} model {m!r} not in {sorted(VALID_MODELS)} or a full id")
        if e is not None:
            check(e in VALID_EFFORTS or e.isdigit(),
                  f"{label} effort {e!r} is valid", f"{label} effort {e!r} not in {sorted(VALID_EFFORTS)} or a number")
        ag = fm.get("agents")
        if ag is not None:
            for a in parse_list(ag):
                check(a in agent_names, f"{label} → agent '{a}' exists",
                      f"{label} references agent '{a}' with no agents/{a}.md")

    # --- skills: every trigger skill has name + description + model/effort/agents profile ---
    print("== skills ==")
    skills_dir = ROOT / "skills"
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        base = skill_md.parent.name
        if base == "_shared":
            check(False, "", "skills/_shared must not contain SKILL.md (it would register as a skill)")
            continue
        fm = read_frontmatter(skill_md)
        check(fm.get("name") == base,
              f"skill '{base}' has matching name frontmatter",
              f"skill '{base}': frontmatter name is {fm.get('name')!r}, expected {base!r}")
        check(len(fm.get("description", "")) >= 30 or "description" in _block_keys(skill_md),
              f"skill '{base}' has a description",
              f"skill '{base}' has no/short description")
        check_profile(f"skill '{base}'", fm, require=True, require_agents=True)
        # Skill frontmatter executes BEFORE any settings are read — a skill that pins an
        # entitlement-gated tier hard-fails at skill start for every account without that tier
        # (proven by the 1140b0c-era hard-fail). Judgment tier lives on the AGENTS + judgment_model.
        check(fm.get("model") not in ("opus", "fable"),
              f"skill '{base}' does not pin an entitlement-gated model tier",
              f"skill '{base}' frontmatter pins model: {fm.get('model')} — skill frontmatter runs "
              f"before settings, so accounts without that tier hard-fail; use `model: inherit` "
              f"(judgment quality belongs to the agents / judgment_model)")
    check((skills_dir / "_shared").is_dir() and not (skills_dir / "_shared" / "SKILL.md").exists(),
          "_shared is reference-only (no SKILL.md)",
          "_shared is missing or contains a SKILL.md")

    # --- agents: name + description ---
    print("== agents ==")
    for agent_md in sorted((ROOT / "agents").glob("*.md")):
        fm = read_frontmatter(agent_md)
        check(bool(fm.get("name")), f"agent '{agent_md.stem}' has a name", f"agent '{agent_md.name}' has no name frontmatter")
        check("description" in _block_keys(agent_md), f"agent '{agent_md.stem}' has a description", f"agent '{agent_md.name}' has no description")
        check_profile(f"agent '{agent_md.stem}'", fm, require=True)

    # === semantic + consistency invariants (the checks a human ran by hand each change) ===
    # The groups above check structure (manifests agree, frontmatter valid). These check the
    # conventions the plugin actually relies on: doc links resolve, the invocation form is right,
    # every stage ends with its handoff block, the surface taxonomy is single-source, and no
    # _shared/ file lost all its referrers. Structure passing != the conventions holding.
    skill_glob = sorted((ROOT / "skills").rglob("*.md"))
    skill_specs = sorted((ROOT / "skills").glob("*/SKILL.md"))
    doc_pool = skill_glob + sorted((ROOT / "agents").glob("*.md"))

    # --- skill count in prose: README + the 4 manifests state the REAL skill count ---
    # The "N atomic" phrase is marketing prose that silently rots when a skill is added;
    # every file that carries it must agree with the actual number of skills/*/SKILL.md.
    print("== skill count in prose ==")
    n_skills = len(skill_specs)
    ATOMIC_RE = re.compile(r"\b(\d+) atomic")
    for rel in ("README.md", ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
                ".codex-plugin/plugin.json", ".cursor-plugin/plugin.json"):
        counts = ATOMIC_RE.findall((ROOT / rel).read_text())
        check(bool(counts) and all(int(c) == n_skills for c in counts),
              f"{rel} states the real skill count ({n_skills} atomic)",
              f"{rel} must say '{n_skills} atomic …' to match the {n_skills} skills/*/SKILL.md "
              f"(found: {counts if counts else 'no `N atomic` phrase'})")

    # --- markdown relative links resolve (replaces the per-change manual link sweep) ---
    # Only *.md / dir targets are resolved (the doc cross-references). Skipped: http(s), #anchors,
    # any <placeholder> target, and the template-runtime paths that resolve ONLY inside a generated
    # docs/features/<slug>/ folder (the skills/*/templates/ scaffolds link to those).
    print("== links ==")
    LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    LINK_ALLOW = {"./CONTEXT.md", "../spec.md", "../sad.md", "../data-model.md", "../tasks.json",
                  "../ux-flows.md", "../screens.md"}
    LINK_ALLOW_PREFIX = ("../contracts/", "../adr/", "./features/")
    link_files = sorted(set(skill_glob + sorted((ROOT / "agents").glob("*.md")) + [ROOT / "README.md"]))
    n_links = 0
    broken: list[str] = []
    for f in link_files:
        for m in LINK_RE.finditer(f.read_text()):
            target = m.group(1).strip()
            if target.startswith(("http://", "https://")) or target.startswith("#"):
                continue
            if "<" in target:                        # placeholder, e.g. docs/features/<slug>/…
                continue
            path_part = target.split("#", 1)[0]
            if not path_part or not (path_part.endswith(".md") or path_part.endswith("/")):
                continue                             # only doc (*.md) + dir links are resolvable here
            if path_part in LINK_ALLOW or path_part.startswith(LINK_ALLOW_PREFIX):
                continue                             # template-runtime: resolves only in a feature folder
            n_links += 1
            if not (f.parent / path_part).exists():
                broken.append(f"{f.relative_to(ROOT)} → {target}")
    check(not broken,
          f"all {n_links} relative doc links resolve (template-runtime paths allowlisted)",
          "broken relative links (real *.md/dir target missing, not template-runtime):\n        "
          + "\n        ".join(broken))

    # --- invocation form: the namespaced /sdd:<name>, never the hyphenated /sdd-<name> ---
    # The plugin ships skills (no commands/ dir), so Claude Code invokes them /sdd:<name>. The only
    # legit /sdd- in the tree is the proof-run branch ref proof/sdd-notification-preferences.
    # We scan docs + the manifests (the v1.8.4 sweep missed plugin.json's description —
    # that gap stays closed).
    print("== invocation form ==")
    SDD_HYPHEN = re.compile(r"(?<!proof)/sdd-")
    form_files = link_files + [ROOT / ".claude-plugin" / "plugin.json", ROOT / ".claude-plugin" / "marketplace.json"]
    offenders: list[str] = []
    for f in sorted(set(form_files)):
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if SDD_HYPHEN.search(line):
                offenders.append(f"{f.relative_to(ROOT)}:{i}")
    check(not offenders,
          "invocation form is namespaced /sdd:<name> everywhere (no hyphenated /sdd-)",
          "found the stale hyphenated /sdd- form (use /sdd:<name>) at: " + ", ".join(offenders))

    # --- every stage ends with the handoff block (the v1.8.1 output contract) ---
    # The phrase «stage-handoff block» is the contract wording every spine's final step uses;
    # a bare `handoff.md` substring (e.g. in a passing mention) is not enough to prove the
    # skill actually ends with the block.
    print("== handoff block ==")
    for skill_md in skill_specs:
        base = skill_md.parent.name
        check("stage-handoff block" in flat(skill_md),
              f"skill '{base}' emits the stage-handoff block (the literal phrase is present)",
              f"skill '{base}' SKILL.md never says 'stage-handoff block' — every stage must end with «emit the stage-handoff block per _shared/handoff.md»")

    # --- every skill verifies its own output (the structural self-check contract) ---
    # _shared/self-check.md defines the contract; every SKILL.md either runs a named checklist
    # or maps its heavy verifier (critic/reviewer/drift/mermaid/GATE) onto it — the literal
    # phrase «structural self-check» is the greppable evidence, same mechanism as the
    # stage-handoff check above.
    print("== structural self-check ==")
    for skill_md in skill_specs:
        base = skill_md.parent.name
        check("structural self-check" in flat(skill_md),
              f"skill '{base}' names its structural self-check",
              f"skill '{base}' SKILL.md never says 'structural self-check' — every skill must run "
              f"the checklist (or map its heavy verifier) per _shared/self-check.md")

    # --- skill dir names are BRE-safe (install.sh interpolates them into a sed pattern) ---
    print("== skill dir names ==")
    DIRNAME_RE = re.compile(r"^[a-z0-9-]+$")
    for skill_md in skill_specs:
        base = skill_md.parent.name
        check(bool(DIRNAME_RE.match(base)),
              f"skill dir '{base}' matches ^[a-z0-9-]+$",
              f"skill dir '{base}' must match ^[a-z0-9-]+$ — install.sh interpolates the dir name into a sed (BRE) pattern, so a dot/underscore/+ would break the rename pass")

    # --- cross-tool mechanism coverage: every Claude mechanism a spine uses is mapped ---
    # tool-adapters.md is the single Codex/Cursor mapping table; a spine that starts using a
    # new Claude-specific mechanism without a row there strands non-Claude users.
    print("== cross-tool mechanism coverage ==")
    adapters_text = (ROOT / "skills" / "_shared" / "tool-adapters.md").read_text()
    MECHANISMS = ["AskUserQuestion", "TeamCreate", "Workflow", "subagent_type", "/clear"]
    for mech in MECHANISMS:
        used_in = [s.parent.name for s in skill_specs if mech in s.read_text()]
        if not used_in:
            continue  # no spine uses it — nothing to map
        check(mech in adapters_text,
              f"mechanism '{mech}' (used by {len(used_in)} skill(s)) is mapped in tool-adapters.md",
              f"mechanism '{mech}' is used by {', '.join(sorted(used_in))} but has no row in _shared/tool-adapters.md — Codex/Cursor users get no mapping for it")

    # --- the surface taxonomy is single-source in _shared/surfaces.md (DRY) ---
    # The two canonical tables (the taxonomy + the per-skill gating table) live ONLY here; a SKILL.md
    # that copies a header row has duplicated the source of truth (surfaces.md's own discipline rule).
    print("== taxonomy single-source ==")
    surfaces_text = (ROOT / "skills" / "_shared" / "surfaces.md").read_text()
    TAXONOMY_ROWS = [
        "| Surface | `api` contract form |",             # the per-skill gating table
        "| Surface | What it is (the C4 container) |",    # the surface taxonomy table
    ]
    for row in TAXONOMY_ROWS:
        dups = [str(s.relative_to(ROOT)) for s in skill_specs if row in s.read_text()]
        check(row in surfaces_text and not dups,
              f"taxonomy row `{row} …` is single-source in _shared/surfaces.md",
              (f"taxonomy row `{row} …` is duplicated in a SKILL.md (must live only in _shared/surfaces.md): "
               + ", ".join(dups)) if dups
              else f"taxonomy row `{row} …` is missing from _shared/surfaces.md (did it move/rename?)")

    # --- the design-pipeline boundary stays declared in surfaces.md ---
    # v2.0.0 moved screen-level design into the design skills (ux-flows.md / screens.md);
    # surfaces.md carries the architecture ↔ design boundary (SAD keeps the UI-architecture
    # decision, the design skills keep the screens). If either mention drops, the boundary was
    # silently reverted to the pre-2.0 "no screen artifact" scope.
    print("== design-pipeline boundary ==")
    for token in ("screens.md", "ux-flows.md"):
        check(token in surfaces_text,
              f"_shared/surfaces.md names {token} (the design-pipeline boundary)",
              f"_shared/surfaces.md never mentions '{token}' — the architecture ↔ design boundary "
              f"(SAD keeps UI-architecture; screen-level design lives in the design skills' "
              f"artifacts) must stay declared there")

    # --- architecture-map template shape: the machine-readable keys survey fills ---
    # implement's command-detection cascade reads test_cmd/lint_cmd from the map frontmatter and
    # design/others key freshness off reflects_commit — the template must keep declaring them.
    print("== architecture-map template ==")
    amap = ROOT / "skills" / "survey" / "templates" / "architecture-map.md"
    amap_fm = _block_keys(amap)
    for key in ("test_cmd", "reflects_commit"):
        check(key in amap_fm,
              f"architecture-map template frontmatter declares `{key}`",
              f"skills/survey/templates/architecture-map.md frontmatter lost the `{key}` key — "
              f"command-detection / staleness checks read it")

    # --- survey document authority: historical material cannot become the active plan ---
    # Survey is the architecture anchor, so its input classification must fail closed when a
    # docs-only/greenfield repo explicitly says the active architecture plan is missing.
    print("== survey document authority ==")
    survey_text = flat(ROOT / "skills" / "survey" / "SKILL.md")
    authority_classes = ("active/current authoritative plans", "accepted adrs/current architecture",
                         "historical documents", "research/spikes",
                         "abandoned or superseded plans")
    check(all(authority_class in survey_text for authority_class in authority_classes),
          "survey classifies architecture/product documents by authority",
          "skills/survey/SKILL.md must distinguish active plans, accepted/current architecture, "
          "historical documents, research/spikes, and abandoned/superseded plans")
    check("must not authorize target architecture" in survey_text
          and "active architecture plan is missing" in survey_text
          and "write no foundation artifacts" in survey_text,
          "survey refuses to promote historical material when an active plan is explicitly missing",
          "skills/survey/SKILL.md must keep the greenfield authority gate: historical evidence "
          "cannot authorize targets, and an explicitly missing active plan stops foundation writes")

    survey_evals = (
        "survey-authority-conflict",
        "survey-missing-active-plan",
        "survey-empty-cli-scaffold",
    )
    missing_survey_eval_parts = [
        f"{name}/{part}"
        for name in survey_evals
        for part in ("prompt.txt", "rubric.md")
        if not (ROOT / "evals" / "scenarios" / name / part).exists()
    ]
    check(not missing_survey_eval_parts,
          "focused survey authority/scaffold evals exist",
          "survey authority regression scenarios are incomplete: "
          + ", ".join(missing_survey_eval_parts))

    # --- model policy consistency: judgment_model is documented everywhere it matters ---
    # The judgment_model settings key (open value-set switch for the judgment agents) is defined in
    # the settings doc, consumed per agent-roster's precedence, and surfaced to users in the README —
    # if any file drops the mention, the policy silently forks. Both policy files must also carry
    # the "floor" rule (default-is-a-floor: never silently downgrade judgment below the session),
    # so the rule can't vanish from one of them.
    print("== model policy ==")
    for rel in ("skills/implement/references/settings.md", "skills/_shared/agent-roster.md",
                "README.md"):
        check("judgment_model" in (ROOT / rel).read_text(),
              f"{rel} documents judgment_model",
              f"{rel} never mentions 'judgment_model' — the settings doc, the roster policy and the README must all carry it")
    for rel in ("skills/implement/references/settings.md", "skills/_shared/agent-roster.md"):
        check("floor" in (ROOT / rel).read_text().lower(),
              f"{rel} carries the judgment_model floor rule",
              f"{rel} never says 'floor' — the default-is-a-floor rule (no silent judgment downgrade below the session) must stay in both policy files")

    # --- artifact language: the key is defined + the rule is threaded through every writer ---
    # The artifact_language settings key (en|uk prose switch for pipeline documents) is defined in
    # the settings doc and its rule lives in _shared/artifact-language.md — if either drops the
    # mention, the policy silently forks. And every artifact-writing skill must point at the shared
    # rule; a dropped pointer means that skill's documents silently revert to always-English.
    print("== artifact language ==")
    for rel in ("skills/implement/references/settings.md", "skills/_shared/artifact-language.md"):
        check("artifact_language" in (ROOT / rel).read_text(),
              f"{rel} documents artifact_language",
              f"{rel} never mentions 'artifact_language' — the settings doc and the shared rule must both carry it")
    ARTIFACT_WRITERS = ("interview", "specify", "clarify", "glossary", "design", "decide-adr", "sequences",
                        "data-model", "api", "tasks", "plan-tests", "review", "ship", "fix",
                        "roadmap", "survey", "design-system", "ux-flows", "screens")
    for name in ARTIFACT_WRITERS:
        check("artifact-language.md" in (ROOT / "skills" / name / "SKILL.md").read_text(),
              f"skills/{name}/SKILL.md points at _shared/artifact-language.md",
              f"skills/{name}/SKILL.md never mentions 'artifact-language.md' — every artifact-writing "
              f"skill must carry the language pointer")

    # --- the route table is single-source in _shared/size-matrix.md + `.route` is threaded ---
    # The Routes table (quick/standard/full handoff behaviour) lives ONLY in size-matrix.md;
    # and the `.route` artifact must be named by the files that write/consume it — a rename or
    # a dropped mention silently reverts the pipeline to always-standard.
    print("== routes ==")
    size_matrix_text = (ROOT / "skills" / "_shared" / "size-matrix.md").read_text()
    ROUTE_HEADER = "| Route | Handoff behaviour at an optional stage |"
    route_dups = [str(s.relative_to(ROOT)) for s in skill_specs if ROUTE_HEADER in s.read_text()]
    check(ROUTE_HEADER in size_matrix_text and not route_dups,
          "route table is single-source in _shared/size-matrix.md",
          (f"route table header is duplicated in a SKILL.md (must live only in _shared/size-matrix.md): "
           + ", ".join(route_dups)) if route_dups
          else "route table header is missing from _shared/size-matrix.md (did it move/rename?)")
    for rel in ("skills/_shared/size-matrix.md", "skills/_shared/handoff.md",
                "skills/classify-size/SKILL.md", "skills/specify/SKILL.md"):
        check('.route' in (ROOT / rel).read_text(),
              f"{rel} mentions the .route artifact",
              f"{rel} never mentions '.route' — it writes or resolves the route and must name the artifact")

    # --- specify domain discovery: risk-gated evidence remains separate from ideation ---
    # This workflow spans an agent, a conditional template, the specify spine, and its drafting
    # reference. A missing link can leave discovery silently skipped or written but never consumed.
    print("== specify domain discovery ==")
    specify_path = ROOT / "skills" / "specify" / "SKILL.md"
    specify_text = flat(specify_path)
    investigator = ROOT / "agents" / "domain-investigator.md"
    discovery_template = ROOT / "skills" / "specify" / "templates" / "discovery.md"
    draft_generation = ROOT / "skills" / "specify" / "references" / "draft-generation.md"
    roster = ROOT / "skills" / "_shared" / "agent-roster.md"
    discovery_eval = ROOT / "evals" / "scenarios" / "specify-unfamiliar-domain-discovery"

    check(investigator.exists() and discovery_template.exists(),
          "domain-investigator and discovery.md template exist",
          "specify domain discovery requires agents/domain-investigator.md and "
          "skills/specify/templates/discovery.md")
    specify_agents = parse_list(read_frontmatter(specify_path).get("agents", ""))
    check("domain-investigator" in specify_agents
          and bool(table_row(roster, "domain-investigator"))
          and "sdd:domain-investigator" in specify_text
          and "discovery.md" in specify_text,
          "domain-investigator is registered and specify names its discovery artifact",
          "domain-investigator must remain in the roster and specify agent/artifact contract")

    template_text = discovery_template.read_text().lower() if discovery_template.exists() else ""
    discovery_sections = {"why discovery was needed", "verified domain facts",
                          "terminology and workflow norms", "assumptions",
                          "unknowns and source gaps", "authoritative sources", "edge cases",
                          "failure modes", "risk register", "measurement / kpi seeds"}
    actual_discovery_sections = markdown_headings(discovery_template) if discovery_template.exists() else set()
    check(discovery_sections <= actual_discovery_sections
          and "research_limited" in template_text,
          "discovery template preserves facts, uncertainty, risks, and measurements",
          "discovery.md template lost required content: "
          + ", ".join(sorted(discovery_sections - actual_discovery_sections)))

    drafting_text = flat(draft_generation) if draft_generation.exists() else ""
    check("discovery.md" in drafting_text
          and all(section in drafting_text for section in ("§1", "§3", "§5", "§6", "§7", "§8")),
          "discovery findings feed the current spec schema",
          "draft-generation.md must map discovery findings into the current spec instead of leaving dead documentation")
    check((discovery_eval / "prompt.txt").exists()
          and (discovery_eval / "rubric.md").exists()
          and (discovery_eval / "fixture" / "docs" / ".gitkeep").exists(),
          "focused unfamiliar-domain discovery eval exists",
          "evals/scenarios/specify-unfamiliar-domain-discovery must include prompt, rubric, and fixture")

    # --- specify KPI contract: decisions remain measurable without an unexplained TBD ---
    # The contract spans the template, drafting/Socratic guidance, critic, and a behaviour eval.
    # Guard the load-bearing fields so a future simplification cannot silently regress to a
    # baseline/target bullet list that lacks ownership or an actionable post-timebox decision.
    print("== specify KPI contract ==")
    spec_template_path = ROOT / "skills" / "specify" / "templates" / "spec.md"
    measurement_eval = ROOT / "evals" / "scenarios" / "specify-product-measurement-plan"
    kpi_fields = {"metric", "why it matters", "source/event", "baseline", "target/timebox",
                  "decision threshold", "owner", "when reviewed"}
    spec_tables = markdown_tables(spec_template_path)
    kpi_headers = next((set(header) for heading, header, _rows in spec_tables
                        if heading == "metrics / kpis"), set())

    check(kpi_fields <= kpi_headers,
          "spec template carries the complete KPI decision contract",
          "skills/specify/templates/spec.md lost KPI fields: "
          + ", ".join(sorted(kpi_fields - kpi_headers)))
    # Actionable thresholds and honest unknown baselines are semantic behavior owned by this eval.
    check((measurement_eval / "prompt.txt").exists()
          and (measurement_eval / "rubric.md").exists()
          and (measurement_eval / "fixture" / "docs" / ".gitkeep").exists(),
          "focused product-measurement eval exists",
          "evals/scenarios/specify-product-measurement-plan must include prompt, rubric, and fixture")

    # --- specify authorization coverage: the N/A waiver stays explicit and sourced ---
    # The authorization AC floor spans the template, drafting guidance, the Socratic gate, the
    # critic floor, and clarify's second catch. The waiver is legal ONLY as an explicit,
    # source-cited N/A — a future simplification must not turn it into a silent skip or a
    # self-declared (unsourced) excuse. Guard every link of the contract.
    print("== specify authorization coverage ==")
    draft_gen_path = ROOT / "skills" / "specify" / "references" / "draft-generation.md"
    socratic_path = ROOT / "skills" / "specify" / "references" / "socratic.md"
    specify_critic_path = ROOT / "skills" / "specify" / "references" / "critic.md"
    depth_path = ROOT / "skills" / "_shared" / "interview-depth.md"
    ambiguity_path = ROOT / "skills" / "clarify" / "references" / "ambiguity-checks.md"
    spec_template_text = flat(spec_template_path) if spec_template_path.exists() else ""
    authz_waiver_files = {
        "draft-generation.md": flat(draft_gen_path) if draft_gen_path.exists() else "",
        "socratic.md": flat(socratic_path) if socratic_path.exists() else "",
        "critic.md": flat(specify_critic_path) if specify_critic_path.exists() else "",
        "interview-depth.md": flat(depth_path) if depth_path.exists() else "",
        "ambiguity-checks.md": flat(ambiguity_path) if ambiguity_path.exists() else "",
    }

    for waiver_file, waiver_text in authz_waiver_files.items():
        check("authorization: n/a" in waiver_text and "source" in waiver_text,
              f"authorization N/A waiver stays explicit + sourced in {waiver_file}",
              f"the authorization coverage waiver must remain an explicit, source-cited N/A in "
              f"{waiver_file} — a silent skip or an unsourced excuse is a floor violation")
    check("authoritative upstream artifact" in authz_waiver_files["draft-generation.md"],
          "draft-generation.md names the waiver's authority condition",
          "skills/specify/references/draft-generation.md must tie the authorization N/A to an "
          "authoritative upstream artifact (committed approach / non-goal / discovery / product doc)")
    check("authorization: n/a" in spec_template_text,
          "spec template documents the authorization N/A form",
          "skills/specify/templates/spec.md must show the sourced `Authorization: N/A` waiver "
          "line next to the coverage-type list")

    # --- specify measurement waiver: §6/§7 targets may be declined only sourced + revisitable ---
    # The authorization-N/A genre applied to numbers: a walking skeleton / spike / throwaway tool
    # may waive numeric §6 aspects and the §7 KPI table — but only as an explicit, sourced
    # `Measurement: N/A` line with a §8 revisit OQ. A future simplification must not turn it
    # into a silent empty table (numbers vanish) nor close the door again (vanity rows return).
    # Guard every link: the canon definition, the template forms, the Socratic + critic gates,
    # and the downstream consumers (clarify's unmeasured-NFR class, design's §10, plan-tests'
    # measurement readiness).
    print("== specify measurement waiver ==")
    waiver_files = {
        "draft-generation.md": flat(draft_gen_path) if draft_gen_path.exists() else "",
        "socratic.md": flat(socratic_path) if socratic_path.exists() else "",
        "critic.md": flat(specify_critic_path) if specify_critic_path.exists() else "",
        "spec-template": flat(spec_template_path) if spec_template_path.exists() else "",
    }
    for waiver_file, waiver_text in waiver_files.items():
        check("measurement: n/a" in waiver_text and "source" in waiver_text,
              f"measurement N/A waiver stays explicit + sourced in {waiver_file}",
              f"the measurement waiver must remain an explicit, source-cited `Measurement: N/A` "
              f"in {waiver_file} — a silent empty §6/§7 or an unsourced excuse is a floor violation")
    for waiver_file, waiver_text in waiver_files.items():
        check("revisit" in waiver_text,
              f"measurement N/A waiver stays revisitable in {waiver_file}",
              f"{waiver_file} must tie the `Measurement: N/A` waiver to a §8 revisit OQ with "
              f"owner + due — an unrevisitable waiver silently becomes permanent")
    check("scenario type" in waiver_files["draft-generation.md"],
          "draft-generation.md names the waiver's applicability condition",
          "skills/specify/references/draft-generation.md must tie the measurement N/A to a "
          "scenario type an upstream source establishes (walking skeleton / spike / throwaway)")
    check("measurement: n/a" in flat(ambiguity_path) if ambiguity_path.exists() else True,
          "clarify's unmeasured-NFR class recognizes the sourced waiver",
          "skills/clarify/references/ambiguity-checks.md must treat the sourced measurement "
          "N/A as a legal decline (verify its §8 revisit), not re-flag it as unmeasured")
    design_draft_text = flat(ROOT / "skills" / "design" / "references" / "draft-generation.md")
    check("measurement n/a" in design_draft_text,
          "design's quality goals derive without minting numbers for waived aspects",
          "skills/design/references/draft-generation.md must handle the sourced §6 measurement "
          "N/A — qualitative §10 scenario or dropped goal, never an invented target")
    check("fewer than 3" in design_draft_text,
          "design's ≥3 quality-goal floor degrades when the spec keeps fewer aspects",
          "skills/design/references/draft-generation.md must relax the ≥3 quality-goal / §10 "
          "scenario floors to one-per-kept-aspect when the spec's §6 waivers leave fewer than "
          "3 aspects — else the waiver forces padding with invented qualities")
    design_sad_text = flat(ROOT / "skills" / "design" / "templates" / "sad.md")
    check("no padding" in design_sad_text,
          "sad.md template allows fewer than 3 QG blocks when §6 keeps fewer aspects",
          "skills/design/templates/sad.md must not hard-code 3 quality-goal / QG blocks — a "
          "waived spec yields fewer, and padding is a floor violation")
    plan_tests_text_2 = flat(ROOT / "skills" / "plan-tests" / "SKILL.md")
    check("measurement: n/a" in plan_tests_text_2 and "revisit" in plan_tests_text_2,
          "plan-tests mirrors a waived §7 instead of fabricating MEAS rows",
          "skills/plan-tests/SKILL.md must mirror the sourced measurement N/A (revisit "
          "accounted for) rather than inventing measurement-readiness rows")

    # --- plan-tests risk + measurement continuity: promises reach executable/release evidence ---
    # Risk/KPI rows are useful only if plan-tests distinguishes pre-release readiness from future
    # outcomes and implement refuses to silently drop executable rows that have no task owner.
    print("== plan-tests risk and measurement continuity ==")
    plan_tests_text = flat(ROOT / "skills" / "plan-tests" / "SKILL.md")
    test_plan_template = flat(ROOT / "skills" / "plan-tests" / "templates" / "test-plan.md")
    implement_text = flat(ROOT / "skills" / "implement" / "SKILL.md")
    implement_inputs = flat(ROOT / "skills" / "implement" / "references" / "inputs.md")
    test_author_text = flat(ROOT / "agents" / "test-author.md")
    implementer_text = flat(ROOT / "agents" / "implementer.md")
    risk_measurement_eval = ROOT / "evals" / "scenarios" / "plan-tests-risk-measurement-coverage"

    risk_sources = ("discovery.md §9", "sad.md §11", "spec.md §6.1")
    check(all(source in plan_tests_text for source in risk_sources)
          and "risk-nn" in plan_tests_text and "meas-nn" in plan_tests_text,
          "plan-tests names its risk, KPI, and identifier sources",
          "skills/plan-tests/SKILL.md must name discovery/SAD/security sources and RISK-NN/MEAS-NN")

    plan_tables = {heading: set(header)
                   for heading, header, _rows in markdown_tables(
                       ROOT / "skills" / "plan-tests" / "templates" / "test-plan.md")}
    required_plan_tables = {
        "risk coverage": {"check id", "source", "risk / failure mode", "severity",
                          "verification / monitoring activity", "pass or decision condition",
                          "owner / timing"},
        "measurement readiness": {"check id", "metric", "source/event", "baseline plan",
                                  "target/timebox", "decision threshold",
                                  "pre-release readiness check", "post-release outcome review",
                                  "owner / review timing"},
        "implementation linkage": {"check id", "source row", "task link", "closure activity",
                                   "evidence required", "owner / timing", "status"},
    }
    missing_plan_structure = {
        heading: sorted(columns - plan_tables.get(heading, set()))
        for heading, columns in required_plan_tables.items()
        if columns - plan_tables.get(heading, set())
    }
    check(not missing_plan_structure
          and "risk-nn" in test_plan_template and "meas-nn" in test_plan_template,
          "test-plan template carries risk, measurement, and linkage tables",
          "skills/plan-tests/templates/test-plan.md lost structure: "
          + repr(missing_plan_structure))
    check("test-plan.md" in implement_text and "sdd-check" in implement_text
          and "risk-nn" in implement_text and "meas-nn" in implement_text
          and "test-plan.md" in implement_inputs
          and "risk-nn" in implement_inputs and "meas-nn" in implement_inputs
          and "risk-nn" in test_author_text and "meas-nn" in test_author_text
          and "risk-nn" in implementer_text and "meas-nn" in implementer_text,
          "implementation contracts consume linked risk and measurement IDs",
          "implement and its RED/GREEN agents must name test-plan.md and RISK-NN/MEAS-NN linkage")
    # Honest residual handling, readiness-vs-outcome behavior, and task linkage are owned by the
    # focused plan-tests eval below; the validator protects only their artifact structure.
    check((risk_measurement_eval / "prompt.txt").exists()
          and (risk_measurement_eval / "rubric.md").exists()
          and (risk_measurement_eval / "fixture" / "docs" / "features"
               / "invoice-approval-guardrails" / "spec.md").exists(),
          "focused plan-tests risk/measurement eval exists",
          "evals/scenarios/plan-tests-risk-measurement-coverage must include prompt, rubric, "
          "and a feature fixture")

    # --- plan-tests routing: task-level tests never replace the planning stage ---
    print("== plan-tests routing ==")
    tasks_path = ROOT / "skills" / "tasks" / "SKILL.md"
    tasks_text = flat(tasks_path)
    size_matrix_path = ROOT / "skills" / "_shared" / "size-matrix.md"
    handoff_path = ROOT / "skills" / "_shared" / "handoff.md"
    routing_eval = ROOT / "evals" / "scenarios" / "tasks-plan-tests-routing"
    plan_tests_row = table_row(size_matrix_path, "plan-tests")
    tasks_row = table_row(handoff_path, "tasks")

    check(bool(plan_tests_row) and "## test plan" in " | ".join(plan_tests_row)
          and bool(tasks_row) and "/sdd:plan-tests <slug>" in " | ".join(tasks_row)
          and "../_shared/handoff.md" in tasks_text,
          "route and handoff tables preserve the plan-tests stage and inline artifact",
          "size-matrix/handoff/tasks contracts must structurally route tasks through plan-tests")
    # Whether task-level test names incorrectly bypass this stage is owned by the routing eval.
    check((routing_eval / "prompt.txt").exists()
          and (routing_eval / "rubric.md").exists()
          and (routing_eval / "fixture" / "docs" / "features"
               / "release-health" / "spec.md").exists(),
          "focused tasks-to-plan-tests routing eval exists",
          "evals/scenarios/tasks-plan-tests-routing must include prompt, rubric, and a feature fixture")

    # --- ux-flows interaction decisions: downstream consumes the UXD ledger, never edits it ---
    # UXD-NN rows are resolved user-experience evidence, not architecture decisions; spec.md stays
    # the authority on conflict; and sequences/screens/plan-tests preserve resolved interaction
    # behavior instead of re-inventing transitions. Guard the four spines' contract phrases so a
    # future edit can't silently drop the authority boundary or the no-reinvention rule.
    print("== ux-flows interaction decisions ==")
    design_text_uxd = flat(ROOT / "skills" / "design" / "SKILL.md")
    sequences_text_uxd = flat(ROOT / "skills" / "sequences" / "SKILL.md")
    screens_text_uxd = flat(ROOT / "skills" / "screens" / "SKILL.md")
    plan_tests_text_uxd = flat(ROOT / "skills" / "plan-tests" / "SKILL.md")

    check("interaction decisions" in design_text_uxd
          and "resolved user-experience evidence" in design_text_uxd
          and "spec.md" in design_text_uxd and "higher authority" in design_text_uxd
          and "surface" in design_text_uxd and "never" in design_text_uxd,
          "design consumes UXD rows as resolved UX evidence with spec as higher authority, "
          "surfacing conflicts",
          "skills/design/SKILL.md must read the UXD ledger as resolved user-experience evidence, "
          "keep spec.md the higher authority, and surface conflicts — never silently override")
    check("uxd-nn" in sequences_text_uxd and "automatic progression" in sequences_text_uxd
          and "do not re-introduce a transition" in sequences_text_uxd,
          "sequences preserves UXD navigation/continuation pins and never re-introduces "
          "excluded transitions",
          "skills/sequences/SKILL.md must preserve UXD-NN navigation/continuation pins and forbid "
          "re-introducing a transition ux-flows explicitly excluded")
    check("must not invent new automatic navigation" in screens_text_uxd,
          "screens never invents automatic navigation or automatic next-step screens",
          "skills/screens/SKILL.md must keep the rule that screens details the resolved UX-flow "
          "inventory and must not invent automatic navigation / automatic next-step screens")
    check("preserve resolved interaction behavior" in plan_tests_text_uxd
          and "logical next steps" in plan_tests_text_uxd,
          "plan-tests preserves resolved interaction behavior when deriving e2e-through-UI paths",
          "skills/plan-tests/SKILL.md must preserve resolved interaction behavior and forbid "
          "extending the UX flow with logical next steps")

    ux_flows_eval = ROOT / "evals" / "scenarios" / "ux-flows-interaction-decision"
    ux_flows_conflict_eval = ROOT / "evals" / "scenarios" / "ux-flows-spec-conflict"
    check((ux_flows_eval / "prompt.txt").exists()
          and (ux_flows_eval / "rubric.md").exists()
          and (ux_flows_eval / "fixture" / "docs" / "features"
               / "project-workspace" / "spec.md").exists(),
          "focused ux-flows interaction-decision eval exists",
          "evals/scenarios/ux-flows-interaction-decision must include prompt, rubric, and a "
          "feature fixture")
    check((ux_flows_conflict_eval / "prompt.txt").exists()
          and (ux_flows_conflict_eval / "rubric.md").exists()
          and (ux_flows_conflict_eval / "fixture" / "docs" / "features"
               / "project-workspace" / "spec.md").exists(),
          "focused ux-flows spec-conflict eval exists",
          "evals/scenarios/ux-flows-spec-conflict must include prompt, rubric, and a feature fixture")

    # --- the settings file: one canon, one create-anchor, one editor ---
    # Three invariants that only prose holds up, so the validator holds them mechanically:
    # (1) the README's copy of the template agrees with the canon key-for-key — README trims the
    #     inline comments for width, so only key+value are compared, but a drifted DEFAULT there
    #     is a lie in the most-read file; (2) exactly the six pipeline skills + config carry the
    #     create step, identified by its bold anchor + a link to the canon — a seventh skill
    #     growing its own create step, or one of the six losing it, is the regression that made
    #     the file non-deterministic in the first place; (3) no file outside config/ offers to
    #     SAVE a value into the settings file — creating is many skills' job, changing values is
    #     config's alone, and that rule previously leaked (command-detection.md offered to save
    #     the cmd_* keys).
    print("== settings file invariants ==")
    canon_text = (ROOT / "skills" / "_shared" / "settings-file.md").read_text()

    def yaml_pairs(text: str) -> dict[str, str]:
        block = re.search(r"```yaml\n(.*?)```", text, re.S)
        if not block:
            return {}
        out = {}
        for line in block.group(1).splitlines():
            m = re.match(r"^([a-z_]+):\s*(.*?)\s*(?:#.*)?$", line)
            if m:
                out[m.group(1)] = m.group(2)
        return out

    canon_keys = yaml_pairs(canon_text[canon_text.index("## The documented frontmatter"):])
    readme_text = (ROOT / "README.md").read_text()
    readme_keys = yaml_pairs(readme_text[readme_text.index("### The settings file"):])
    drift = sorted(k for k in set(canon_keys) | set(readme_keys)
                   if canon_keys.get(k) != readme_keys.get(k))
    check(bool(canon_keys) and not drift,
          f"README's settings block matches the canon ({len(canon_keys)} keys, same defaults)",
          f"README.md's settings YAML has drifted from skills/_shared/settings-file.md on: "
          f"{', '.join(drift) if drift else '(no canon block found)'} — the README block must "
          f"carry the same keys and the same default values (comments may be trimmed for width)")

    CREATORS = ("interview", "survey", "roadmap", "scaffold", "specify", "implement", "config")
    CREATE_ANCHOR = "**ensure the settings file"
    for base in CREATORS:
        body = flat(ROOT / "skills" / base / "SKILL.md")
        check(CREATE_ANCHOR in body and "settings-file.md" in body,
              f"skill '{base}' carries the settings create step (anchor + canon link)",
              f"skill '{base}' lost the «**Ensure the settings file …**» step or its link to "
              f"_shared/settings-file.md — the file must be created deterministically by all "
              f"{len(CREATORS)} of {', '.join(CREATORS)}")
    strays = [s.parent.name for s in skill_specs
              if s.parent.name not in CREATORS and CREATE_ANCHOR in flat(s)]
    check(not strays,
          f"no skill outside the {len(CREATORS)} creators carries the create step",
          f"skill(s) {', '.join(strays)} grew their own settings create step — the step belongs to "
          f"{', '.join(CREATORS)} only; every other skill reads the file")

    SAVE_OFFER = re.compile(
        r"(offer to (save|write|persist|set)|save (them|it|these|the commands) to)[^\n]{0,60}sdd\.local\.md",
        re.I)
    editors = {ROOT / "skills" / "_shared" / "settings-file.md"}
    leaks = [str(f.relative_to(ROOT)) for f in doc_pool
             if f not in editors and "skills/config/" not in str(f) and SAVE_OFFER.search(f.read_text())]
    check(not leaks,
          "only config/ offers to save a value into .claude/sdd.local.md",
          f"{', '.join(leaks)} offers to save a value into .claude/sdd.local.md — changing values "
          f"belongs to the `config` skill alone; point the user at /sdd:config instead")

    # --- install.sh can still extract the settings template from the canon ---
    # install.sh writes .claude/sdd.local.md at install time (Codex/Cursor) by awk-extracting the
    # yaml block + the «What each key does» section OUT of _shared/settings-file.md, deliberately
    # keeping one copy of the template. That coupling is invisible: renaming a heading or adding a
    # second ```yaml block there would silently produce an empty/wrong settings file. So run the
    # installer's OWN awk programs here and assert they still yield both pieces.
    print("== install.sh settings extraction ==")
    import subprocess
    canon = ROOT / "skills" / "_shared" / "settings-file.md"
    installer_text = (ROOT / "install.sh").read_text()
    progs = re.findall(r"\$\(awk '([^']+)' \"\$canon\"\)", installer_text)
    if check(len(progs) == 2,
             "install.sh carries the two awk extraction programs",
             f"install.sh must extract the settings template from _shared/settings-file.md with two "
             f"awk programs (found {len(progs)}) — did the extraction change shape?"):
        try:
            fm = subprocess.run(["awk", progs[0], str(canon)], capture_output=True, text=True, check=True).stdout
            body = subprocess.run(["awk", progs[1], str(canon)], capture_output=True, text=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError) as exc:
            fm = body = ""
            check(False, "", f"running install.sh's awk extraction failed: {exc}")
        check("interview_depth:" in fm and "judgment_model:" in fm and fm.count(":") >= 25,
              f"install.sh extracts the full settings frontmatter ({len(fm.splitlines())} lines)",
              "install.sh's awk no longer extracts the documented frontmatter from "
              "_shared/settings-file.md — check the `## The documented frontmatter` heading and "
              "that it is still followed by exactly one ```yaml block")
        check(body.startswith("## What each key does") and "**`interview_depth`**" in body,
              f"install.sh extracts the «What each key does» body ({len(body.splitlines())} lines)",
              "install.sh's awk no longer extracts the «What each key does» section from "
              "_shared/settings-file.md — was the heading renamed or moved?")

    # --- no orphan in _shared/: every shared reference is pointed to by >=1 file ---
    print("== _shared no-orphan ==")
    for sf in sorted((ROOT / "skills" / "_shared").glob("*.md")):
        referrers = [p for p in doc_pool if p != sf and sf.name in p.read_text()]
        check(bool(referrers),
              f"_shared/{sf.name} is referenced by {len(referrers)} file(s)",
              f"_shared/{sf.name} is an orphan — nothing under skills/ or agents/ points to it")

    print()
    if errors:
        print(f"FAILED: {len(errors)} error(s) out of {checks} checks")
        return 1
    print(f"PASSED: {checks} checks")
    return 0


def _block_keys(path: Path) -> set[str]:
    """Keys present in the frontmatter, including multi-line (folded) ones like `description: >`."""
    text = path.read_text()
    if not text.startswith("---"):
        return set()
    end = text.find("\n---", 3)
    block = text[3:end] if end != -1 else ""
    return {m.group(1) for m in re.finditer(r"^([A-Za-z_][\w-]*):", block, re.M)}


if __name__ == "__main__":
    sys.exit(main())
