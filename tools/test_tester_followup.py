"""Regression checks for canonical keys, combat feedback and TNT03B brood cleanup."""
from pathlib import Path
import argparse, json
from check_engine import run_case, ROOT

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine',type=Path,required=True)
    p.add_argument('--iwad',type=Path,required=True)
    p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
    p.add_argument('--work',type=Path,default=ROOT/'tutnt/.codex/validation/tester-followup')
    a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
    common=dict(engine=a.engine,iwad=a.iwad,root=a.work,mod=a.mod)
    settings=[('vid_activeinbackground',True),('i_pauseinbackground',False)]
    cases=[
        ('keys','pulse-keys','TNT02',54,'wait 60;netevent keycheck;wait 3;netevent keylegacy;wait 3;netevent keyrestored;wait 3;'),
        ('combat','combat-feedback','TNT02',101,'wait 100;netevent combatcheck;wait 180;'),
        ('brood','spider-brood','TNT03B',7,'wait 100;netevent broodstart;wait 15;netevent broodlast;wait 80;save brood-complete;wait 10;load brood-complete;wait 35;netevent brooddead;wait 35;netevent broodlate;wait 5;'),
        ('brood-control','spider-brood','TNT02',6,'wait 100;netevent broodstart;wait 15;netevent broodlast;wait 80;netevent brooddead;wait 35;netevent broodlate;wait 5;'),
        ('portal','portal-occlusion','TNT03B',2,'wait 30;netevent portalview 0;wait 210;netevent portalview 1;wait 210;netevent portalcheck;wait 3;'),
    ]
    results=[]
    for label,fixture,mapname,minimum,commands in cases:
        addon=ROOT/'tools/fixtures'/fixture
        check=run_case(**common,addon=addon,label=label+'-compile');results.append(check)
        if not check['ok']:continue
        result=run_case(**common,addon=addon,mapname=mapname,label=label,timeout=90,settings=settings,
                        commands='god;notarget;'+commands+'echo UTNT_TEST_END;quit')
        result['ok'] &= result['assertions']>=minimum
        results.append(result)
    (a.work/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    return 0 if len(results)==len(cases)*2 and all(x['ok'] for x in results) else 1
if __name__=='__main__':raise SystemExit(main())
