"""Physical ordering, color-independent bodies, rotation and neutral-plane checks."""
import json
import numpy as np
from PIL import Image
from build_organic_materials import ROOT,height_depth,relief
from material_geometry import ALIASES

def check():
    manifest=json.loads((ROOT/'tools/organic-materials/generated.json').read_text())
    selected=[m for m in manifest['materials'] if m['profile']=='authored']
    fields={};details=[]
    for m in selected:
        for name in m['variants']:
            v=manifest['variants'][name]
            a=np.asarray(Image.open(ROOT/'tutnt'/(v['stem']+'-height.png')))
            n=np.asarray(Image.open(ROOT/'tutnt'/(v['stem']+'-normal.png')))
            z=-height_depth(a)*v['depth'];fields[name]=a
            assert z.min()>=-6 and z.max()<=6,name
            assert (a==127).any(),name+' has no neutral plane'
            assert a.shape==n.shape[:2] and list(a.shape[::-1])==v['data_size']
            flat=(a==127)
            for axis in (0,1):
                for step in (-1,1):flat&=np.roll(a,step,axis)==127
            assert np.all(n[flat,:2]==127) and np.all(n[flat,2]==255),name
            details.append(dict(name=name,min=float(z.min()),max=float(z.max()),neutral_fraction=float((a==127).mean())))
        v=manifest['variants'][m['name']];w,h=v['size']
        # Recoloring, painted shadows and logos cannot deform authored components.
        a,_=relief(np.zeros((h,w,3),np.uint8),'authored',12,v['logical'],m['height_detail'])
        b,_=relief(np.random.default_rng(667).integers(0,256,(h,w,3),dtype=np.uint8),'authored',12,v['logical'],m['height_detail'])
        assert np.array_equal(a,b),m['name']
    for skin,base in ALIASES.items():
        if skin not in fields or base not in fields:continue
        a,b=fields[skin],fields[base];hh=min(a.shape[0],b.shape[0]);ww=min(a.shape[1],b.shape[1])
        assert np.array_equal(a[:hh,:ww],b[:hh,:ww]),(skin,base)
    assert np.array_equal(fields['FTUB3'],np.rot90(fields['FTUB2']))
    def at(name,x,y):
        v=manifest['variants'][name];a=fields[name]
        return float(-height_depth(a[int(y*a.shape[0]/v['size'][1]),int(x*a.shape[1]/v['size'][0])])*v['depth'])
    checks=[('ADEL_G02',(32,30),(18,30)),('ADEL_G03',(32,55),(18,55)),('QWOOD1',(22,8),(22,36)),('QWOOD4',(22,63),(22,36)),('IKTCR05B',(32,32),(20,40)),('IKWALL28',(17,12),(17,9)),('IKWALL64',(8,60),(32,60)),('IKWALL69',(8,60),(64,60)),('PLATF2',(15,36),(10,36)),('QTECH20',(64,60),(5,60)),('QTECH25',(64,60),(5,60)),('QTECH08',(3,16),(10,16)),('QTECH07',(8,7),(16,7)),('IKCRATE1',(32,30),(32,10)),('QCRATE1',(32,30),(15,58)),('PANBOOK',(8,50),(30,50))]
    for name,front,back in checks:assert at(name,*front)>at(name,*back)+.15,(name,front,back,at(name,*front),at(name,*back))
    out=dict(ok=True,materials=len(selected),variants=len(details),semantic_order_checks=len(checks),data=details)
    p=ROOT/'tutnt/.codex/validation/material-reanalysis';p.mkdir(parents=True,exist_ok=True)
    (p/'data.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    return out
if __name__=='__main__':
    r=check();print(json.dumps({k:v for k,v in r.items() if k!='data'}))
