# Local UTNT work

Temporary packages, references, editor backups and test evidence live under
`tutnt/.codex/`, which is excluded from Git and the UTNT build.
Read `tutnt/.codex/README.md` locally for the directory map and path resolver.

The local `logs`, `_references` and `tools/validation` directories are compatibility
junctions into that directory. They preserve existing local commands and links;
junctions and machine-specific paths are not committed. On a fresh checkout,
generate test evidence by running the tools, or choose output paths below
`tutnt/.codex`. Historical evidence remains available in Git history.

Build/test tools, test fixtures, artwork source material and project documentation
remain versioned. `tutnt.pk3` remains the shared integration package at repository root.

## Required workflow for project agents

New temporary scripts, mockups and task outputs must go in
`tutnt/.codex/work/<topic>/`; test packages in `.codex/builds/`, logs in
`.codex/logs/`, evidence in `.codex/validation/`, references in
`.codex/references/`, backups in `.codex/backups/`, and caches in `.codex/cache/`.
Apply this rule to resumed tasks and delegated agents. Review the output paths
of historical scripts before rerunning them. Do not create new temporary
directories in the shared chat workspace. Existing legacy work remains available.

Before committing or finishing a task, run `python -B tools/check_work_layout.py`.
It reports known temporary file types outside the central directory, incorrect
compatibility paths, and new top-level chat workspace entries when the local
`tutnt/.codex/policy/workspace-root.json` baseline is available. It does not mutate
files or detect every possible temporary filename. Check your task's other output
paths as well. Fix your own outputs; preserve unrelated work.

Official mod packages and their build locks may remain at repository root.
Durable source files, tools, fixtures and documentation remain versioned.
Legacy junctions must point into the central directory; do not replace them with
ordinary output directories. Local agent instructions remain excluded from Git.

## Documentation

Keep permanent documentation under `_docs/utnt/` and temporary notes, concepts and historical reports under `tutnt/.codex/notes/`. See [the documentation index](../_docs/utnt/README.md). Root-level `UTNT_*.md` and `TNT*_CONCEPT.md` are rejected by the layout check.

## Preserve the established layout

Every new or resumed task must keep documentation under `_docs/` and definition
modules in the directories listed in [_docs/utnt/DEFINITION_LAYOUT.md](../_docs/utnt/DEFINITION_LAYOUT.md).
Do not recreate `docs/`, old root fragments or new workspace output folders.
Generated root tables must be refreshed from their authoritative modules.

Before committing or finishing, run `python -B tools/check_work_layout.py`.
For definition changes, also run `python -B tools/build_definition_tables.py --check`.
The layout checker rejects the retired root docs directory and misplaced modules
for all nine definition formats, in addition to temporary files and broken
compatibility paths. Fix your own findings; preserve and identify foreign work.
Historical scripts must resolve old paths before they read or write current files.

GitHub Actions runs the layout and generated-table checks on every push and pull
request (`.github/workflows/work-layout.yml`), including changes made through
GitHub Desktop. A failed check reports the violation; it does not delete files.
