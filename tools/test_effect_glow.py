"""Native selective-glow regression on OpenGL/Vulkan; all output stays in .codex.

Uses the existing industrial test room, with an isolated addon and test saves.
"""
from pathlib import Path
import argparse, json, os, shutil
from check_engine import ROOT, run_case


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
        'UTNT_glowstrength 1', 'UTNT_glowsize 1.75', 'wait 3', 'event glowcheck 6 1',
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
        'netevent glowclear', 'wait 80', 'event glowcheck 0',
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
    report = ROOT/'tutnt/.codex/validation/effect-glow'
    report.mkdir(parents=True, exist_ok=True)
    (report/f'runtime-{a.renderer}.json').write_text(json.dumps(result, indent=2)+'\n')
    if not result['ok']:
        print(Path(result['log']).read_text(encoding='utf-8')[-7000:])
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
