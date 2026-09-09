"""Check actual fixed-camera captures: moving clouds and stationary mountains.

Run test_cursed_sky.py --case views first, at its prescribed 1440x810 size.
The two samples are five seconds apart with weather off and the completed night transition, so the fade colour remains constant.
"""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image

def check(prefix):
 a=np.asarray(Image.open(str(prefix)+'-motion-a.png').convert('RGB'),dtype=float)
 b=np.asarray(Image.open(str(prefix)+'-motion-b.png').convert('RGB'),dtype=float)
 assert a.shape==b.shape==(810,1440,3),'unexpected capture dimensions'
 def difference(x,y,w,h):return float(np.abs(a[y:y+h,x:x+w]-b[y:y+h,x:x+w]).mean())
 cloud=difference(450,80,600,250);mountain=difference(300,565,230,60)
 result=dict(prefix=str(prefix),cloud_mean_difference=cloud,mountain_mean_difference=mountain,ok=cloud>1 and mountain<.1)
 assert result['ok'],result
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('prefix',type=Path,nargs='+');p.add_argument('--output',type=Path)
 a=p.parse_args();text=json.dumps([check(v) for v in a.prefix],indent=2);print(text)
 if a.output:a.output.write_text(text)
