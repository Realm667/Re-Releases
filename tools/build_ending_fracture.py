"""Derive registered emission/height/normal DATA from approved ending fracture art.
Diffuse is never changed. Requires NumPy and Pillow; all outputs stay in the repo.
Height 127 is the geometric plane, matching the shared organic POM shader.
"""
from pathlib import Path
import argparse,hashlib,io,json
import numpy as np
from PIL import Image,ImageFilter
ROOT=Path(__file__).resolve().parent.parent
DEPTH=4.0
LOGICAL=192.0

def build(root=ROOT,check=False):
    folder=root/'tutnt/materials/credits/fracture'
    source=folder/'diffuse.png';im=Image.open(source).convert('RGB')
    rgb=np.asarray(im,dtype=np.float32)/255;rows,cols=rgb.shape[:2]
    # Only saturated warm fracture interiors emit; ordinary brown stone does not.
    hot=np.clip((rgb[:,:,0]-np.maximum(rgb[:,:,1],rgb[:,:,2])-.10)*5.0,0,1)
    hot*=np.clip((rgb[:,:,0]-.24)*5.0,0,1)
    def blur(a,radius):
        return np.asarray(Image.fromarray(np.uint8(np.clip(a,0,1)*255)).filter(ImageFilter.GaussianBlur(radius)),dtype=np.float32)/255
    # Enlarge the luminous core into a recessed channel including its black banks.
    core=Image.fromarray(np.uint8(hot*255))
    channel=np.asarray(core.filter(ImageFilter.MaxFilter(17)),dtype=np.float32)/255
    channel=blur(channel,3.0)
    lum=rgb @ np.array([.2126,.7152,.0722],dtype=np.float32)
    stone=np.clip((blur(lum,8.0)-.16)*4.0,-.18,.15)
    yy,xx=np.mgrid[:rows,:cols];edge=np.maximum(abs((xx+.5)/cols-.5),abs((yy+.5)/rows-.5))
    fade=np.clip((.49-edge)/.14,0,1);fade=fade*fade*(3-2*fade)
    signed=(stone*(1-channel)-channel*.95)*fade
    encoded=np.uint8(np.rint(np.clip(127+signed*127.5,0,255)))
    # Derive normals from the quantized height used by POM, in actual map units.
    height=(encoded.astype(np.float32)-127)/127.5*DEPTH
    # Suppress quantization-scale normals; retain the broad fracture walls.
    smoothed=blur(encoded.astype(np.float32)/255,4.0)
    normal_height=(smoothed*255-127)/127.5*DEPTH
    dy,dx=np.gradient(normal_height,LOGICAL/rows,LOGICAL/cols)
    normal=np.stack((-dx,dy,np.ones_like(height)),axis=2)
    normal/=np.linalg.norm(normal,axis=2,keepdims=True)
    outputs={
        'height.png':encoded,
        'normal.png':np.uint8(np.rint(np.clip(normal*.5+.5,0,1)*255)),
        'brightmap.png':np.uint8(np.rint(hot*fade*255)),
    }
    hashes={}
    for name,data in outputs.items():
        buf=io.BytesIO();Image.fromarray(data).save(buf,format='PNG',optimize=True);payload=buf.getvalue()
        target=folder/name
        if check:assert target.read_bytes()==payload,'Stale data map: '+name
        else:target.write_bytes(payload)
        hashes[name]=hashlib.sha256(payload).hexdigest()
    report=dict(diffuse_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),dimensions=[cols,rows],logical_units=LOGICAL,depth_units=DEPTH,height_neutral=127,height_min=float(height.min()),height_max=float(height.max()),emissive_fraction=float(np.mean(hot>.5)),outputs=hashes)
    assert report['height_min'] < -3 and report['height_max'] <=.61
    assert .001 < report['emissive_fraction'] < .06
    assert float(np.mean(height[hot>.7])) < -2.5,'Hot cracks must recess rather than protrude'
    manifest=root/'tools/artwork/ending-fracture/generated.json'
    if check:assert json.loads(manifest.read_text(encoding='utf-8'))==report,'Stale manifest'
    else:manifest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args();build(check=a.check)
