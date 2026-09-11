"""Check neutral height, signed ray intersections and the authored ORUST plate data."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from build_organic_materials import ROOT, PROFILE_BASE, encode_height, height_depth, patch_rgb


def intersect_constant(expected, top, bottom, steps):
    # Analytical oracle is expected: every ray must hit a constant plane there,
    # including zero inside a mixed protrusion/recess tracing interval.
    step=(bottom-top)/steps;layer=top
    for _ in range(steps):
        if layer>=expected:break
        layer+=step
    low=max(top,layer-step);high=layer
    for _ in range(5):
        mid=(low+high)*.5
        if mid<expected:low=mid
        else:high=mid
    den=high-low
    return low+(high-low)*np.clip((expected-low)/den,0,1) if abs(den)>1e-8 else high


def check():
    for profile,base in PROFILE_BASE.items():
        plane=encode_height(np.full((8,8),base),profile)
        assert np.all(plane==127),profile
        assert np.all(height_depth(plane)==0),profile
    for steps in [16,23,32]:
        for limits in [(-.7,.3),(-.36,0),(0,.8),(-.6,.9)]:
            for depth in [limits[0],0,limits[1],sum(limits)*.5]:
                assert abs(intersect_constant(depth,*limits,steps)-depth)<1e-7
    assert height_depth(np.array([0,127,255]))[0]>0
    assert height_depth(np.array([0,127,255]))[2]<0
    manifest=json.loads((ROOT/'tools/organic-materials/generated.json').read_text())
    config=json.loads((ROOT/'tools/organic-materials/materials.json').read_text())
    palette=np.frombuffer((ROOT/'tutnt/PLAYPAL.pal').read_bytes()[:768],np.uint8).reshape(256,3)
    variants={};rust={}
    for name,m in manifest['variants'].items():
        h=np.asarray(Image.open(ROOT/'tutnt'/(m['stem']+'-height.png')))
        d=height_depth(h)
        assert m['neutral']==127 and abs(m['base_height']-PROFILE_BASE[m['profile']])<1e-8
        assert abs(float(d.min())-m['min_depth'])<1e-7 and abs(float(d.max())-m['max_depth'])<1e-7
        assert m['trace_top']<=float(d.min()) and m['trace_bottom']>=float(d.max())
        assert (float(d.max())-float(d.min()))<=1.02,'Relief span exceeded original depth budget'
        assert max(abs(float(d.min())),abs(float(d.max())))<=1
        variants[name]=dict(inward_max=float(d.max())*m['depth'],outward_max=-float(d.min())*m['depth'])
    for name in ['ORUST01','ORUST02','ORUST03','ORUST04']:
        m=manifest['variants'][name];h=np.asarray(Image.open(ROOT/'tutnt'/(m['stem']+'-height.png')))
        n=np.asarray(Image.open(ROOT/'tutnt'/(m['stem']+'-normal.png')))
        assert np.min(h)==127 and np.max(h)>127
        plane=h==127
        for y,x in [(0,1),(0,-1),(1,0),(-1,0)]:plane &= np.roll(np.roll(h==127,y,0),x,1)
        assert plane.sum()>100
        assert np.all((n[plane,:2]>=127)&(n[plane,:2]<=128)) and np.all(n[plane,2]==255)
        rust[name]=dict(neutral_pixels=int((h==127).sum()),total_pixels=h.size,**variants[name])
    # Unmodified shared base artwork between ORUST02/03 stays at the same height
    # everywhere outside ORUST03's deliberately added three-dimensional rivets.
    a,b=[patch_rgb((ROOT/f'tutnt/textures/ogro/{name}.lmp').read_bytes(),palette) for name in ['ORUST02','ORUST03']]
    ha,hb=[np.asarray(Image.open(ROOT/'tutnt'/(manifest['variants'][name]['stem']+'-height.png'))) for name in ['ORUST02','ORUST03']]
    yy,xx=np.mgrid[:128,:64];xx=xx+.5;yy=yy+.5
    m=next(m for m in config['materials'] if m['name']=='ORUST03')
    outside=np.ones((128,64),bool)
    for cx,cy in m['height_detail']['rivets']:
        dx=np.abs(xx-cx);dy=np.abs(yy-cy);dx=np.minimum(dx,64-dx);dy=np.minimum(dy,128-dy)
        outside &= dx*dx+dy*dy>3.25**2
        assert hb[min(int(cy),127),min(int(cx),63)]>=190,'Rivet cap failed to protrude'
    shared=outside & np.all(a==b,axis=2)
    assert shared.sum()>1000 and np.array_equal(ha[shared],hb[shared])
    result=dict(ok=True,neutral_gray=127,materials=len(manifest['materials']),variants=len(variants),rust=rust,shared_rust_pixels=int(shared.sum()),analytic_planes=48)
    dest=ROOT/'tutnt/.codex/validation/neutral-relief';dest.mkdir(parents=True,exist_ok=True)
    (dest/'data.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':check()
