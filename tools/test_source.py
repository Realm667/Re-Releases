"""Source battle regression and mockup views in real TNT04CN, using isolated saves.

Tests the existing guardian death special, real attack scripts, shield collision,
save restoration, three viewpoints, local FX switches and TNT04C map isolation.
"""
from pathlib import Path
import argparse,os,json,re
from check_engine import run_case,ROOT

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE'))
 p.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD'))
 p.add_argument('--mod',type=Path,default=ROOT/'tutnt')
 p.add_argument('--work',type=Path,required=True)
 p.add_argument('--renderer',choices=['0','1'],default='1')
 a=p.parse_args()
 if not a.engine or not a.iwad:p.error('Set --engine and --iwad')
 W=a.work.resolve();W.mkdir(parents=True,exist_ok=True);label='source-'+a.renderer
 cmd=['wait 450','netevent sourcecheck 15000 0']
 def shot(name):cmd.append(f'screenshot "{(W/(label+"-"+name+".png")).as_posix()}"')
 shot('closed')
 cmd+=['netevent sourceview 3','wait 15'];shot('reference')
 cmd+=['netevent sourceview 0','wait 15']
 cmd+=['netevent sourcehit','wait 8'];shot('hit')
 cmd+=['netevent sourceguardian','wait 16','netevent sourcecheck 15000 1'];shot('guardian-open')
 cmd += [f'save {label}','wait 8',f'load {label}','wait 100','netevent sourcecheck 15000 1'];shot('restored-open')
 cmd+=['wait 320','netevent sourcecheck 15000 0','netevent sourcehp 6000','netevent sourceattack 2','wait 45','netevent sourceattackcheck 2'];shot('comet-charge')
 cmd+=['wait 40'];shot('comet-release')
 cmd+=['netevent sourceattack 3','wait 55','netevent sourceattackcheck 3'];shot('fire-charge')
 cmd+=['netevent sourceattack 1','wait 65','netevent sourceattackcheck 1'];shot('rock-charge')
 cmd+=['netevent sourceview 1','wait 10'];shot('arena-wide')
 cmd+=['netevent sourceview 2','wait 10'];shot('side')
 cmd+=['UTNT_reducedfx true','wait 20','netevent sourcecheck 6000 0'];shot('reduced')
 cmd+=['UTNT_fxquality 0','wait 15','netevent sourcecheck 6000 0'];shot('fx-zero')
 cmd+=['netevent sourceshield','wait 20','netevent sourcecheck 6000 1'];shot('fx-zero-open')
 cmd+=['UTNT_fxquality 3','UTNT_reducedfx false','netevent sourceview 0','wait 15','netevent sourcekill','wait 20'];shot('collapse')
 cmd+=['wait 100','map TNT04C','wait 100','netevent sourcecheck','echo UTNT_TEST_END','wait 5','quit']
 result=run_case(a.engine,a.iwad,root=W,mod=a.mod,addon=ROOT/'tools/source-tests',mapname='TNT04CN',
  renderer=a.renderer,label=label,timeout=180,commands='; '.join(cmd),
  settings=[('win_w',1298),('win_h',767),('screenblocks',12),('con_notifytime',0),('r_drawplayersprites','false'),
   ('crosshair',0),('vid_maxfps',60),('i_pauseinbackground','false'),('vid_activeinbackground','true')])
 log=Path(result['log']).read_text(encoding='utf-8')
 alphas=[float(v) for v in re.findall(r'SOURCE_RENDER_ALPHA ([0-9.]+)',log)]
 result['closed_render_frames']=len(alphas)
 if not alphas or any(abs(v-0.7)>0.001 for v in alphas):
  result['ok']=False;result['errors'].append('closed shield opacity changed at render time')
 if result['assertions']<65 or 'Unknown command' in log or 'requires these files' in log:
  result['ok']=False;result['errors'].append('incomplete assertions, unknown command or save dependency')
 (W/'runtime.json').write_text(json.dumps(result,indent=2)+'\n')
 if not result['ok']:print(log[-7000:])
 return 0 if result['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
