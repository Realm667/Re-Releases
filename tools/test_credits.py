"""Exercise all credit layouts, save/load, authored finale and optional Remaster cards."""
from pathlib import Path
import sys,json,argparse,subprocess,re
REPO=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(REPO/'tools'))
from check_engine import run_case
p=argparse.ArgumentParser();p.add_argument('--mode',default='visual',choices=['visual','regression','finale','remaster','animation','cinematic','spark','look']);p.add_argument('--mod',type=Path,default=REPO/'tutnt.pk3');p.add_argument('--fixture',type=Path,default=REPO/'tools/credits-tests');p.add_argument('--language',default='en');p.add_argument('--renderer',default='1');p.add_argument('--classic',action='store_true');p.add_argument('--out',type=Path,required=True);p.add_argument('--engine',type=Path,required=True);p.add_argument('--iwad',type=Path,required=True);a=p.parse_args();ROOT=a.out.resolve();ROOT.mkdir(parents=True,exist_ok=True)
ENGINE=a.engine;IWAD=a.iwad
label='credits-'+a.mode+'-'+a.renderer+('-4x3' if a.classic else '')+'-'+a.language
cmd=['unbindall','wait 420']
if a.mode=='visual':
 cmd+=['netevent creditstest 0']
 for i in range(24):cmd += [f'netevent creditstest 1 {i}','wait 15',f'screenshot logs/{label}-{i:02}.png']
elif a.mode=='regression':
 cmd+=['netevent creditstest 0','netevent creditstest 1 10','wait 3','netevent creditstest 2','wait 28','save creditstate','wait 4','netevent creditstest 1 15','wait 3','load creditstate','wait 15','netevent creditstest 3 11','netevent creditstest 4','wait 1000','netevent creditstest 5',f'screenshot logs/{label}-end.png','save creditend','wait 4','load creditend','wait 15','netevent creditstest 5']
elif a.mode=='finale':cmd+=['netevent creditstest 7','wait 35','netevent creditstest 8','wait 1000','netevent creditstest 5',f'screenshot logs/{label}-end.png']
elif a.mode=='remaster':
 cmd+=['netevent creditstest 9','netevent creditstest 1 24','wait 15',f'screenshot logs/{label}-chapter.png','save creditremaster','wait 65','netevent creditstest 12','load creditremaster','wait 3','netevent creditstest 13','wait 65','netevent creditstest 12','netevent creditstest 1 25','wait 15',f'screenshot logs/{label}-remaster.png','netevent creditstest 1 26','wait 15',f'screenshot logs/{label}-remaster-next.png','netevent creditstest 7','wait 35','netevent creditstest 8']
elif a.mode=='animation':
 cmd+=['netevent creditstest 10 7 0','wait 36',f'screenshot logs/{label}-entry.png','save creditentry','wait 10','load creditentry','wait 2','netevent creditstest 14','wait 25',f'screenshot logs/{label}-settled.png']
elif a.mode=='look':
 cmd+=['listshaders']
 for i in [1,7,4,2,5]:cmd += [f'netevent creditstest 1 {i}','wait 30',f'screenshot logs/{label}-camera-{i:02}.png']
 cmd+=['netevent creditstest 1 7','wait 25','pause','wait 3',f'screenshot logs/{label}-graded.png','creditlookbaseline true','wait 4',f'screenshot logs/{label}-baseline.png','creditlookbaseline false','wait 3','pause','netevent creditstest 15','netevent utnt_credit 2','wait 785','netevent creditstest 19','save creditlook','wait 10','load creditlook','wait 2','netevent creditstest 19']
 for i in range(14):cmd+=['wait 5',f'screenshot logs/{label}-spark-{i:02}.png']
 cmd+=['wait 170','netevent creditstest 16',f'screenshot logs/{label}-end.png','map TNT01','wait 40',f'screenshot logs/{label}-outside.png']
elif a.mode=='spark':
 cmd+=['netevent creditstest 15','netevent utnt_credit 2','wait 785','netevent creditstest 19',f'screenshot logs/{label}-focus.png','save creditspark','wait 12','load creditspark','wait 2','netevent creditstest 19']
 for i in range(10):cmd+=['wait 5',f'screenshot logs/{label}-spark-{i:02}.png']
 cmd+=['wait 180','netevent creditstest 16',f'screenshot logs/{label}-end.png']
elif a.mode=='cinematic':
 cmd+=['netevent creditstest 1 7','wait 5','netevent utnt_credit 0','wait 8','netevent creditstest 17 8','save creditcut','wait 30','load creditcut','wait 2','netevent creditstest 17 8','wait 35','netevent creditstest 3 8','wait 25','netevent creditstest 15','netevent utnt_credit 2','wait 120','save creditflight','wait 30','load creditflight','wait 2','netevent creditstest 18','wait 280',f'screenshot logs/{label}-flight-a.png','wait 220',f'screenshot logs/{label}-flight-b.png','wait 340','netevent creditstest 16',f'screenshot logs/{label}-end.png']
# Network events execute on the next game tick; do not let load/quit overtake them.
cmd=[part for command in cmd for part in ([command,'wait 2'] if command.startswith('netevent ') else [command])]
cmd+=['echo UTNT_TEST_END','quit']
fixture=a.fixture.resolve();addon=fixture
if a.mode=='remaster':
 addon=ROOT/'tests-remaster';addon.mkdir(exist_ok=True);(addon/'credits').mkdir(exist_ok=True)
 import shutil
 shutil.copytree(fixture,addon,dirs_exist_ok=True)
 (addon/'credits/remaster.txt').write_text('P|standard|1|6.5|$UTNT_CREDITS_TEXT_071\nN|FIRST CONTRIBUTOR|Remaster work\nN|SECOND CONTRIBUTOR|Additional work\nN|THIRD CONTRIBUTOR|Art\nN|FOURTH CONTRIBUTOR|Testing\n')
r=run_case(ENGINE,IWAD,root=ROOT,mod=a.mod,addon=addon,mapname='ENDMAP01',renderer=a.renderer,label=label,timeout=110,settings=[('language',a.language),('win_w',978 if a.classic else 1298),('win_h',767),('screenblocks',12),('con_notifytime',0),('vid_maxfps',60),('i_pauseinbackground',False),('vid_activeinbackground',True),('use_mouse',False),('use_joystick',False),('gl_texture_filter',0)],commands='; '.join(cmd)+'\n')
if r['assertions']<5:r['ok']=False;r['errors'].append('missing credit assertions')
if a.mode=='visual':
 seen={int(n) for n in re.findall(r'UTNT_ASSERT PASS: credit page (\d+) layout fits',Path(r['log']).read_text())}
 if seen!=set(range(24)):r['ok']=False;r['errors'].append('not all 24 layouts verified')
if a.mode=='look':
 log=Path(r['log']).read_text(encoding='utf-8')
 if len(re.findall(r'Shader \(\d+\): UTNTEndingLook\s',log))!=1:r['ok']=False;r['errors'].append('ending shader must be registered exactly once')
 from PIL import Image,ImageChops,ImageStat
 try:
  graded=Image.open(ROOT/'logs'/f'{label}-graded.png').convert('RGB');baseline=Image.open(ROOT/'logs'/f'{label}-baseline.png').convert('RGB')
  scale=graded.height/720;left=(graded.width-min(1280,graded.width/scale)*scale)/2
  # Opaque text interiors avoid antialiased frame edges that reveal the world beneath.
  errors=[]
  for top in [450,532,614]:
   box=(int(left+64*scale),int(top*scale),int(left+350*scale),int((top+16)*scale))
   diff=ImageChops.difference(graded.crop(box),baseline.crop(box));errors.append(max(x[1] for x in diff.getextrema()))
  r['credit_text_max_difference']=errors
  if max(errors)>1:r['ok']=False;r['errors'].append('postprocessing changes credit text')
  world=ImageStat.Stat(ImageChops.difference(graded,baseline)).mean;r['world_mean_difference']=world
  if max(world)<.5:r['ok']=False;r['errors'].append('scene pass has no visible effect')
 except OSError as error:r['ok']=False;r['errors'].append(str(error))
(ROOT/(label+'.json')).write_text(json.dumps(r,indent=2))
if not r['ok']:print(Path(r['log']).read_text()[-6500:]);raise SystemExit(1)
