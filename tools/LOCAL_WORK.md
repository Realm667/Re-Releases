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
