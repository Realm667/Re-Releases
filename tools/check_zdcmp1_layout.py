"""Check only ZDCMP1 sources and its own workspace; no other mod policy is read."""
import argparse
import json
import os
from pathlib import Path
import re

from zdcmp1_paths import ROOT, workspace as default_workspace

WORKSPACE_ENTRIES = {'.codex', '.git', 'AGENTS.md', 'README.md', 'develop.ps1', 'tool.ps1',
                     'assets', 'builds', 'dependencies', 'history', 'migration', 'mockups', 'work'}


def violations(root=ROOT, workspace=None, workspace_config=None):
    root = Path(root).resolve()
    local = Path(workspace).resolve() if workspace is not None else default_workspace()
    issues = []
    if not local.is_dir():
        return [f'ZDCMP1 workspace not found: {local}']
    allowed = WORKSPACE_ENTRIES
    if workspace_config:
        config = Path(workspace_config).resolve()
        if not config.is_relative_to(local):
            return ['ZDCMP1 workspace policy must be inside its own workspace']
        policy = json.loads(config.read_text(encoding='utf-8-sig'))
        if Path(policy['workspace']).resolve() != local:
            return ['ZDCMP1 workspace policy points to a different project']
        allowed = set(policy['existing_entries'])
    for entry in local.iterdir():
        if entry.name not in allowed:
            issues.append(f'{entry}: unexpected workspace-root entry; use {local / ".codex/work"}')
        if not entry.resolve().is_relative_to(local):
            issues.append(f'{entry}: workspace entry points outside the ZDCMP1 directory')
    source = root / 'zdcmp1'
    if not source.is_dir():
        return sorted(issues + [f'ZDCMP1 production sources not found: {source}'])
    for base, dirs, files in os.walk(source, followlinks=False):
        for name in list(dirs):
            path = Path(base) / name
            if name in ('.codex', '__pycache__') or not path.resolve().is_relative_to(source):
                issues.append(f'{path}: local work data or external directory in production sources')
                dirs.remove(name)
        for name in files:
            path = Path(base) / name
            if (name.lower().endswith(('.log', '.tmp', '.bak', '.dbs', '.pyc', '.pk3'))
                    or re.search(r'\.(?:backup|autosave)\d*$', name, re.I)):
                issues.append(f'{path}: temporary output belongs in {local / ".codex"}')
            if not path.resolve().is_relative_to(source):
                issues.append(f'{path}: production file points outside the source directory')
    return sorted(issues)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--workspace', type=Path)
    parser.add_argument('--workspace-config', type=Path)
    args = parser.parse_args()
    issues = violations(args.root, args.workspace, args.workspace_config)
    print(json.dumps({'ok': not issues, 'violations': issues}, indent=2))
    return int(bool(issues))


if __name__ == '__main__':
    raise SystemExit(main())
