"""Run shared Source encounter regressions in both arena variants, sequentially."""
from pathlib import Path
import argparse, json, subprocess, sys

ROOT = Path(__file__).resolve().parent.parent
CASES = {'battle': 'test_source.py', 'darkness': 'test_source_darkness.py', 'finale': 'test_source_finale.py'}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('engine', 'iwad', 'mod', 'work'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--maps', nargs='+', choices=['TNT04CN', 'TNT04C'], default=['TNT04CN', 'TNT04C'])
    p.add_argument('--renderers', nargs='+', choices=['0', '1'], default=['0', '1'])
    p.add_argument('--cases', nargs='+', choices=list(CASES), default=list(CASES))
    a = p.parse_args()
    a.work = a.work.resolve(); a.work.mkdir(parents=True, exist_ok=True)
    results = []
    for mapname in a.maps:
        for renderer in a.renderers:
            for case in a.cases:
                out = a.work / f'{mapname.lower()}-{renderer}-{case}'
                cmd = [sys.executable, '-B', str(ROOT / 'tools' / CASES[case]), '--map', mapname, '--renderer', renderer, '--work', str(out)]
                for name in ('engine', 'iwad', 'mod'):
                    cmd += ['--' + name, str(getattr(a, name).resolve())]
                code = subprocess.run(cmd, cwd=ROOT).returncode
                results.append({'map': mapname, 'renderer': renderer, 'case': case, 'ok': code == 0, 'report': str(out / 'runtime.json')})
                (a.work / 'matrix.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
                if code: return code
    return 0

if __name__ == '__main__': raise SystemExit(main())
