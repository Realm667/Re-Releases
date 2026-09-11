"""Native selective-glow regression on OpenGL/Vulkan; all output stays in .codex.

Uses the existing industrial test room, with an isolated addon and test saves.
"""
from pathlib import Path
import argparse, json, os, shutil
from check_engine import ROOT, run_case


def check_glow_colors(on_path, off_path, repeat_path):
    """Measure the glow alone, not the already-colored original projectiles."""
    from PIL import Image, ImageChops
    on, off, repeat = [Image.open(p).convert('RGB') for p in (on_path, off_path, repeat_path)]
    assert on.size == off.size == repeat.size
    delta = ImageChops.subtract(on, off)
    w, h = delta.size
    # The status-bar face keeps animating during freeze; compare the same
    # effect region that is measured below, excluding the unrelated HUD.
    region = (0, h//10, w, h*4//5)
    assert ImageChops.difference(off, repeat).crop(region).getbbox() is None, 'Frozen effect region changed'
    measurements = {}
    for i, name in enumerate(('blue', 'green', 'orange')):
        data = delta.crop((i*w//3, h//10, (i+1)*w//3, h*4//5)).tobytes()
        pixels = zip(data[0::3], data[1::3], data[2::3])
        sums = [0, 0, 0]
        for rgb in pixels:
            if max(rgb) >= 6:
                for c in range(3): sums[c] += rgb[c]
        r, g, b = sums
        ok = (b > 1.3*r and b > 1.1*g) if i == 0 else ((g > 1.15*r and g > 1.3*b) if i == 1 else (r > 1.15*g and r > 1.4*b))
        measurements[name] = {'rgb_sum': sums, 'ok': ok}
    assert all(v['ok'] for v in measurements.values()), measurements
    return measurements


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine', type=Path, default=os.environ.get('UTNT_ENGINE', 'F:/DoomDev/uzdoom.exe'))
    p.add_argument('--iwad', type=Path, default=os.environ.get('UTNT_IWAD', 'F:/DoomDev/DOOM2.WAD'))
    p.add_argument('--mod', type=Path, default=ROOT/'tutnt.pk3')
    p.add_argument('--renderer', choices=['0','1'], default='1')
    a = p.parse_args()
    work = ROOT/'tutnt/.codex/work/effect-glow'
    addon = work/'addon'
    (addon/'maps').mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT/'tools/industrial-revision-tests/maps/utntifx.wad', addon/'maps/utntifx.wad')
    shutil.copyfile(ROOT/'tools/fixtures/effect-glow/ZSCRIPT', addon/'zscript.zc')
    (addon/'MAPINFO').write_text('gameinfo { AddEventHandlers="UTNTGlowTest" }\nmap UTNTIFX "Glow validation" { levelnum=98 }\n')
    compiled = run_case(a.engine, a.iwad, mod=a.mod, addon=addon, label='effect-glow-fixture-compile')
    if not compiled['ok']:
        print(Path(compiled['log']).read_text(encoding='utf-8')[-5000:])
        return 1
    commands = [
        'wait 300', 'netevent glowclassify', 'wait 80', 'netevent glowspawn', 'wait 12',
        'event glowcheck 6 1', 'screenshot logs/effect-glow-on-'+a.renderer+'.png',
        'save effect-glow-'+a.renderer, 'wait 5',
        'UTNT_effectglow false', 'wait 3', 'event glowcheck 0',
        'screenshot logs/effect-glow-off-'+a.renderer+'.png',
        'UTNT_effectglow true', 'wait 3', 'event glowcheck 6 1',
        'UTNT_glowstrength 0', 'wait 3', 'event glowcheck 0',
        'UTNT_glowstrength 1', 'UTNT_glowsize 1.75', 'wait 3', 'event glowcheck 6 1 1',
        'UTNT_fxquality 0', 'wait 3', 'event glowcheck 0',
        'UTNT_fxquality 3', 'UTNT_glowstrength 0.65', 'UTNT_glowsize 1',
        'load effect-glow-'+a.renderer, 'wait 8', 'netevent glowloadtest', 'event glowcheck 6 1',
        'UTNT_lod 0', 'wait 3', 'event glowcheck 0',
        'UTNT_lod 2048', 'wait 3', 'event glowcheck 6 1',
        'netevent glowburst', 'wait 3', 'event glowcheck 2', 'wait 2',
        'screenshot logs/effect-glow-burst-'+a.renderer+'.png',
        'wait 60', 'event glowcheck 0',
        'netevent glowflood', 'wait 3', 'event glowcheck 1',
        'UTNT_reducedfx true', 'wait 3', 'event glowcheck 1',
        'netevent glowclear', 'wait 2', 'event glowcheck 1', 'wait 80', 'event glowcheck 0',
        'UTNT_reducedfx false', 'UTNT_glowstrength 1', 'UTNT_glowsize 1',
        'UTNT_shaderoverlayswitch false', 'motionblur false', 'fov 65',
        'netevent glowcolors', 'wait 8', 'freeze', 'wait 12',
        'screenshot logs/effect-glow-color-on-'+a.renderer+'.png',
        'UTNT_effectglow false', 'wait 8', 'screenshot logs/effect-glow-color-off-'+a.renderer+'.png',
        'wait 8', 'screenshot logs/effect-glow-color-repeat-'+a.renderer+'.png',
        'freeze', 'netevent glowclear', 'wait 40',
        'UTNT_effectglow true', 'netevent glowcolors', 'wait 8',
        'freeze', 'wait 8', 'netevent glowfade 3', 'wait 10', 'netevent glowfadepaused',
        'freeze', 'wait 16', 'netevent glowfadegone',
        'netevent glowcolors', 'wait 8',
        'netevent glowfade 1', 'wait 16',
        'netevent glowcolors', 'wait 8', 'netevent glowfade 0', 'wait 16', 'event glowcheck 3',
        'netevent glowfade 2', 'wait 2', 'UTNT_effectglow false', 'wait 3',
        'netevent glowfadeoff', 'event glowcheck 0',
        'netevent glowclear', 'wait 20',
        'language de', 'event glowmenu', 'wait 12', 'screenshot logs/effect-glow-menu-de-'+a.renderer+'.png',
        'language fr', 'wait 12', 'screenshot logs/effect-glow-menu-fr-'+a.renderer+'.png',
        'language es', 'wait 12', 'screenshot logs/effect-glow-menu-es-'+a.renderer+'.png',
        'language en', 'wait 12', 'screenshot logs/effect-glow-menu-en-'+a.renderer+'.png',
        'echo UTNT_TEST_END', 'wait 3', 'quit',
    ]
    result = run_case(a.engine, a.iwad, mod=a.mod, addon=addon, mapname='UTNTIFX',
        renderer=a.renderer, timeout=110, label='effect-glow-'+a.renderer,
        commands='; '.join(commands).replace('event glowcheck','netevent glowcheck'), settings=[('vid_maxfps',60),('gl_bloom','false'),
        ('i_pauseinbackground','false'),('vid_activeinbackground','true'),
        ('UTNT_effectglow','true'),('UTNT_glowstrength',0.65),('UTNT_glowsize',1),
        ('UTNT_lod',2048),('UTNT_fxquality',3),('UTNT_reducedfx','false'),
        ('r_drawplayersprites','false'),('screenblocks',11),('con_notifytime',0)])
    result['ok'] &= result['assertions'] >= 150
    if result['ok']:
        try:
            result['colors'] = check_glow_colors(*[ROOT/f'tutnt/.codex/logs/effect-glow-color-{state}-{a.renderer}.png' for state in ('on', 'off', 'repeat')])
        except (AssertionError, OSError) as error:
            result['ok'] = False
            result['errors'].append('rendered glow colors: '+str(error))
            print(result['errors'][-1])
    report = ROOT/'tutnt/.codex/validation/effect-glow'
    report.mkdir(parents=True, exist_ok=True)
    (report/f'runtime-{a.renderer}.json').write_text(json.dumps(result, indent=2)+'\n')
    if not result['ok']:
        print(Path(result['log']).read_text(encoding='utf-8')[-7000:])
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
