"""Render lava on adjacent, differently mapped surfaces and in TNTLE.

Uses original native palette assets. Requires UZDoom and DOOM2 via environment
or command line; writes fixtures, frames and logs only under the output folder.
"""
from pathlib import Path
import argparse,sys,os,json,struct,re

def fixture(out,light=160):
    addon=out/'fixture';addon.mkdir(parents=True,exist_ok=True)
    verts=[(-512,-256),(0,-256),(512,-256),(-512,768),(0,768),(512,768)]
    # Clockwise loops, right side points into the sector.
    edges=[(0,3,0,None),(3,4,0,None),(4,1,0,1),(1,0,0,None),
           (4,5,1,None),(5,2,1,None),(2,1,1,None)]
    text='namespace="zdoom";\n'
    for x,y in verts:text+=f'vertex {{ x={x}.0; y={y}.0; }}\n'
    sides=[]
    for i,(v1,v2,front,back) in enumerate(edges):
        s1=len(sides);sides.append((front,'LAVA' if i==1 else 'LAVAHR' if i==4 else 'BSTONE1',i*31))
        s2=-1
        if back is not None:s2=len(sides);sides.append((back,'-',83))
        text+=f'linedef {{ v1={v1}; v2={v2}; sidefront={s1};'+(f' sideback={s2}; twosided=true;' if back is not None else ' blocking=true;')+' }\n'
    for sector,tex,offset in sides:
        text+=f'sidedef {{ sector={sector}; texturemiddle="{tex}"; offsetx={offset}; offsety={offset+23}; }}\n'
    for i in range(2):
        text+=f'sector {{ heightfloor=0; heightceiling=640; texturefloor="QLAVA"; textureceiling="CEIL5_2"; lightlevel={light}; xpanningfloor={i*39}.0; ypanningfloor={i*57}.0; }}\n'
    text+='thing { x=0.0; y=-128.0; angle=90; type=1; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; coop=true; dm=true; }\n'
    lumps=[(b'LAVATEST',b''),(b'TEXTMAP',text.encode()),(b'ENDMAP',b'')]
    body=bytearray();directory=bytearray()
    for n,d in lumps:directory+=struct.pack('<II8s',12+len(body),len(d),n);body+=d
    (addon/'maps').mkdir(exist_ok=True)
    (addon/'maps/lavatest.wad').write_bytes(struct.pack('<4sII',b'PWAD',len(lumps),12+len(body))+body+directory)
    (addon/'MAPINFO').write_text('gameinfo { AddEventHandlers="UTNTLavaTest" }\nmap LAVATEST "Lava material test" { NoIntermission }\n')
    (addon/'ZSCRIPT').write_text('''version "5.0.0"
class UTNTLavaTest : EventHandler
{
    override void WorldTick()
    {
        if (!(level.MapName~=="LAVATEST")) return;
        if (level.time==2)
        {
            let p=players[0].mo;
            p.bInvulnerable=true; p.bNoGravity=true;
            p.SetOrigin((0,-128,100),false); p.Angle=90; p.Pitch=15;
        }
    }
    override void NetworkProcess(ConsoleEvent e)
    {
        if (e.Name=="lavaview")
        {
            let p=players[0].mo;
            p.SetOrigin(e.Args[0]==1 ? (0,430,90) : (0,-128,100),false);
            p.Pitch=e.Args[0]==1 ? 0 : 15; p.Angle=90;
        }
        if(e.Name=="lavafloor")
        {
            let tex=TexMan.CheckForTexture(e.Args[0]==1 ? "QLAVA2" : e.Args[0]==2 ? "QLAVASB" : "QLAVA");
            for(int i=0;i<level.Sectors.Size();i++) level.Sectors[i].SetTexture(sector.floor,tex);
        }
    }
}
''')
    return addon

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,default=Path(__file__).resolve().parent.parent)
    p.add_argument('--out',type=Path)
    p.add_argument('--engine',default=os.environ.get('UTNT_ENGINE'))
    p.add_argument('--iwad',default=os.environ.get('UTNT_IWAD'))
    p.add_argument('--renderer',default='1',choices=['0','1','both'])
    p.add_argument('--mod',type=Path)
    p.add_argument('--label',default='lava')
    p.add_argument('--map',default='LAVATEST',choices=['LAVATEST','TNTLE'])
    p.add_argument('--baseline',action='store_true',help='Render the original warp/UV appearance for comparison.')
    p.add_argument('--time',type=float,help='Freeze the test shader clock for controlled brightness comparisons.')
    p.add_argument('--dark',action='store_true',help='Set fixture light to 32 for an emission check.')
    p.add_argument('--bloom',action='store_true')
    a=p.parse_args();sys.path.insert(0,str(a.project/'tools'))
    from check_engine import run_case
    out=(a.out or a.project/'logs/lava-test').resolve();out.mkdir(parents=True,exist_ok=True)
    addon=fixture(out,32 if a.dark else 160)
    if a.map!='LAVATEST':
        (addon/'ZSCRIPT').write_text('''version "5.0.0"
class UTNTLavaTest : EventHandler
{
    Actor Cam;
    override void NetworkProcess(ConsoleEvent e)
    {
        if(e.Name!="lavascene") return;
        if(!Cam) Cam=Actor.Spawn("MapSpot",(0,0,0));
        Cam.SetOrigin(e.Args[0]==1 ? (100,-5300,80) : (-500,-5600,80),false);
        Cam.Angle=e.Args[0]==1 ? 155 : 90; Cam.Pitch=5;
        players[0].camera=Cam;
    }
}
''')
    if a.baseline:
        defs=''
        for name in ['QLAVA','QLAVA2','QLAVASB']:
            defs+=f'Material Flat "{name}" {{ Shader "baseline-floor.fp" }}\n'
        for name in ['LAVA','LAVAHR']:
            defs+=f'Material Texture "{name}" {{ Shader "baseline-fall.fp" }}\n'
        (addon/'GLDEFS').write_text(defs)
        (addon/'baseline-floor.fp').write_text('''void SetupMaterial(inout Material mat)
{ vec2 uv=vTexCoord.st; vec2 bend=vec2(sin(6.28318530718*(uv.y+timer*0.125)),sin(6.28318530718*(uv.x+timer*0.125)))*0.1;
SetMaterialProps(mat,uv+bend); }''')
        (addon/'baseline-fall.fp').write_text('void SetupMaterial(inout Material mat) { SetMaterialProps(mat,vTexCoord.st); }')
    else:
        (addon/'GLDEFS').unlink(missing_ok=True)
    if a.time is not None:
        if a.baseline:p.error('--time cannot be combined with --baseline')
        defs=''
        for names,kind,shader in [(['QLAVA','QLAVA2','QLAVASB'],'Flat','lava-surface.fp'),(['LAVA','LAVAHR'],'Texture','lava-fall.fp')]:
            original=(a.project/'tutnt/shaders'/shader).read_text()
            if a.mod:
                import zipfile
                with zipfile.ZipFile(a.mod) as z:original=z.read('shaders/'+shader).decode()
            (addon/shader).write_text(re.sub(r'\btimer\b',f'({a.time:.6f})',original))
            binding='Texture crustHeight \"materials/lava/crust-height.png\"' if 'crustHeight' in original else ''
            for name in names:defs+=f'Material {kind} "{name}" {{ Shader "{shader}" {binding} }}\n'
        (addon/'GLDEFS').write_text(defs)
    results=[]
    for r in ['0','1'] if a.renderer=='both' else [a.renderer]:
        label='lava-'+a.label+'-'+r
        commands=['unbindall','god','notarget','wait 240','vid_setsize 1600 900','wait 30']
        if a.map!='LAVATEST':commands+=['netevent lavascene 1','wait 10']
        for i in range(1 if a.time is not None else 8):
            commands += [f'screenshot logs/{label}-surface-{i}.png','wait 8']
        if a.map!='LAVATEST':
            commands += ['netevent lavascene 2','wait 10',f'screenshot logs/{label}-lake.png']
        if a.map=='LAVATEST':
            commands += ['netevent lavaview 1','wait 25']
            for i in range(1 if a.time is not None else 8): commands += [f'screenshot logs/{label}-fall-{i}.png','wait 4']
            for i in (1,2): commands += [f'netevent lavafloor {i}','netevent lavaview 0','wait 20',f'screenshot logs/{label}-variant-{i}.png']
            commands += [f'save {label}','wait 4',f'load {label}','wait 30',f'screenshot logs/{label}-restored.png']
        commands += ['echo UTNT_TEST_END','wait 5','quit']
        result=run_case(a.engine,a.iwad,root=out,mod=a.mod or a.project/'tutnt',mapname=a.map,
            addon=addon,renderer=r,label=label,commands='; '.join(commands)+'\n',timeout=130,
            settings=[('use_mouse',False),('use_joystick',False),('i_pauseinbackground',False),
            ('vid_activeinbackground',True),('vid_lowerinbackground',False),
            ('vid_maxfps',60),('gl_texture_filter',0),('gl_bloom',a.bloom),('gl_lights',True),
            ('screenblocks',12),('crosshair',0),('r_drawplayersprites',False),('con_notifytime',0)])
        output=Path(result['log']).read_text()
        for bad in ['Failed to compile','Shader compilation failed','Unable to load shader','nonexistent texture','Unknown texture']:
            if bad.lower() in output.lower():result['ok']=False;result['errors'].append(bad)
        if result['ok'] and a.map=='LAVATEST' and not a.baseline and a.time is None:
            try:result['pixels']=inspect_pixels(out/'logs',label)
            except Exception as ex:result['ok']=False;result['errors'].append(str(ex))
        results.append(result)
    (out/(a.label+'-results.json')).write_text(json.dumps(results,indent=2)+'\n')
    if not all(r['ok'] for r in results):
        for r in results:
            if not r['ok']:print(Path(r['log']).read_text()[-8000:])
        raise SystemExit(1)
def inspect_pixels(logs,label):
    import numpy as np
    from PIL import Image
    def frame(kind,i):
        a=np.array(Image.open(logs/f'{label}-{kind}-{i}.png').convert('RGB'),dtype=float)
        assert a.shape==(900,1600,3),a.shape
        return a
    a=frame('surface',0);b=frame('surface',3)
    floor_a=a[470:760,250:1350];floor_b=b[470:760,250:1350]
    motion=float(np.mean(np.max(abs(floor_a-floor_b),axis=2)>4))
    assert motion>0.03,('floor is not visibly animated',motion)
    static=float(np.mean(abs(a[60:220,20:180]-b[60:220,20:180])))
    assert static<1.0,('control wall changed',static)
    a=frame('fall',0)[80:430,200:1400];b=frame('fall',1)[80:430,200:1400]
    scores={k:float(np.mean(abs(a[max(0,-k):min(350,350-k)]-b[max(0,k):min(350,350+k)]))) for k in range(-96,97)}
    shift=min(scores,key=scores.get)
    assert 1<=shift<96,('fall does not advect downwards',shift)
    assert scores[shift]<scores[0]*0.85,('motion is flickering rather than advection',scores)
    seam=float(np.mean(abs(a[:,599]-a[:,600])))
    nearby=float(np.mean(abs(a[:,570:629]-a[:,571:630])))
    assert seam<max(5.0,nearby*4),('LAVA/LAVAHR boundary seam',seam,nearby)
    restored=np.array(Image.open(logs/f'{label}-restored.png').convert('RGB'))
    assert restored[400:760,:,0].max()>90,'materials missing after save/load'
    return {'surface_changed_fraction':motion,'unchanged_wall_mean_delta':static,
            'fall_downward_pixels':shift,'fall_match_error':scores[shift],
            'fall_static_error':scores[0],'different_mapping_seam_delta':seam,
            'ordinary_neighbor_delta':nearby,'save_load_frame_present':True}

if __name__=='__main__':main()
