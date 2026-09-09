"""Measure actual rendered lava advection and stationary rock/cloud controls."""
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image
def check(logs,renderer):
 pre='tntle-sky-'+renderer
 def pic(name):return np.asarray(Image.open(logs/(pre+'-'+name+'.png')).convert('RGB'),dtype=float)
 a,b,c=[pic('lava-'+v) for v in 'abc'];assert a.shape==(1080,1920,3)
 lava=(slice(180,800),slice(1160,1530))
 rock=(slice(160,650),slice(800,1100))
 # Remove the static source texture before correlating two equal-time flow
 # differences. Positive shift means the luminous pattern moved downwards.
 aa,bb,cc=[p[lava].mean(axis=2) for p in (a,b,c)]
 mean=np.maximum((aa+bb+cc)/3,12);d1=(bb-aa)/mean;d2=(cc-bb)/mean
 scores={}
 for dy in range(-12,13):
  x=d1[16:-16];y=d2[16+dy:d2.shape[0]-16+dy]
  x=x-x.mean();y=y-y.mean()
  scores[dy]=float(np.sum(x*y)/np.sqrt(max(1e-20,np.sum(x*x)*np.sum(y*y))))
 best=max(scores,key=scores.get)
 # Perspective and the two flow layers prevent perfect translation. Test
 # direction against stationary/upward controls, rather than expecting a
 # high absolute correlation from this deliberately non-rigid animation.
 control=max(v for k,v in scores.items() if k<=0)
 result={'renderer':renderer,'lava_mean_abs_rgb':float(abs(b[lava]-a[lava]).mean()),'rock_mean_abs_rgb':float(abs(b[rock]-a[rock]).mean()),'downward_flow_pixels_per_7_tics':best,'flow_correlation':scores[best],
  'cloud_mean_abs_rgb_5_seconds':float(abs(pic('cloud-b')[:880]-pic('cloud-a')[:880]).mean()),
  'reduced_fx_changed_pixels':int(np.count_nonzero(np.max(abs(pic('fullfx')[:880]-pic('reduced')[:880]),axis=2)>5))}
 result['stationary_or_upward_correlation']=control
 result['direction_margin']=scores[best]-control
 result['shift_correlations']=scores
 result['ok']=result['lava_mean_abs_rgb']>.15 and result['rock_mean_abs_rgb']<.15 and 0<best<12 and scores[best]>.50 and result['direction_margin']>.05 and result['cloud_mean_abs_rgb_5_seconds']>.05 and result['reduced_fx_changed_pixels']>0
 print(json.dumps(result,indent=2));(logs/(pre+'-motion.json')).write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('logs',type=Path);p.add_argument('--renderer',default='1');a=p.parse_args();raise SystemExit(0 if check(a.logs,a.renderer)['ok'] else 1)
