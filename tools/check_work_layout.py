"""Read-only check for misplaced UTNT work files and broken compatibility paths.

Run before finishing a task. No files are moved or deleted. Existing legacy chat
workspace entries are allowed by a local baseline; only new top-level entries
there are reported. Inside the repository, known temporary file types are checked.
"""
from work_paths import codex_root
import argparse
import json
import os
from pathlib import Path
import re
from build_definition_tables import DIRECTORIES

ROOT = Path(__file__).resolve().parent.parent
ALIASES = {'logs': 'logs', '_references': 'references',
           'tools/validation': 'validation', 'tools/__pycache__': 'cache/python',
           'tools/ui-regression-tests/acs': 'cache/ui-regression-acs'}

def is_link(path):
    """Recognize broken NTFS junctions as well as symlinks on Python 3.11+."""
    try:
        attributes = getattr(path.lstat(), 'st_file_attributes', 0)
    except FileNotFoundError:
        return False
    return path.is_symlink() or bool(attributes & 0x400)


def violations(root, workspace_config=None):
    root = Path(root).resolve()
    central = codex_root(root)
    issues = []
    external = not central.is_relative_to(root)
    retired = [root/'tutnt/.codex'] if external else []
    for path in retired:
        if path.exists() or is_link(path):
            issues.append(f'{path}: retired compatibility path; use {central}')
    if (root/'docs').exists() or (root/'docs').is_symlink():
        issues.append('docs: retired directory; keep documentation under _docs')
    for old, new in ALIASES.items():
        path = root/old
        if external and (path.exists() or is_link(path)):
            issues.append(f'{old}: retired compatibility path; use {central/new}')
        elif path.exists() and path.resolve() != (central/new).resolve():
            issues.append(f'{old}: compatibility path must point to {central/new}')
    for folder, dirs, files in os.walk(root, followlinks=False):
        kept = []
        for name in dirs:
            path = Path(folder)/name
            relative = path.relative_to(root).as_posix()
            if name == '.git' or path == central or relative in ALIASES:
                continue
            if is_link(path):
                continue
            if name in ('.codex', '__pycache__'):
                issues.append(f'{relative}: use the central agent workspace {central}')
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
                issues.append(f'{relative}: documentation belongs in _docs/utnt or {central}/notes')
            group = name.split('.', 1)[0].upper()
            if path.parent == root/'tutnt' and group in DIRECTORIES and name != group+'.txt':
                issues.append(f'{relative}: definition module belongs under tutnt/{DIRECTORIES[group]}')
            if temporary:
                issues.append(f'{relative}: temporary output belongs under {central}')
    if workspace_config:
        config = json.loads(Path(workspace_config).read_text(encoding='utf-8'))
        workspace = Path(config['workspace'])
        if not workspace.is_dir():
            issues.append(f'Configured chat workspace not found: {workspace}')
        else:
            allowed = {x.casefold() for x in config['existing_entries']}
            for path in workspace.iterdir():
                if path.name.casefold() not in allowed:
                    issues.append(f'{path}: new chat workspace entry; use {central}/work/<topic>')
    return sorted(issues)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--workspace-config', type=Path)
    parser.add_argument('--project', choices=('utnt', 'zdcmp1'), default='utnt')
    parser.add_argument('--workspace', type=Path, help='Explicit workspace for a scoped project check')
    args = parser.parse_args()
    if args.project == 'zdcmp1':
        from check_zdcmp1_layout import violations as project_violations
        issues = project_violations(args.root, args.workspace, args.workspace_config)
        print(json.dumps({'ok': not issues, 'violations': issues}, indent=2))
        return int(bool(issues))
    config = args.workspace_config or codex_root(args.root)/'policy/workspace-root.json'
    issues = violations(args.root, config if config.is_file() else None)
    print(json.dumps({'ok': not issues, 'violations': issues}, indent=2, ensure_ascii=False))
    return int(bool(issues))

if __name__ == '__main__':
    raise SystemExit(main())
