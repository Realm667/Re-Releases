"""Engine regression and captures for the September tester feedback.

All outputs go under tutnt/.codex. Requires a built PK3 and UZDoom 5.0.1.
"""
from pathlib import Path
import argparse,json,os
from check_engine import run_case
R=Path(__file__).resolve().parent.parent

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--engine',required=True);p.add_argument('--iwad',required=True);p.add_argument('--mod',type=Path,required=True)
 p.add_argument('--case',choices=['core','fog','menu','lava','door','switch','armor','preset','all'],default='all');a=p.parse_args()
 base=dict(root=R/'tutnt/.codex',mod=a.mod,addon=R/'tools/fixtures/tester-feedback',renderer='1',timeout=95)
 r=run_case(a.engine,a.iwad,label='tester-feedback-compile',**base)
 if not r['ok']:raise SystemExit(1)
 settings=[('developer',1),('con_notifytime',0),('i_pauseinbackground',False),('vid_maxfps',60),('language','enu'),('screenblocks',12)]
 cases={
 'preset':('TITLEMAP','wait 180; event fbpreset; wait 10;'),
 'core':('TNT01','wait 230; netevent fbcheck; netevent fbsmoke; wait 50; netevent fbpos 184 25; wait 20; screenshot logs/tester-water-above.png; wait 60; screenshot logs/tester-water-motion.png; netevent fbpos -100 0; wait 20; screenshot logs/tester-water-under.png; netevent fbscene -577 1052 0; netevent fblook 90 -35; idmypos true; wait 10; screenshot logs/tester-hud12.png; event fbkey 4; wait 10; screenshot logs/tester-redskull.png; event fbkey 2; wait 10; screenshot logs/tester-bluecard.png; event fbkey 101; wait 10; screenshot logs/tester-allkeys.png;'),
 'fog':('TNTLE','wait 180; netevent fbscene -128 -3488 0; netevent fblook 225 -8; UTNT_atmosphere false; wait 10; screenshot logs/tester-fog-off.png; UTNT_atmosphere true; wait 10; netevent fbfog 1; screenshot logs/tester-fog-on.png; save tester-fog; wait 3; load tester-fog; wait 5; netevent fbfog 1; UTNT_atmosphere false; wait 10; netevent fbfog 0; screenshot logs/tester-fog-restored.png;'),
 'menu':('TITLEMAP','wait 300; event fbmenu 0; wait 10; screenshot logs/tester-menu-main.png; event fbmenu 1; wait 10; event fbfonts; screenshot logs/tester-menu-episode-en.png; language de; wait 10; event fbfonts; screenshot logs/tester-menu-episode-de.png; language fr; wait 10; event fbfonts; screenshot logs/tester-menu-episode-fr.png; language es; wait 10; event fbfonts; screenshot logs/tester-menu-episode-es.png; event fbmenu 2; wait 10; screenshot logs/tester-menu-skill.png;'),
 'lava':('TNT02','wait 180; netevent fbscene 7517 -844 264; netevent fblook 180 18; wait 10; screenshot logs/tester-lava-a.png; wait 35; screenshot logs/tester-lava-b.png;'),
 'armor':('TNT01','wait 180; netevent fbscene -577 1052 0; netevent fblook 0 0; wait 2; netevent fbarmor; wait 70; screenshot logs/tester-armor.png; wait 5;'),
 'switch':('TNT02','wait 180; netevent fbscene 4312 -350 64; wait 2; netevent fblook 270 0; wait 2; netevent fbswitch 0; wait 2; screenshot logs/tester-switch-before.png; +use; wait 1; -use; wait 5; netevent fbswitch 1; wait 2; screenshot logs/tester-switch-after.png; wait 40; netevent fbswitch 0; wait 2;'),
 'door':('TNT01','wait 180; netevent fbscene -1242 1559 0; netevent fblook 180 0; wait 10; +use; wait 1; -use; wait 25; screenshot logs/tester-door-open.png;')}
 results=[]
 for name,(mapname,commands) in cases.items():
  if a.case not in ['all',name]:continue
  extra=[('gl_precache',True)] if name=='door' else []
  r=run_case(a.engine,a.iwad,label='tester-feedback-'+name,mapname=mapname,commands=commands+' echo UTNT_TEST_END; quit\n',settings=settings+extra,**base)
  results.append(r)
 (R/f'tutnt/.codex/validation/tester-feedback-{a.case}-results.json').write_text(json.dumps(results,indent=2)+'\n')
 raise SystemExit(0 if all(r['ok'] for r in results) else 1)
if __name__=='__main__':main()
