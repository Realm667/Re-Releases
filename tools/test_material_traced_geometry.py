"""Original-artwork landmarks and physical bounds for the final relief pass."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from build_organic_materials import ROOT,height_depth,relief
from material_traced_geometry import snow_height

# Coordinates are measured on the original diffuse art, in native texels.
# Each pair is (front solid, recessed region), never chosen from output maps.
LANDMARKS=[
 ('ADEL_W39',(8,50),(22,30),'stile / inset planks'),
 ('ADEL_W39',(28,70),(22,30),'diagonal brace / inset'),
 ('ADEL_W39',(56,90),(52,50),'metal grip / wood'),
 ('ADEL_W39',(8,40),(64,40),'stile / centre joint'),
 ('IKTCR05B',(38,27),(32,32),'upper diagonal / middle opening'),
 ('IKTCR05B',(26,39),(32,32),'lower diagonal / middle opening'),
 ('IKTCR05B',(11,32),(19,43),'frame / lower triangular opening'),
 ('IKWALL28',(17,8),(17,11),'face / S incision'),
 ('IKWALL28',(40,17),(44,17),'face / G incision'),
 ('IKWALL28',(7,48),(11,48),'face / lower left incision'),
 ('IKWALL28',(55,43),(48,42),'face / lower right incision'),
 ('IKWALL28',(48,50),(53,50),'lower right solid centre / recessed right leg'),
 ('PANBOOK',(20,45),(20,48),'shelf 1 / background'),
 ('PANBOOK',(20,58),(20,61),'shelf 2 / background'),
 ('PANBOOK',(20,70),(20,72),'shelf 3 / background'),
 ('PANBOOK',(20,84),(20,87),'shelf 4 / background'),
 ('PANBOOK',(20,96),(20,99),'shelf 5 / background'),
 ('PANBOOK',(20,109),(20,103),'bottom shelf / background'),
 ('PANBOOK',(17,38),(17,30),'book / empty air above book'),
 ('TECHG',(30,8.5),(30,12.5),'slat crown / vent opening'),
 ('TECHG',(30,20.5),(30,24.5),'slat crown / vent opening'),
 ('OTECH6',(30,72.5),(30,76.5),'repeated slat / opening'),
 ('METALF12',(12,4),(12,9),'casting / channel'),
 ('METALF12',(6,36),(9,41),'L casting / channel'),
 ('QMET10',(4,30),(24,30),'outer plate / inset plate'),
 ('QMET33',(8,30),(25,30),'outer strip / inset strip'),
 ('QTECH30',(30,50),(5,50),'dark girder / pale inset'),
 ('QTECH30',(49,25),(47,25),'cable / cavity'),
 ('QTECH31',(25,50),(5,50),'dark girder / pale inset'),
 ('QTECH31',(63,105),(60,105),'rod / cavity'),
 ('QTECH32',(30,50),(5,50),'dark girder / pale inset'),
 ('QTECH32',(59,99),(62,99),'rod / cavity'),
 ('CITYF01',(7,5),(16.5,5),'brick face / mortar'),
 ('CITYF01',(7,5),(7,8.5),'brick face / horizontal mortar'),
]

def check():
    g=json.loads((ROOT/'tools/organic-materials/generated.json').read_text(encoding='utf8'))
    selected=[m for m in g['materials'] if m.get('height_detail',{}).get('kind')=='traced-geometry']
    fields={};report=[]
    for m in selected:
        for name in m['variants']:
            v=g['variants'][name];a=np.asarray(Image.open(ROOT/'tutnt'/(v['stem']+'-height.png')))
            z=-height_depth(a)*v['depth'];fields[name]=z
            assert z.min()>=-6 and z.max()<=6,name
            assert v['trace_top']<=v['min_depth']<=v['max_depth']<=v['trace_bottom'],name
            assert (a==127).any(),name
            report.append(dict(name=name,min=float(z.min()),max=float(z.max()),neutral_pixels=int((a==127).sum())))
            # Normals must be the derivative of this exact quantized height,
            # with no translation, recoloring or separately filtered data.
            dx=(np.roll(z,-1,1)-np.roll(z,1,1))*.5*a.shape[1]/v['logical'][0]
            dy=(np.roll(z,-1,0)-np.roll(z,1,0))*.5*a.shape[0]/v['logical'][1]
            n=np.stack([-dx,dy,np.ones_like(z)],2);n/=np.linalg.norm(n,axis=2)[:,:,None]
            expected=np.clip((n*.5+.5)*255,0,255).astype(np.uint8)
            actual=np.asarray(Image.open(ROOT/'tutnt'/(v['stem']+'-normal.png')))
            assert np.max(abs(expected.astype(int)-actual.astype(int)))<=1,name
    def at(n,p):
        z=fields[n];v=g['variants'][n];x,y=p
        return float(z[int(y*z.shape[0]/v['size'][1]),int(x*z.shape[1]/v['size'][0])])
    for n,front,back,label in LANDMARKS:
        assert at(n,front)>at(n,back)+.15,(n,label,at(n,front),at(n,back))
    assert np.array_equal(fields['OTECH6'],np.tile(fields['TECHG'],(2,1)))
    assert np.array_equal(fields['QMET33'][:64],fields['QMET33'][64:])
    # A known upper-lit wave must reconstruct height in phase with geometry,
    # rather than in phase with the diffuse brightness (a quarter-wave error).
    y,x=np.mgrid[:64,:64];height=np.sin(y*2*np.pi/16)
    lum=128+45*np.cos(y*2*np.pi/16)
    rgb=np.repeat(lum.astype(np.uint8)[:,:,None],3,2)
    reconstructed=snow_height(rgb,(64,64))
    correlation=float(np.corrcoef(height.ravel(),reconstructed.ravel())[0,1]);assert correlation>.98,correlation
    tiled=snow_height(np.tile(rgb,(2,2,1)),(128,128))
    assert np.max(abs(tiled-np.tile(reconstructed,(2,2))))<.02
    result=dict(ok=True,materials=len(selected),variants=len(report),landmarks=len(LANDMARKS),snow_phase_correlation=correlation,data=report)
    p=ROOT/'tutnt/.codex/validation/material-final-pass';p.mkdir(exist_ok=True)
    (p/'data.json').write_text(json.dumps(result,indent=2),encoding='utf8');return result

if __name__=='__main__':
    r=check();print(json.dumps({k:v for k,v in r.items() if k!='data'}))
