"""Check native options placement, reachable settings and navigation in UZDoom."""
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
    parser.add_argument('--languages', nargs='+', choices=['en','de','es','fr'], default=['en','de','es','fr'])
    parser.add_argument('--output', type=Path, default=ROOT/'tutnt/.codex/validation/options-menu')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    addon = ROOT/'tools/fixtures/options-menu'
    compiled = run_case(args.engine,args.iwad,root=args.output,mod=args.mod,addon=addon,label='compile')
    if not compiled['ok']:
        print(Path(compiled['log']).read_text(encoding='utf-8')[-5000:]); return 1
    menus = ['OptionsMenuSimple','UTNTOptions','UTNTControlsOptions','UTNTFeedbackOptions',
             'UTNTWorldOptions','UTNTAtmosphereOptions','UTNTEnvironmentOptions','UTNTCombatOptions',
             'UTNTVoiceOptions','UTNTComfortOptions','UTNTDisplayOptions','UTNTHUDOptions']
    results = []
    for lang in args.languages:
        commands = ['wait 70','event utntoptionscheck','wait 3']
        for menu in menus:
            commands += ['event utntoptionsclose','openmenu '+menu,'wait 8',f'screenshot logs/{lang}-{menu}.png']
        commands += ['echo UTNT_TEST_END','wait 3','quit']
        result = run_case(args.engine,args.iwad,root=args.output,mod=args.mod,addon=addon,
            mapname='TNT01',label=lang,commands='; '.join(commands),timeout=45,regression=True,
            settings=[('language',lang),('win_w',978),('win_h',587),('vid_activeinbackground',True),
                      ('i_pauseinbackground',False),('con_notifytime',0)])
        results.append(result)
        if not result['ok']:
            print(Path(result['log']).read_text(encoding='utf-8')[-5000:])
    (args.output/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    return int(any(not result['ok'] for result in results))

if __name__ == '__main__':
    raise SystemExit(main())
