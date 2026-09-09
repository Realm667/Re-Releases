"""Measure depth-dependent GPU parallax and portal continuity at frozen sky time."""
from pathlib import Path
import argparse,json,os,re,shutil,math
import numpy as np
from PIL import Image
from check_engine import run_case,ROOT
from rift_rocks import LAYERS,REFERENCE_EYE,basis

def camera_fixture():
 lines=[]
 for index,view in [(4,13),(1,15)]:
  # Both cameras stay inside the playable stacked room and clear of the beam.
  base=np.array([0. if view==13 else 1440.,-2080.,6000.])
  yaw,e,w,h,uv,light,radius,phase,distance,period=LAYERS[index]
  f,r,u=map(np.asarray,basis(yaw,e));theta=40*2*math.pi/period+phase
  point=f*distance+r*(radius*w*distance*math.cos(theta))+u*(radius*.65*h*distance*math.sin(theta))
  target=np.asarray(REFERENCE_EYE)+[-point[0],-point[2],point[1]]
  d=target-(base+[0,0,41]);angle=math.atan2(d[1],d[0]);pitch=-math.degrees(math.atan2(d[2],np.linalg.norm(d[:2])))
  for v,translation in [(view,np.zeros(3)),(view+1,np.array([512*math.sin(angle),-512*math.cos(angle),0]))]:
   pos=base+[10496,128,0]+translation
   lines.append(f'  if(View=={v}){{pos=({pos[0]:.8f},{pos[1]:.8f},6000);a={math.degrees(angle):.8f};pitch={pitch:.8f};}}')
  if view==13:lines.append(f'  if(View==17){{pos=(0,-2080,6000);a={math.degrees(angle):.8f};pitch={pitch:.8f};}}')
 return '\n'.join(lines)+'\n'

def feature(mask,near):
 remaining=mask.copy();components=[]
 for yy,xx in zip(*np.where(remaining)):
  if not remaining[yy,xx]:continue
  stack=[(yy,xx)];remaining[yy,xx]=False;xs=[];ys=[]
  while stack:
   y,x=stack.pop();xs.append(x);ys.append(y)
   for ny,nx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
    if 0<=ny<remaining.shape[0] and 0<=nx<remaining.shape[1] and remaining[ny,nx]:remaining[ny,nx]=False;stack.append((ny,nx))
  if len(xs)>300:components.append((len(xs),float(np.mean(xs)),float(np.mean(ys))))
 assert components
 # The leftmost substantial near fragment stays fully visible beside the beam;
 # other fragments can disappear behind real level geometry during the strafe.
 selected=min(components,key=lambda c:c[1]) if near else max(components)
 return selected[0],list(selected[1:])

def measure(work):
 masks={};centers={};areas={}
 for view in range(13,18):
  im=np.asarray(Image.open(work/f'view{view}.png').convert('RGB'));h,w=im.shape[:2]
  im=im[int(h*.20):int(h*.80),int(w*.25):int(w*.75)]
  # Isolated blue near layer / green far layer; the beam has a red component.
  channel=2 if view in [13,14,17] else 1
  mask=(im[:,:,channel]>235)&(im[:,:,0]<20);ys,xs=np.where(mask)
  assert len(xs)>500,(view,len(xs))
  masks[view]=mask;areas[view],centers[view]=feature(mask,view in [13,14,17])
 near=float(np.linalg.norm(np.array(centers[14])-centers[13]))
 far=float(np.linalg.norm(np.array(centers[16])-centers[15]))
 portal=int(np.count_nonzero(masks[13]!=masks[17]))
 assert near>far*2 and .2<far<10 and near<40,(near,far)
 assert portal<10,portal
 # Small jagged fragments gain/lose edge pixels under subpixel rasterization.
 # A 5% area bound still rejects substantial occlusion or a different component.
 for a,b in [(13,14),(15,16)]:assert abs(areas[a]-areas[b])/areas[a]<.05,(a,areas)
 return dict(ok=True,camera_translation_units=512,near_pixels=near,far_pixels=far,
             near_far_ratio=near/far,portal_mask_differences=portal,centroids=centers,feature_areas=areas)

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE'));p.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD'))
 p.add_argument('--mod',type=Path,default=ROOT/'tutnt');p.add_argument('--work',type=Path,required=True)
 p.add_argument('--renderer',choices=['0','1'],default='1');a=p.parse_args()
 if not a.engine or not a.iwad:p.error('Configure engine and IWAD')
 W=a.work.resolve();W.mkdir(parents=True,exist_ok=True);addon=W/'addon';addon.mkdir(exist_ok=True)
 shutil.copy2(ROOT/'tools/rift-tests/MAPINFO',addon/'MAPINFO')
 s=(ROOT/'tools/rift-tests/ZSCRIPT').read_text(encoding='utf-8').replace('  p.SetOrigin(pos,false);',camera_fixture()+'  p.SetOrigin(pos,false);')
 (addon/'ZSCRIPT').write_text(s,encoding='utf-8')
 for face in 'NESWUD':
  dest=addon/f'shaders/rift/sky-{face}.fp';dest.parent.mkdir(parents=True,exist_ok=True)
  s=(ROOT/f'tutnt/shaders/rift/sky-{face}.fp').read_text(encoding='utf-8')
  calls=[line for line in s.splitlines() if 'rocks=RiftRockLayer(' in line]
  near=next(line for line in calls if ',18000.000000000,' in line).replace('rocks','nearProbe')
  far=next(line for line in calls if ',90000.000000000,' in line).replace('rocks','farProbe')
  probe='vec4 nearProbe=vec4(0.0),farProbe=vec4(0.0);\n'+near+'\n'+far+'\nmat.Base=vec4(0.0,farProbe.a,nearProbe.a,1.0);'
  s=re.sub(r'\btimer\b','40.0',s.replace('mat.Base=vec4(color,1.0);',probe))
  dest.write_text(s,encoding='utf-8')
 cmd=['wait 350']
 for view in range(13,18):cmd += [f'netevent riftview {view}','wait 35',f'screenshot "{(W/f"view{view}.png").as_posix()}"']
 cmd+=['echo UTNT_TEST_END','wait 5','quit']
 runtime=run_case(a.engine,a.iwad,root=W,mod=a.mod,addon=addon,mapname='TNT04CN',renderer=a.renderer,label='parallax-'+a.renderer,timeout=50,commands='; '.join(cmd),settings=[('vid_maxfps',60),('i_pauseinbackground','false'),('vid_activeinbackground','true'),('screenblocks',12),('r_drawplayersprites','false'),('con_notifytime',0),('crosshair',0)])
 assert runtime['ok']
 result=measure(W);result['runtime']=runtime
 (W/'parallax.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
