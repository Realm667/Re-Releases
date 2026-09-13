"""Sample the authoritative sprite alpha for local illuminated dust."""
from pathlib import Path
import argparse
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def generate(check=False):
    lines=['// Generated from the legacy alpha masks; do not edit.','class UTNTLightRayMask play','{',
           '    static double Density(int frame,double u,double v)','    {']
    for name in ('A','B'):
        with Image.open(ROOT/f'tutnt/sprites/sfx/VOLT{name}0.png') as image:
            pixels=image.getchannel('A').resize((32,32),Image.Resampling.BOX)
            values=[pixels.getpixel((x,y)) for y in range(32) for x in range(32)]
        lines.append(f'    static const int Mask{name}[] = {{'+','.join(map(str,values))+'};')
    lines += ['        if(u<0 || u>1 || v<0 || v>1)return 0;',
              '        double x=clamp(u*32-.5,0.,31.),y=clamp(v*32-.5,0.,31.);',
              '        int a=int(x),b=int(y),c=min(31,a+1),d=min(31,b+1);',
              '        double fx=x-a,fy=y-b;',
              '        double p=frame==0?MaskA[b*32+a]:MaskB[b*32+a];',
              '        double q=frame==0?MaskA[b*32+c]:MaskB[b*32+c];',
              '        double r=frame==0?MaskA[d*32+a]:MaskB[d*32+a];',
              '        double s=frame==0?MaskA[d*32+c]:MaskB[d*32+c];',
              '        return ((p+(q-p)*fx)*(1-fy)+(r+(s-r)*fx)*fy)/255.;',
              '    }','}']
    data='\n'.join(lines)+'\n';path=ROOT/'tutnt/zscript/light-ray-masks.zc'
    if check:assert path.read_text()==data,'Stale light-ray alpha samples'
    else:path.write_text(data,encoding='utf-8')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true')
    generate(p.parse_args().check)
