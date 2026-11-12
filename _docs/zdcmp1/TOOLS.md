# ZDCMP1 tools and workspaces

Production sources and reusable tools stay in the repository. Local dependencies,
packages, temporary files, logs and saves belong to the separate ZDCMP1 workspace.
The configured Windows workspace is `D:/Codex/ReReleases/ZDCMP1`; the checkout is
`F:/DoomDev/Projects/realm667.git`. Other checkouts must set `ZDCMP1_WORKSPACE`.

From the local workspace, use:

```powershell
.\develop.ps1 -Action Build
.\develop.ps1 -Action Validate
.\develop.ps1 -Action Check
.\develop.ps1 -Action Test -Suite paths
.\develop.ps1 -Action Test -Suite sky_parallax
.\tool.ps1 test_zdcmp1_edges --renderer 1
```

`tool.ps1` runs repository tools with the private Python interpreter and restores
the caller's environment afterwards. The local Python console launchers also use
this private interpreter and private temporary/Pip-cache directories. Original
launcher binaries are kept in the workspace's backup directory.

The Python runners use `tools/zdcmp1_paths.py` to select tools and output paths:

- `dependencies/uzdoom/`, `dependencies/iwads/` and `dependencies/acc/` supply the
  local tools. `ZDCMP1_ENGINE`, `ZDCMP1_IWAD` and `ZDCMP1_ACC` are explicit overrides.
- Runtime output, test fixtures, saves and caches use the workspace's `.codex/`.
- The default release package uses `builds/zdcmp1.pk3` under the workspace.
- `--mod`, `--output` and explicit isolated runtime roots remain supported.

Importing the path module does not change another project's environment.
Shared `work_paths.codex_root()` and the default repository-wide layout check keep
their UTNT behavior. The shared engine runner selects ZDCMP1 output paths only
for ZDCMP1 mods; specialized tests use the ZDCMP1 runner even for differently named
comparison packages.

The scoped layout check reads no UTNT policy or chat baseline:

```powershell
python -B tools/check_work_layout.py --project zdcmp1 --workspace D:/Codex/ReReleases/ZDCMP1
```

It checks ZDCMP1 production files and the selected workspace. The default checker
still covers the full repository for other projects. Do not recreate the retired
repository `logs` or `tutnt/.codex` aliases to run ZDCMP1 tests.

The ZDCMP1 CI job sets an explicit workspace below the runner's temporary
directory. Downloaded dependencies, compiled test fixtures, packages and uploaded
runtime logs use that workspace; the tracked engine/game test fixtures stay in
`tools/zdcmp1-tests/`. Gameplay assertions and package contents are unchanged.
