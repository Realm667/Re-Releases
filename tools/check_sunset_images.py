"""Verify real rendered pixels: distant snow, masking, freeze and ridge glare."""
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image

def check(prefix):
 def im(name):return np.asarray(Image.open(str(prefix)+'-'+name+'.png').convert('RGB'),dtype=float)
 def crop(a,box):x,y,r,b=box;return a[y:b,x:r]
 sky=(400,60,1100,330);mountain=(460,420,650,490);wall=(0,600,250,700)
 off,on,held,moved=(im(n) for n in ('snow-off','snow-on','snow-frozen','snow-moved'))
 stats={}
 for name,box in [('clouds',sky),('mountains',mountain)]:
  stats[name+'_snow_delta']=float(np.abs(crop(on-off,box)).mean())
  stats[name+'_freeze_max']=float(np.abs(crop(held-on,box)).max())
  stats[name+'_resumed_delta']=float(np.abs(crop(moved-held,box)).mean())
  assert stats[name+'_snow_delta']>.03,(name,'snow missing')
  assert stats[name+'_freeze_max']==0,(name,'snow moves while frozen')
  assert stats[name+'_resumed_delta']>.05,(name,'animation did not resume')
 stats['wall_delta_max']=float(np.abs(crop(on-off,wall)).max())
 assert stats['wall_delta_max']<=4,'Snow leaks onto foreground wall'
 stats['ridge_glare_delta']=float(np.abs(crop(im('afterglow-on')-im('afterglow-off'),(300,50,1200,480))).max())
 assert stats['ridge_glare_delta']<=1,'Glare remains after sun passes behind ridge'
 bare=im('south-bare');flare=im('south-flare')
 stats['glare_delta']=float(crop(flare-bare,(620,310,820,500)).mean())
 assert stats['glare_delta']>4,'Direct sun glare missing'
 mask=(bare[:,:,0]>230)&(bare[:,:,1]>150)&((bare[:,:,0]-bare[:,:,2])>65)
 mask[:200]=False;mask[550:]=False;mask[:,:500]=False;mask[:,940:]=False
 y,x=np.where(mask);assert x.size>15,'Readable sun disc missing'
 stats['sun_center']=[float(x.mean()),float(y.mean())]
 assert abs(x.mean()-720)<10 and abs(y.mean()-405)<10,'Sun/view alignment mismatch'
 stats['ok']=True
 return stats

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('prefix',type=Path);p.add_argument('--output',type=Path)
 a=p.parse_args();result=check(a.prefix);print(json.dumps(result,indent=2))
 if a.output:a.output.write_text(json.dumps(result,indent=2)+'\n')
