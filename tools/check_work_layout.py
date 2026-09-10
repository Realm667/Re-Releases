"""Read-only check for misplaced UTNT work files and broken compatibility paths.

Run before finishing a task. No files are moved or deleted. Existing legacy chat
workspace entries are allowed by a local baseline; only new top-level entries
there are reported. Inside the repository, known temporary file types are checked.
"""
import argparse
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
ALIASES = {'logs': 'logs', '_references': 'references',
           'tools/validation': 'validation', 'tools/__pycache__': 'cache/python',
           'tools/ui-regression-tests/acs': 'cache/ui-regression-acs'}

def violations(root, workspace_config=None):
    root = Path(root).resolve()
    central = root/'tutnt/.codex'
    issues = []
    for old, new in ALIASES.items():
        path = root/old
        if path.exists() and path.resolve() != (central/new).resolve():
            issues.append(f'{old}: compatibility path must point to tutnt/.codex/{new}')
    for folder, dirs, files in os.walk(root, followlinks=False):
        kept = []
        for name in dirs:
            path = Path(folder)/name
            relative = path.relative_to(root).as_posix()
            if name == '.git' or path == central or relative in ALIASES:
                continue
            if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
                continue
            if name in ('.codex', '__pycache__'):
                issues.append(f'{relative}: use the central tutnt/.codex directory')
                continue
            kept.append(name)
        dirs[:] = kept
        for name in files:
            path = Path(folder)/name
            relative = path.relative_to(root).as_posix()
            lower = name.lower()
            temporary = (lower.endswith(('.log', '.tmp', '.bak', '.dbs'))
                         or re.search(r'\.(?:backup|autosave)\d*$', lower))
            if lower.endswith(('.pk3', '.pk3.build.lock')):
                package = name.removesuffix('.build.lock')
                canonical = path.parent == root and (root/(Path(package).stem+'_build.bat')).is_file()
                temporary = not canonical
            if path.parent == root and (re.match(r'(arena|map|profile|final)-.*\.png$', lower)
                                        or lower in ('save-load.png', 'options-menu.png', 'utnt-smoke.png')
                                        or re.match(r'log-utnt-.*\.txt$', lower)):
                temporary = True
            if path.parent == root and re.match(r'(?:UTNT_.*|TNT.*_CONCEPT)\.md$', name, re.I):
                issues.append(f'{relative}: documentation belongs in docs/utnt or tutnt/.codex/notes')
            if temporary:
                issues.append(f'{relative}: temporary output belongs under tutnt/.codex')
    if workspace_config:
        config = json.loads(Path(workspace_config).read_text(encoding='utf-8'))
        workspace = Path(config['workspace'])
        if not workspace.is_dir():
            issues.append(f'Configured chat workspace not found: {workspace}')
        else:
            allowed = {x.casefold() for x in config['existing_entries']}
            for path in workspace.iterdir():
                if path.name.casefold() not in allowed:
                    issues.append(f'{path}: new chat workspace entry; use tutnt/.codex/work/<topic>')
    return sorted(issues)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--workspace-config', type=Path)
    args = parser.parse_args()
    config = args.workspace_config or args.root/'tutnt/.codex/policy/workspace-root.json'
    issues = violations(args.root, config if config.is_file() else None)
    print(json.dumps({'ok': not issues, 'violations': issues}, indent=2, ensure_ascii=False))
    return int(bool(issues))

if __name__ == '__main__':
    raise SystemExit(main())
