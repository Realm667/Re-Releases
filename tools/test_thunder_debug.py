import sys,json
from pathlib import Path
import argparse
from check_engine import run_case,ROOT
p=argparse.ArgumentParser(description="TNT02 ridge and public thunder debug regression")
p.add_argument('--engine',type=Path,required=True);p.add_argument('--iwad',type=Path,required=True)
p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3');p.add_argument('--work',type=Path,default=ROOT)
p.add_argument('--renderer',choices=['0','1'],default='1');a=p.parse_args()
W=a.work;R=ROOT;backend=a.renderer
cmd=['notarget','wait 350','utnt_thunder_off','wait 70','netevent debugmanual',f'screenshot logs/ridge-{backend}-dark.png',
 'netevent debugview 1','wait 70',f'screenshot logs/ridge-{backend}-seam.png','netevent debugview 0','wait 10']
if backend=='1':
 cmd+=['netevent debugbegin','utnt_thunder_far','wait 35','netevent debugpending','save thunder-debug',
 'wait 10','load thunder-debug','wait 210','netevent debugcheck 0 1 0',
 'netevent debugbegin','utnt_thunder_mid','wait 100','netevent debugcheck 1 1 0',
 'netevent debugbegin','utnt_thunder_near','wait 70','netevent debugcheck 2 1 0',
 'netevent debugbegin','netevent utnt_thunder_test 2 2 1','wait 70','netevent debugcheck 2 2 1',
 'netevent debugbegin','utnt_thunder_far','wait 30','utnt_thunder_off','wait 200','netevent debugmanual','netevent debugstill',
 'netevent utnt_thunder_test 4 1 0','wait 10','netevent debugmanual']
cmd+=['utnt_thunder_status','utnt_thunder_auto','wait 35','netevent debugauto','wait 10','echo UTNT_TEST_END','quit']
r=run_case(a.engine,a.iwad,root=W,
 mod=a.mod,addon=R/'tools/thunder-debug-tests',mapname='TNT02',renderer=backend,label='ridge-'+backend,timeout=110,
 commands='; '.join(cmd),settings=[('win_w',1938),('win_h',1127),('vid_maxfps',60),('vid_activeinbackground',True),
 ('vid_lowerinbackground',False),('i_pauseinbackground',False),('use_mouse',False),('gl_texture_filter',0),('screenblocks',10),('con_notifytime',0)])
(W/f'result-{backend}.json').write_text(json.dumps(r,indent=2));assert r['ok'] and r['assertions']>=(26 if backend=='1' else 2),r
