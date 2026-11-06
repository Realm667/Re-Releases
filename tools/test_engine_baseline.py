"""Verify UTNT's engine floor and real diagnostic menu actions with isolated configs."""
import argparse
import json
from pathlib import Path
import re
import zipfile
from check_engine import ROOT, run_case


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', type=Path, default=Path('F:/DoomDev/uzdoom.exe'))
    parser.add_argument('--iwad', type=Path, default=Path('F:/DoomDev/DOOM2.WAD'))
    parser.add_argument('--mod', type=Path, default=ROOT/'tutnt.pk3')
    parser.add_argument('--old-engine', type=Path, help='Optional real UZDoom 5.0.2 executable; must be rejected')
    parser.add_argument('--renderer', choices=['0', '1'], default='0')
    parser.add_argument('--timeout', type=int, default=90, help='Per-runtime timeout; raise for cold shader compilation')
    args = parser.parse_args()
    addon = ROOT/'tutnt/.codex/builds/engine-baseline-fixture.pk3'
    addon.parent.mkdir(parents=True, exist_ok=True)
    (ROOT/'tutnt/.codex/validation').mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(addon, 'w') as archive:
        for file in (ROOT/'tools/fixtures/engine-baseline').iterdir():
            archive.write(file, file.name)
        archive.write(ROOT/'tools/fixtures/voxels/maps/VXLAB.wad', 'maps/VXLAB.wad')
    results = []
    if args.old_engine:
        result = run_case(args.old_engine, args.iwad, mod=args.mod, label='engine-baseline-old', timeout=60, quiet=True)
        log = Path(result['log']).read_text(encoding='utf-8')
        rejected = (not result['ok'] and result['exit'] != -1
                    and 'requires a newer version' in log
                    and '5.0.3 is required' in log and 'only supports 5.0.2' in log)
        result['expected_rejection'] = rejected
        result['ok'] = rejected
        results.append(result)
        print(json.dumps(result), flush=True)
    for lang in ['en', 'de', 'es', 'fr']:
        out = ROOT/'tutnt/.codex/validation'
        menu_shot = out/f'engine-baseline-menu-{lang}.png'
        graph_shot = out/f'engine-baseline-graph-{lang}.png'
        for shot in (menu_shot, graph_shot):
            shot.unlink(missing_ok=True)
        commands = ['wait 70', 'event diagnostictoggle', 'wait 140',
                    'echo BASELINE_STATS_ON', 'stat', f'screenshot {graph_shot.as_posix()}',
                    'event diagnostictoggle', 'wait 3', 'echo BASELINE_STATS_OFF', 'stat',
                    'event diagnosticmenu', 'wait 5', f'screenshot {menu_shot.as_posix()}',
                    'echo UTNT_TEST_END', 'quit']
        result = run_case(args.engine, args.iwad, mod=args.mod, mapname='VXLAB',
                          addon=addon, renderer=args.renderer,
                          label='engine-baseline-'+lang, timeout=args.timeout, commands='; '.join(commands),
                          settings=[('language', lang), ('con_notifytime', 0),
                                    ('i_pauseinbackground', 'false'), ('vid_activeinbackground', 'true')], quiet=True)
        log = Path(result['log']).read_text(encoding='utf-8')
        on = log.partition('BASELINE_STATS_ON')[2].partition('BASELINE_STATS_OFF')[0]
        off = log.partition('BASELINE_STATS_OFF')[2]
        result['toggles_verified'] = all(re.search(r'\*'+stat+r'\b', on) and
                                           not re.search(r'\*'+stat+r'\b', off)
                                           for stat in ['rendergraph', 'rendertimes'])
        result['ok'] &= (result['assertions'] == 4 and result['toggles_verified']
                         and 'Unknown stat:' not in log and menu_shot.exists() and graph_shot.exists())
        results.append(result)
        print(json.dumps(result), flush=True)
        if not result['ok']:
            print(log[-6000:])
            break
    (ROOT/'tutnt/.codex/validation/engine-baseline.json').write_text(json.dumps(results, indent=2)+'\n')
    return 0 if all(result['ok'] for result in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
