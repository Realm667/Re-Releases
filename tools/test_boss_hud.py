"""Render the five original boss plaques and exercise HUD lifecycle in UZDoom.
Requires UTNT_ENGINE and UTNT_IWAD; uses isolated configs/saves and writes logs/.
The fixture changes only its own test actor and the production boss adapter.
"""
import argparse, json, os, pathlib, struct
from check_engine import ROOT, run_case

def commands(label):
    result=['wait 400','event plaqueresources']
    def snap(name): result.append(f'screenshot logs/{label}-{name}.png')
    result += ['netevent plaque 1 1000 0','wait 30','event plaquecheck 1 1000 0']
    snap('hectebus-100')
    result += ['netevent plaquehp 600','wait 12','event plaquecheck 1 600 1']
    snap('damage-trail')
    result += ['wait 35','event plaquecheck 1 600 0']
    snap('hectebus-60')
    result += [f'save {label}','wait 5','netevent plaquehp 100','wait 20',f'load {label}','wait 30','event plaquecheck 1 600 0']
    snap('restored')
    for kind,hp,name in [(2,600,'bruisers-60'),(3,300,'guardian-30'),(4,100,'queen-10'),(5,300,'source-shield')]:
        result += [f'netevent plaque {kind} {hp} {int(kind==5)}','wait 30',f'event plaquecheck {kind} {hp} 0']
        snap(name)
    result += ['event plaqueshield 1','netevent plaque 5 300 0','wait 20','event plaqueshield 0']
    snap('source-exposed')
    result += ['UTNT_bosspercent false','wait 5']
    snap('no-percent')
    result += ['UTNT_bosspercent true','netevent plaquecutscene 1','wait 5']
    snap('cutscene-hidden')
    result += ['netevent plaquecutscene 0','UTNT_bosshud false','wait 5']
    snap('hud-hidden')
    result += ['UTNT_bosshud true','UTNT_reducedfx true','netevent plaquehp 1000','wait 3','netevent plaquehp 100','wait 3','event plaquecheck 5 100 2']
    snap('reduced-effects')
    result += ['UTNT_reducedfx false','netevent plaquehp 0','wait 50']
    snap('death-fade')
    result += ['wait 30','event plaquedead']
    snap('death-hidden')
    result += ['netevent plaque 1 1000 0','wait 20','vid_setsize 1920 1080','wait 20']
    snap('1080p')
    result += ['vid_setsize 1024 768','wait 20']
    snap('4by3')
    result += ['echo UTNT_TEST_END','wait 5','quit']
    return '; '.join(result)+'\n'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--renderer',choices=['0','1','both'],default='both')
    p.add_argument('--mod',type=pathlib.Path)
    p.add_argument('--label',default='boss-plaque')
    p.add_argument('--work',type=pathlib.Path,default=ROOT/'tutnt/.codex/logs/boss-hud')
    args=p.parse_args(); results=[]
    work=args.work.resolve(); work.mkdir(parents=True,exist_ok=True)
    for renderer in ['0','1'] if args.renderer=='both' else [args.renderer]:
        label=args.label+'-'+renderer
        result=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],mod=args.mod or ROOT/'tutnt',root=work,
            mapname='TNT01',addon=ROOT/'tools/boss-hud-tests',renderer=renderer,
            label=label,commands=commands(label),timeout=120,regression=True,
            settings=[('i_pauseinbackground',False),('vid_activeinbackground',True),('use_mouse',False),('vid_maxfps',60),('screenblocks',11),('con_notifytime',0),('UTNT_bosshud',True),('UTNT_bosspercent',True),('UTNT_reducedfx',False)])
        log=pathlib.Path(result['log']).read_text(encoding='utf-8')
        if 'Unknown command' in log: result['errors'].append('unknown test console command')
        for name,expected in [('1080p',(1920,1080)),('4by3',(1024,768))]:
            shot=work/'logs'/f'{label}-{name}.png'
            actual=struct.unpack('>II',shot.read_bytes()[16:24]) if shot.exists() else None
            if actual!=expected: result['errors'].append(f'{name}: expected {expected}, got {actual}')
        result['ok']=result['ok'] and not result['errors']
        results.append(result)
    (work/f'{args.label}-results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    raise SystemExit(0 if all(r['ok'] for r in results) else 1)

if __name__=='__main__': main()
