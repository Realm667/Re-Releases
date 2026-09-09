"""Compare procedural lava normals against flat normals under moving test lights.

All shader overrides, the frozen phase and test actors live only in the fixture.
The normal and flat runs have identical material colors and camera positions.
"""
from pathlib import Path
import argparse,sys,re,json,zipfile

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--engine',required=True)
    p.add_argument('--iwad',required=True)
    p.add_argument('--mod',type=Path,required=True)
    p.add_argument('--height-asset',type=Path,help='Local candidate height asset.')
    p.add_argument('--shader',type=Path,help='Optional local candidate before installation.')
    p.add_argument('--renderer',choices=['0','1','both'],default='both')
    p.add_argument('--mode',choices=['bump','flat','mask','flatdepth','both'],default='both')
    p.add_argument('--pitch',type=float,default=65)
    p.add_argument('--camera-height',type=float,default=260)
    p.add_argument('--check-only',action='store_true',help='Validate previously captured bump/flat frames.')
    a=p.parse_args();sys.path.insert(0,str(a.project/'tools'))
    from test_lava import fixture
    from check_engine import run_case
    a.out=a.out.resolve();addon=fixture(a.out,96)
    if a.height_asset:
        import shutil
        (addon/'materials/lava').mkdir(parents=True,exist_ok=True)
        shutil.copy2(a.height_asset,addon/'materials/lava/crust-height.png')
    (addon/'ZSCRIPT').write_text('''version "5.0.0"
class UTNTLavaLamp : PointLightAttenuated
{
    Default { Args 255,230,200,220; }
}
class UTNTLavaTest : EventHandler
{
    Actor Cam;
    DynamicLight Lamp;
    override void NetworkProcess(ConsoleEvent e)
    {
        if(e.Name!="lavarelief") return;
        if(!Cam) Cam=Actor.Spawn("MapSpot",(0,-40,260));
        Cam.Angle=90; Cam.Pitch=65; players[0].camera=Cam;
        if(Lamp) { Lamp.Destroy(); Lamp=null; }
        if(e.Args[0]>0) Lamp=DynamicLight(Actor.Spawn("UTNTLavaLamp",e.Args[0]==1 ? (-140,130,50) : (140,130,50)));
    }
}
'''.replace('(0,-40,260)',f'(0,-40,{a.camera_height})').replace('Cam.Pitch=65',f'Cam.Pitch={a.pitch}'))
    with zipfile.ZipFile(a.mod) as z:source=z.read('shaders/lava-surface.fp').decode()
    if a.shader:source=a.shader.read_text()
    source=re.sub(r'\btimer\b','(3.750000)',source)
    binding='Texture crustHeight \"materials/lava/crust-height.png\"' if 'crustHeight' in source else ''
    (addon/'GLDEFS').write_text('\n'.join(f'Material Flat "{n}" {{ Shader "lava-relief.fp" {binding} }}' for n in ['QLAVA','QLAVA2','QLAVASB']))
    cases=[]
    for mode in ([] if a.check_only else ['bump','flat'] if a.mode=='both' else [a.mode]):
        shader=source
        if mode=='flat':
            # Keep the height-normal evaluation live in the Vulkan compiler.
            # Otherwise removing it changes shared POM floating-point folding,
            # contaminating the albedo control with a different height solution.
            flat='mat.Normal=mix(bumpedNormal,normalize(vWorldNormal.xyz),step(-100000.0,pixelpos.y));' if 'vec3 bumpedNormal=' in shader else 'mat.Normal=normalize(vWorldNormal.xyz);'
            shader,count=re.subn(r'mat\.Normal\s*=\s*[^;]+;', flat,shader)
            assert count==1
        if mode=='flatdepth':
            shader=shader.replace('vec3 hit=LavaCrustHit(raft,slope,dx,dy);','vec3 hit=vec3(raft,0.0);')
        if mode=='mask':
            shader=shader.rsplit('}',1)[0]+'mat.Base=vec4(vec3(floe),1.0); mat.Bright=vec4(1.0);\n}'
        (addon/'lava-relief.fp').write_text(shader)
        for r in ['0','1'] if a.renderer=='both' else [a.renderer]:
            label=f'lava-relief-{mode}-{r}'
            commands=['unbindall','god','notarget','wait 240','vid_setsize 1600 900','wait 30']
            for i,name in enumerate(['ambient','left','right']):
                commands += [f'netevent lavarelief {i}','wait 45',f'screenshot logs/{label}-{name}.png']
            commands+=['echo UTNT_TEST_END','wait 4','quit']
            result=run_case(a.engine,a.iwad,root=a.out,mod=a.mod,mapname='LAVATEST',addon=addon,
                renderer=r,label=label,commands='; '.join(commands)+'\n',timeout=65,
                settings=[('use_mouse',False),('use_joystick',False),('i_pauseinbackground',False),
                    ('vid_maxfps',60),('gl_texture_filter',0),('gl_bloom',False),('gl_lights',True),
                    ('screenblocks',12),('crosshair',0),('r_drawplayersprites',False),('con_notifytime',0)])
            log=Path(result['log']).read_text()
            for bad in ['Failed to compile','Shader compilation failed','Unable to load shader']:
                if bad.lower() in log.lower():result['ok']=False;result['errors'].append(bad)
            if not result['ok']:print(log[-8000:]);raise RuntimeError(result)
            cases.append(result)
    if not a.check_only:(a.out/f'relief-{a.mode}-results.json').write_text(json.dumps(cases,indent=2)+'\n')
    if a.mode=='both':
        import numpy as np
        from PIL import Image
        metrics={}
        for r in ['0','1'] if a.renderer=='both' else [a.renderer]:
            def frame(mode,light):
                return np.array(Image.open(a.out/f'logs/lava-relief-{mode}-{r}-{light}.png').convert('RGB'),dtype=float)[100:760,100:1500]
            ambient=frame('bump','ambient');flat_ambient=frame('flat','ambient')
            # Bump mapping must not bake illumination into the texture color.
            ambient_delta=float(np.abs(ambient-flat_ambient).mean())
            assert ambient_delta<0.1,('normal override changed unlit albedo',ambient_delta)
            samples={}
            for side in ['left','right']:
                b=frame('bump',side);f=frame('flat',side)
                delta=np.max(abs(b-f),axis=2)
                assert (delta>1).sum()>400,('normal mapping has no visible lighting response',side,int((delta>1).sum()))
                assert np.abs(b-ambient).mean()>0.2,('test light missing',side)
                samples[side]={'affected_pixels':int((delta>1).sum()),'max_channel_delta':float(delta.max()),'mean_channel_delta':float(abs(b-f).mean())}
            metrics[r]={'ambient_mean_delta':ambient_delta,'directional_lighting':samples}
        (a.out/'relief-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
        print(json.dumps(metrics,indent=2))

if __name__=='__main__':main()
