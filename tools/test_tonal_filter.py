"""Exercise local tone controls, save/load, map travel and rendered image changes."""
import argparse
import json
import os
from pathlib import Path
from check_engine import run_case

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', default=os.environ.get('UTNT_ENGINE', ROOT/'engine/uzdoom.exe'))
    parser.add_argument('--iwad', default=os.environ.get('UTNT_IWAD', 'F:/DoomDev/DOOM2.WAD'))
    parser.add_argument('--mod', type=Path, default=ROOT/'tutnt.pk3')
    parser.add_argument('--output', type=Path, default=ROOT/'tutnt/.codex/validation/tonal-filter')
    parser.add_argument('--renderer', choices=['0', '1'], default='1')
    parser.add_argument('--maps', nargs='*', default=[])
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    settings = [('vid_activeinbackground', True), ('i_pauseinbackground', False),
                ('con_notifytime', 0), ('screenblocks', 10), ('language', 'de'),
                ('use_mouse', False), ('use_joystick', False), ('vid_maxfps', 60)]
    commands = ['unbindall', 'wait 80', 'event tonalmenu', 'wait 3',
                'event tonalcheck 1 30 15', 'openmenu UTNTDisplayOptions', 'wait 8',
                'screenshot logs/tonal-menu.png', 'event tonalclose', 'wait 3', 'pause', 'wait 4',
                'UTNT_tonalfilter false', 'wait 4', 'screenshot logs/tonal-original.png',
                'event tonalcheck 0 30 15', 'UTNT_tonalfilter true', 'wait 4',
                'screenshot logs/tonal-default.png', 'event tonalcheck 1 30 15',
                'UTNT_tonalshadows 0', 'UTNT_tonalmidtones 0', 'wait 4',
                'screenshot logs/tonal-zero.png', 'event tonalcheck 0 0 0',
                'UTNT_tonalshadows 100', 'UTNT_tonalmidtones 100', 'UTNT_tonalhighlights 100',
                'wait 4', 'screenshot logs/tonal-bright.png', 'event tonalcheck 1 100 100',
                'UTNT_tonalshadows -100', 'UTNT_tonalmidtones -100', 'UTNT_tonalhighlights -100',
                'wait 4', 'screenshot logs/tonal-dark.png', 'event tonalcheck 1 -100 -100',
                'UTNT_tonalshadows 999', 'UTNT_tonalmidtones -999', 'wait 4',
                'event tonalcheck 1 100 -100', 'UTNT_tonalshadows 30', 'UTNT_tonalmidtones 15',
                'UTNT_tonalhighlights 0', 'pause', 'wait 4', 'save tonal-state', 'wait 4',
                'UTNT_tonalshadows 16', 'UTNT_tonalmidtones 11', 'load tonal-state', 'wait 8',
                'event tonalcheck 1 16 11', 'map TNT03A1', 'wait 50', 'event tonalcheck 1 16 11',
                'changemap TNT03A2', 'wait 50', 'event tonalcheck 1 16 11',
                'changemap TNT03A1', 'wait 50', 'event tonalcheck 1 16 11',
                'echo UTNT_TEST_END', 'wait 3', 'quit']
    results = [run_case(args.engine, args.iwad, root=args.output, mod=args.mod,
                       addon=ROOT/'tools/fixtures/tonal-filter', mapname='TNT01',
                       renderer=args.renderer, label='tonal-regression', timeout=100,
                       commands='; '.join(commands), settings=settings, regression=True)]
    result = results[0]
    if result['ok']:
        from PIL import Image, ImageChops, ImageStat
        frames = {name: Image.open(args.output/'logs'/f'tonal-{name}.png').convert('RGB')
                  for name in ['original', 'zero', 'default', 'bright', 'dark']}
        base = frames['original']
        def box(x1, y1, x2, y2):
            return (int(x1*base.width/960), int(y1*base.height/540),
                    int(x2*base.width/960), int(y2*base.height/540))
        # Fixed masonry avoids flame/sky shader animation that can continue
        # between paused frames; HUD labels exclude the world beside the bar.
        wall = box(780, 190, 940, 370)
        result['zero_identical'] = ImageChops.difference(base.crop(wall), frames['zero'].crop(wall)).getbbox() is None
        hud = box(170, 523, 420, 537)
        result['hud_identical'] = all(ImageChops.difference(base.crop(hud), frame.crop(hud)).getbbox() is None
                                      for frame in frames.values())
        world = (0, 0, base.width, int(base.height * 0.65))
        means = {name: sum(ImageStat.Stat(frame.crop(world)).mean) / 3 for name, frame in frames.items()}
        result['world_means'] = means
        result['ordered_brightness'] = means['dark'] < means['original'] < means['default'] < means['bright']
        result['ok'] = all(result[key] for key in ['ok', 'zero_identical', 'hud_identical', 'ordered_brightness'])
        print(json.dumps(result), flush=True)
    for mapname in args.maps:
        results.append(run_case(args.engine, args.iwad, root=args.output, mod=args.mod,
            addon=ROOT/'tools/fixtures/tonal-filter', mapname=mapname, renderer=args.renderer,
            label='tonal-'+mapname, timeout=60, settings=settings, regression=True,
            commands=f'wait 100; event tonalcheck 1 30 15; wait 3; screenshot logs/tonal-{mapname}.png; echo UTNT_TEST_END; wait 3; quit'))
    (args.output/'results.json').write_text(json.dumps(results, indent=2)+'\n', encoding='utf-8')
    for result in results:
        if not result['ok']:
            print(Path(result['log']).read_text(encoding='utf-8')[-5000:])
    return int(any(not result['ok'] for result in results))


if __name__ == '__main__':
    raise SystemExit(main())
