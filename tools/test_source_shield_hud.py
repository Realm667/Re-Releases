"""Verify real guardian-driven Source shield icons in both maps and renderers."""
from pathlib import Path
import argparse, json
from check_engine import ROOT, run_case

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('engine','iwad','mod','work'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--renderers',nargs='+',choices=['0','1'],default=['0','1'])
    a=p.parse_args();W=a.work.resolve();W.mkdir(parents=True,exist_ok=True);results=[]
    commands='; '.join(['wait 450','netevent plaqueencounter','wait 20','event plaqueshield 1','screenshot logs/closed.png',
        'netevent plaqueguardian','wait 70','event plaqueshield 0','screenshot logs/open.png',
        'save shield-open','wait 5','load shield-open','wait 20','event plaqueshield 0','screenshot logs/restored-open.png',
        'UTNT_bosspercent false','wait 5','screenshot logs/no-percent.png',
        'UTNT_bosspercent true','wait 280','event plaqueshield 1','screenshot logs/reclosed.png',
        'echo UTNT_TEST_END','wait 3','quit'])
    for mapname in ('TNT04CN','TNT04C'):
        for renderer in a.renderers:
            out=W/f'{mapname.lower()}-{renderer}';out.mkdir(exist_ok=True)
            result=run_case(a.engine,a.iwad,root=out,mod=a.mod,addon=ROOT/'tools/boss-hud-tests',mapname=mapname,
                renderer=renderer,label='shield-hud',commands=commands,timeout=100,
                settings=[('win_w',1298),('win_h',767),('screenblocks',11),('con_notifytime',0),
                          ('UTNT_bosshud',True),('UTNT_bosspercent',True),('vid_maxfps',60),
                          ('i_pauseinbackground',False),('vid_activeinbackground',True),('use_mouse',False)])
            result.update(map=mapname,renderer=renderer)
            if result['assertions']!=12:result['ok']=False;result['errors'].append('expected twelve shield assertions')
            results.append(result)
            (W/'runtime.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
            if not result['ok']:return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
