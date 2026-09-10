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
