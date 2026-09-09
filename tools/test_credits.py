"""Exercise all credit layouts, save/load, authored finale and optional Remaster cards."""
from pathlib import Path
import sys,json,argparse,subprocess,re
REPO=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(REPO/'tools'))
from check_engine import run_case
p=argparse.ArgumentParser();p.add_argument('--mode',default='visual',choices=['visual','regression','finale','remaster']);p.add_argument('--mod',type=Path,default=REPO/'tutnt.pk3');p.add_argument('--renderer',default='1');p.add_argument('--classic',action='store_true');p.add_argument('--out',type=Path,required=True);p.add_argument('--engine',type=Path,required=True);p.add_argument('--iwad',type=Path,required=True);a=p.parse_args();ROOT=a.out.resolve();ROOT.mkdir(parents=True,exist_ok=True)
ENGINE=a.engine;IWAD=a.iwad
label='credits-'+a.mode+'-'+a.renderer+('-4x3' if a.classic else '')
cmd=['unbindall','wait 420']
if a.mode=='visual':
 cmd+=['netevent creditstest 0']
 for i in range(25):cmd += [f'netevent creditstest 1 {i}','wait 15',f'screenshot logs/{label}-{i:02}.png']
elif a.mode=='regression':
 cmd+=['netevent creditstest 0','netevent creditstest 1 10','wait 3','netevent creditstest 2','wait 3','save creditstate','wait 4','netevent creditstest 1 15','wait 3','load creditstate','wait 15','netevent creditstest 3 11','netevent creditstest 4','wait 1100','netevent creditstest 5',f'screenshot logs/{label}-end.png','save creditend','wait 4','load creditend','wait 15','netevent creditstest 5']
elif a.mode=='finale':cmd+=['netevent creditstest 7','wait 10','netevent creditstest 8','wait 1100','netevent creditstest 5',f'screenshot logs/{label}-end.png']
elif a.mode=='remaster':cmd+=['netevent creditstest 9','netevent creditstest 1 25','wait 15',f'screenshot logs/{label}-remaster.png']
cmd+=['echo UTNT_TEST_END','quit']
fixture=REPO/'tools/credits-tests';addon=fixture
if a.mode=='remaster':
 addon=ROOT/'tests-remaster';addon.mkdir(exist_ok=True);(addon/'credits').mkdir(exist_ok=True)
 for f in ['MAPINFO.txt','zscript.zc']:(addon/f).write_bytes((fixture/f).read_bytes())
 (addon/'credits/remaster.txt').write_text('P|standard|1|13|Remaster\nN|FIRST CONTRIBUTOR|Remaster work\nN|SECOND CONTRIBUTOR|Additional work\nN|THIRD CONTRIBUTOR|Art\nN|FOURTH CONTRIBUTOR|Testing\n')
r=run_case(ENGINE,IWAD,root=ROOT,mod=a.mod,addon=addon,mapname='ENDMAP01',renderer=a.renderer,label=label,timeout=85,settings=[('win_w',978 if a.classic else 1298),('win_h',767),('screenblocks',12),('con_notifytime',0),('vid_maxfps',60),('i_pauseinbackground',False),('vid_activeinbackground',True),('use_mouse',False),('use_joystick',False),('gl_texture_filter',0)],commands='; '.join(cmd)+'\n')
if r['assertions']<5:r['ok']=False;r['errors'].append('missing credit assertions')
if a.mode=='visual':
 seen={int(n) for n in re.findall(r'UTNT_ASSERT PASS: credit page (\d+) layout fits',Path(r['log']).read_text())}
 if seen!=set(range(25)):r['ok']=False;r['errors'].append('not all 25 layouts verified')
(ROOT/(label+'.json')).write_text(json.dumps(r,indent=2))
if not r['ok']:print(Path(r['log']).read_text()[-6500:]);raise SystemExit(1)
