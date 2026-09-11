"""Capture fixed ending-fracture views, with an optional POM-off comparison.
Use central .codex/work and .codex/validation paths; logs must be a central junction.
"""
from pathlib import Path
import argparse,json,shutil
from check_engine import run_case
R=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--out',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
p.add_argument('--mod',type=Path,default=R/'tutnt.pk3');p.add_argument('--fixture',type=Path,default=R/'tools/credits-tests')
p.add_argument('--engine',type=Path,required=True);p.add_argument('--iwad',type=Path,required=True)
p.add_argument('--renderer',default='1');p.add_argument('--baseline',action='store_true');a=p.parse_args()
label='fracture-material-'+a.renderer+('-flat' if a.baseline else '-relief')
fixture=a.work/label;shutil.copytree(a.fixture,fixture,dirs_exist_ok=True)
if a.baseline:
    dest=fixture/'credits/ember-fracture.gldefs';dest.parent.mkdir(parents=True,exist_ok=True)
    text=(R/'tutnt/credits/ember-fracture.gldefs').read_text(encoding='utf-8-sig')
    assert text.count('ORGANIC_DEPTH = "4.0"')==1
    dest.write_text(text.replace('ORGANIC_DEPTH = "4.0"','ORGANIC_DEPTH = "0.0"'),encoding='utf-8')
commands=['unbindall','wait 420','creditlookbaseline true']
for view in range(3):commands+=['netevent creditstest 20 '+str(view),'wait 20','screenshot logs/'+label+'-'+str(view)+'.png']
commands+=['creditlookbaseline false','wait 10','screenshot logs/'+label+'-graded.png','echo UTNT_TEST_END','quit']
a.out.mkdir(parents=True,exist_ok=True)
r=run_case(a.engine,a.iwad,root=a.out,mod=a.mod,addon=fixture,mapname='ENDMAP01',renderer=a.renderer,label=label,timeout=65,settings=[('win_w',1298),('win_h',767),('screenblocks',12),('con_notifytime',0),('vid_maxfps',60),('i_pauseinbackground',False),('vid_activeinbackground',True),('use_mouse',False),('use_joystick',False),('gl_texture_filter',0)],commands='; '.join(commands)+'\n')
if r['assertions']<5:r['ok']=False;r['errors'].append('missing view assertions')
(a.out/(label+'.json')).write_text(json.dumps(r,indent=2),encoding='utf-8')
if not r['ok']:print(Path(r['log']).read_text(encoding='utf-8')[-6000:]);raise SystemExit(1)
