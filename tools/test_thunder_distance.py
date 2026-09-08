import argparse,json,sys
from pathlib import Path
import numpy as np
from PIL import Image
from check_engine import run_case,ROOT
p=argparse.ArgumentParser(description="TNT02 dark sky and distance-coupled thunder regression")
p.add_argument('--renderer',choices=['0','1'],default='1');p.add_argument('--profiles',action='store_true')
p.add_argument('--engine',type=Path,required=True);p.add_argument('--iwad',type=Path,required=True)
p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3');p.add_argument('--work',type=Path,default=ROOT)
p.add_argument('--before',type=Path,help='Optional dark screenshot of the original brighter implementation')
a=p.parse_args();W=a.work;R=ROOT
label='revision-'+a.renderer
cmd=['notarget','wait 350','netevent thunderflash 0','wait 70',f'screenshot logs/{label}-dark.png',
 'netevent thunderroof 1','wait 175',f'screenshot logs/{label}-motion.png',
 'netevent thunderflash 3 1','wait 70',f'screenshot logs/{label}-far.png',
 'netevent thunderflash 5 1','wait 70',f'screenshot logs/{label}-mid.png',
 'netevent thunderflash 8 1','wait 70',f'screenshot logs/{label}-near.png','netevent thundercheck',
 'netevent thunderview 2','wait 70','netevent thunderroof 0',f'screenshot logs/{label}-inside-near.png',
 'netevent thunderflash 0','wait 70',f'screenshot logs/{label}-inside-dark.png',
 'netevent thunderview 3','wait 70','netevent thunderroof 0']
if a.profiles:
 cmd+=['netevent thunderdistribution','wait 10','netevent thunderprofile 0','wait 35','save distant-thunder','wait 35',
 'load distant-thunder','wait 245','netevent thunderprofiledone',
 'netevent thunderprofile 1','wait 110','netevent thunderprofiledone',
 'netevent thunderprofile 2','wait 70','netevent thunderprofiledone','netevent thunderrest']
cmd+=['wait 15','echo UTNT_TEST_END','quit']
r=run_case(a.engine,a.iwad,
 root=W,mod=a.mod,addon=R/'tools/thunder-tests',mapname='TNT02',label=label,renderer=a.renderer,
 timeout=110,commands='; '.join(cmd),settings=[('win_w',1938),('win_h',1127),('vid_maxfps',60),
 ('vid_activeinbackground',True),('vid_lowerinbackground',False),('i_pauseinbackground',False),
 ('use_mouse',False),('gl_texture_filter',0),('screenblocks',10),('con_notifytime',0)])
if r['ok']:
 def read(n):return np.asarray(Image.open(W/'logs'/f'{label}-{n}.png').convert('RGB'),float)
 dark,motion,far,mid,near=[read(n) for n in ('dark','motion','far','mid','near')]
 sky=(slice(40,320),slice(850,1400));world=(slice(560,700),slice(200,650))
 r['sky_means']=[float(im[sky].mean()) for im in [dark,far,mid,near]]
 r['world_means']=[float(im[world].mean()) for im in [dark,far,mid,near]]
 r['motion']=float(np.abs(dark[sky]-motion[sky]).mean())
 r['inside_difference']=float(np.abs(read('inside-dark')[250:600,500:1400]-read('inside-near')[250:600,500:1400]).mean())
 r['blue_excess']=float((dark[sky][...,2]-dark[sky][...,0]).mean())
 if a.before:
  baseline=np.asarray(Image.open(a.before).convert('RGB'),float)
  r['sky_vs_previous']=float(dark[sky].mean()/baseline[sky].mean())
 sm,wm=r['sky_means'],r['world_means']
 checks=[r.get('sky_vs_previous',0)<.6, r['motion']>.1, r['inside_difference']<1,
         sm[0]<sm[1]<sm[2]<sm[3],sm[3]-sm[0]>80,wm[0]<wm[1]<wm[2]<wm[3],r['blue_excess']<8]
 r['ok']=all(checks) and r['assertions']>=(28 if a.profiles else 10)
 if not r['ok']:r['errors'].append('image/coverage checks failed: '+str(checks))
(W/'logs'/f'{label}-results.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r,indent=2));raise SystemExit(0 if r['ok'] else 1)
