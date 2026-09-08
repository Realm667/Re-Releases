from pathlib import Path
import numpy as np
from PIL import Image
import json,sys
w=Path(__file__).resolve().parent
path=Path(sys.argv[1])
a=np.asarray(Image.open(path).convert('RGB')).astype(float)
results=[]
for y in [270,136]:
    for x in [261,407,553,699]:
        patch=a[y-38:y+39,x-35:x+36]
        r,g,b=np.moveaxis(patch,-1,0)
        gold=(r>155)&(g>60)&(r>g*1.12)&(b<100)
        green=(g>45)&(g>r*1.45)&(g>b*1.45)
        axes=[]
        for mask in [gold,green]:
            coords=np.column_stack(np.where(mask));assert len(coords)>=5,(x,y,len(coords))
            values,vectors=np.linalg.eigh(np.cov(coords.T));axes.append(vectors[:,np.argmax(values)])
        angle=float(np.degrees(np.arccos(np.clip(abs(axes[0]@axes[1]),0,1))))
        results.append(dict(x=x,y=y,error_degrees=round(angle,3)))
print(results)
assert max(p['error_degrees'] for p in results)<6,'Rendered sparks must align with independent world-space flight markers'
