"""Exercise every liquid binding, animation, split sectors, walls and save/load.

Run the same fixture against OpenGL and Vulkan. Runtime-only test actors never
ship. --relief compares identical frozen materials under left/right test lights.
"""
from pathlib import Path
import argparse, json, re, struct, sys, shutil, zipfile

NAMES=['QWATER1','QWATER2','QWATER3','QWATER3A','QFWAT','QSLIME1','QSLIME2','IKSLIME1','IKSLIME2','SLIME05B','QWATERT6','QTELEPT','QTELEPOR','STARSKY1','STARSKY2']

def fixture(out,eye_level=False):
    addon=out/'fixture';(addon/'maps').mkdir(parents=True,exist_ok=True)
    vertices=[(-768,-256),(0,-256),(768,-256),(-768,1536),(0,1536),(768,1536)]
    edges=[(0,3,0,None),(3,4,0,None),(4,1,0,1),(1,0,0,None),(4,5,1,None),(5,2,1,None),(2,1,1,None)]
    text='namespace="zdoom";\n'
    for x,y in vertices:text+=f'vertex {{ x={x}.0; y={y}.0; }}\n'
    sides=[]
    for a,b,front,back in edges:
        first=len(sides);sides.append(front);second=-1
        if back is not None:second=len(sides);sides.append(back)
        text+=f'linedef {{ v1={a}; v2={b}; sidefront={first};'+(f' sideback={second}; twosided=true;' if second>=0 else ' blocking=true;')+' }\n'
    for i,sector in enumerate(sides):
        text+=f'sidedef {{ sector={sector}; texturemiddle="'+('-' if i in [2,3] else 'BSTONE1')+f'"; offsetx={i*29}; offsety={i*37}; }}\n'
    for i in range(2):text+=f'sector {{ heightfloor=0; heightceiling=512; texturefloor="QWATER1"; textureceiling="CEIL5_2"; lightlevel=184; xpanningfloor={i*57}.0; ypanningfloor={i*83}.0; rotationfloor={i*33}.0; xscalefloor={1+i*.7}; yscalefloor={1+i*.3}; }}\n'
    text+='thing { x=0.0; y=-128.0; angle=90; type=1; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; coop=true; dm=true; }\n'
    lumps=[(b'LIQTEST',b''),(b'TEXTMAP',text.encode()),(b'ENDMAP',b'')]
    body=bytearray();directory=bytearray()
    for name,blob in lumps:directory+=struct.pack('<II8s',12+len(body),len(blob),name);body+=blob
    (addon/'maps/liqtest.wad').write_bytes(struct.pack('<4sII',b'PWAD',len(lumps),12+len(body))+body+directory)
    (addon/'MAPINFO').write_text('gameinfo { AddEventHandlers="UTNTLiquidTest" }\nmap LIQTEST "Liquid materials" { NoIntermission }\n')
    choice=' : '.join(f'i=={i} ? "{name}"' for i,name in enumerate(NAMES[:-1]))+' : "'+NAMES[-1]+'"'
    code='''version "5.0.0"
class UTNTLiquidLamp : PointLightAttenuated
{
    Default { Args 255,240,220,250; }
}
class UTNTLiquidTest : EventHandler
{
    Actor Cam;
    DynamicLight Lamp;
    void SetView(int mode)
    {
        if(!Cam) Cam=Actor.Spawn("MapSpot",(0,-128,210));
        Cam.Angle=90;
        if(mode==1) { Cam.SetOrigin((0,1300,190),false); Cam.Pitch=0; }
        else if(mode==2) { Cam.SetOrigin((0,-210,290),false); Cam.Pitch=22; }
        else { Cam.SetOrigin((0,-100,180),false); Cam.Pitch=56; }
        players[0].camera=Cam;
    }
    override void WorldTick()
    {
        if(!(level.MapName~=="LIQTEST"))return;
        if(level.time==2) { players[0].mo.bInvulnerable=true; players[0].mo.bNoGravity=true; SetView(0); }
    }
    override void NetworkProcess(ConsoleEvent e)
    {
        if(e.Name=="liquidselect")
        {
            int i=e.Args[0]; String name=CHOICE;
            let tex=TexMan.CheckForTexture(name);
            if(!tex.IsValid()) { Console.Printf("UTNT_ASSERT FAIL missing liquid %s",name);return; }
            if(i<12) { for(int j=0;j<level.Sectors.Size();j++)level.Sectors[j].SetTexture(sector.floor,tex); SetView(0); }
            else { for(int j=0;j<level.Sides.Size();j++)if(j!=2 && j!=3)level.Sides[j].SetTexture(side.mid,tex); SetView(1); }
            Console.Printf("UTNT_ASSERT PASS liquid %s",name);
        }
        if(e.Name=="liquidview")SetView(e.Args[0]);
        if(e.Name=="liquidlight")
        {
            if(Lamp) {Lamp.Destroy();Lamp=null;}
            if(e.Args[0]>0)Lamp=DynamicLight(Actor.Spawn("UTNTLiquidLamp",e.Args[0]==1?(-145,140,90):(145,140,90)));
        }
    }
}
'''.replace('CHOICE',choice)
    if eye_level:code=code.replace('Cam.SetOrigin((0,-100,180),false); Cam.Pitch=56;', 'Cam.SetOrigin((0,-100,56),false); Cam.Pitch=25;')
    (addon/'ZSCRIPT').write_text(code)
    return addon

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,default=Path(__file__).resolve().parent.parent)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--engine',required=True);p.add_argument('--iwad',required=True)
    p.add_argument('--mod',type=Path);p.add_argument('--renderer',choices=['0','1','both'],default='both')
    p.add_argument('--relief',action='store_true');p.add_argument('--preview',action='store_true')
    p.add_argument('--physical',action='store_true',help='Only water, slime and blood')
    p.add_argument('--eye-level',action='store_true',help='Normal player height, no fixture lamp in motion tests')
    p.add_argument('--override-materials',action='store_true',help='Overlay project materials onto --mod for candidate tests')
    a=p.parse_args();a.out=a.out.resolve();a.out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(a.project/'tools'));from check_engine import run_case
    addon=fixture(a.out,a.eye_level);results=[]
    if a.override_materials:
        for directory in ['materials/liquids','shaders/liquids']:
            shutil.copytree(a.project/'tutnt'/directory,addon/directory,dirs_exist_ok=True)
    backends=['0','1'] if a.renderer=='both' else [a.renderer]
    modes=['bump','flat'] if a.relief else ['motion']
    if not a.relief:
        if a.override_materials:shutil.copyfile(a.project/'tutnt/GLDEFS.liquids',addon/'GLDEFS')
        else:(addon/'GLDEFS').unlink(missing_ok=True)
    for mode in modes:
        if a.relief:
            for family in ['water','slime','blood']:
                source=(a.project/f'tutnt/shaders/liquids/{family}.fp').read_text()
                source=re.sub(r'\btimer\b','(3.750000)',source)
                if mode=='flat':source=source.replace('mat.Normal=bumpedNormal;','mat.Normal=mix(bumpedNormal,normalize(vWorldNormal.xyz),step(-100000.0,pixelpos.y));')
                (addon/(family+'.fp')).write_text(source)
            definitions=(a.project/'tutnt/GLDEFS.liquids').read_text()
            for family in ['water','slime','blood']:definitions=definitions.replace('shaders/liquids/'+family+'.fp',family+'.fp')
            (addon/'GLDEFS').write_text(definitions)
        for backend in backends:
            label=f'liquids-{mode}-{backend}'
            commands=['unbindall','god','notarget','wait 180','vid_setsize 1280 720','wait 30']
            if a.relief:
                for i in [0,5,10]:
                    commands += [f'netevent liquidselect {i}','wait 35']
                    for light in [0,1,2]:commands += [f'netevent liquidlight {light}','wait 45',f'screenshot logs/{label}-{NAMES[i]}-{light}.png']
            else:
                for i in ([0,5,10] if a.physical else [0,5,10,11,12,13,14] if a.preview else range(len(NAMES))):
                    commands += [f'netevent liquidselect {i}',f'netevent liquidlight {0 if a.eye_level else 1}','wait 40',f'screenshot logs/{label}-{NAMES[i]}-a.png','wait 30',f'screenshot logs/{label}-{NAMES[i]}-b.png']
                    if a.eye_level:
                        for frame in range(12):commands += ['wait 5',f'screenshot logs/{label}-{NAMES[i]}-clip-{frame:02}.png']
                for i in [0,5,10]:commands += [f'netevent liquidselect {i}','netevent liquidview 2','wait 35',f'screenshot logs/{label}-{NAMES[i]}-far.png']
                commands += [f'save {label}','wait 8',f'load {label}','wait 40',f'screenshot logs/{label}-restored.png']
            commands += ['echo UTNT_TEST_END','wait 4','quit']
            r=run_case(a.engine,a.iwad,root=a.out,mod=a.mod or a.project/'tutnt',addon=addon,mapname='LIQTEST',renderer=backend,label=label,commands='; '.join(commands)+'\n',timeout=120,
                settings=[('use_mouse',False),('use_joystick',False),('i_pauseinbackground',False),('vid_maxfps',60),('gl_texture_filter',0),('gl_bloom',False),('gl_lights',True),('screenblocks',12),('crosshair',0),('r_drawplayersprites',False),('con_notifytime',0)])
            log=Path(r['log']).read_text()
            for message in ['Failed to compile','Shader compilation failed','Unable to load shader','Cannot combine warping','nonexistent texture','Unknown texture','Unknown patch']:
                if message.lower() in log.lower():r['ok']=False;r['errors'].append(message)
            results.append(r)
            if not r['ok']:print(log[-7000:]);break
    (a.out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    if not all(r['ok'] for r in results):raise SystemExit(1)
    if a.relief:verify_relief(a.out,backends)
    else:verify_motion(a.out,backends,a.eye_level)

def verify_motion(out,backends,eye_level=False):
    from PIL import Image
    import numpy as np
    result={}
    for backend in backends:
        for path in sorted((out/'logs').glob(f'liquids-motion-{backend}-*-a.png')):
            other=path.with_name(path.name.replace('-a.png','-b.png'))
            a=np.asarray(Image.open(path).convert('RGB'),dtype=float)[180:680,40:1240]
            b=np.asarray(Image.open(other).convert('RGB'),dtype=float)[180:680,40:1240]
            change=np.max(abs(a-b),axis=2)
            count=int((change>1).sum())
            assert count>20,(path.name,'animation invisible',count)
            assert a.max()>20,(path.name,'material is black')
            result[path.stem]={'animated_pixels':count,'mean_delta':float(abs(a-b).mean())}
            if eye_level:
                fraction=float((change>3).mean())
                result[path.stem]['visible_motion_fraction']=fraction
                # Residual shader motion is intentionally minimal; map-flow
                # direction and displacement are checked by test_liquid_mapflow.
                frames=[Image.open(p).convert('RGB') for p in sorted((out/'logs').glob(path.name.replace('-a.png','-clip-*.png')))]
                if frames:frames[0].save(out/(path.stem+'.webp'),save_all=True,append_images=frames[1:],duration=143,loop=0,quality=88)
        # Regression: nearest filtering on OpenGL previously lost the distant
        # half of water because higher hardware mip levels did not exist.
        water=np.asarray(Image.open(out/f'logs/liquids-motion-{backend}-QWATER1-a.png').convert('RGB'),dtype=float)
        contrast=float(water[30:300,80:1200,2].std())
        if not eye_level:assert contrast>3,(backend,'distant water detail missing',contrast)
        result[f'water-distant-{backend}']={'blue_std':contrast}
    (out/'motion-metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Motion and distant-detail pixel checks passed.')

def verify_relief(out,backends):
    from PIL import Image
    import numpy as np
    result={}
    for backend in backends:
        for name in ['QWATER1','QSLIME1','QWATERT6']:
            def frame(mode,light):return np.asarray(Image.open(out/f'logs/liquids-{mode}-{backend}-{name}-{light}.png').convert('RGB'),dtype=float)[120:630,100:1180]
            ambient=frame('bump',0);flat=frame('flat',0)
            ambientDelta=float(np.abs(ambient-flat).mean())
            assert ambientDelta<0.15,(name,backend,'unlit colors changed',ambientDelta)
            lights={}
            for light in [1,2]:
                b=frame('bump',light);f=frame('flat',light);delta=np.max(abs(b-f),axis=2)
                count=int((delta>1).sum())
                assert count>500,(name,backend,'normal mapping invisible',count)
                lights[light]={'affected_pixels':count,'mean_delta':float(np.abs(b-f).mean())}
            result[name+'-'+backend]={'ambient_delta':ambientDelta,'lights':lights}
    (out/'normal-metrics.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
