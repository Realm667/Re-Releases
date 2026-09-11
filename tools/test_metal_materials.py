"""Verify compatible metal data and render adjacent variants in a native UZDoom room.

All generated fixtures, reports and captures stay under tutnt/.codex. No game map
is edited. Requires the same NumPy/Pillow runtime as build_organic_materials.py.
"""
from pathlib import Path
import argparse, json, struct, sys
import numpy as np
from PIL import Image
from build_organic_materials import ROOT, metal_height, metal_surface, relief, validate_compatibility, height_depth
from check_engine import run_case

CENTRAL=ROOT/'tutnt/.codex'
# Related variants share the centre wall seam; outer panels exercise more variants.
CASES=[
 ('rust-panels',['ORUST01','ORUST02','ORUST03','ORUST04'],'METALF01'),
 ('rust-trims',['ORUST01','ORUST05','ORUST06','ORUST04'],'METALF02'),
 ('rivets',['QMET03','QMET01','QMET04','QMET08'],'METALF24'),
 ('iron',['QMET07','QMET05','QMET06','QMET09'],'METALF04'),
 ('trim-a',['QMET02','QMET11','QMET12','QMET13'],'METALF03'),
 ('trim-b',['QMET11','QMET13','QMET16','QMET14'],'METALF14'),
 ('trim-c',['QMET12','QMET14','QMET15','QMET16'],'METALF09'),
 ('gothic',['QMET17','QMET18','QMET19','QMET20'],'METALF06'),
 ('ornaments',['QMET21','QMET23','QMET24','QMET22'],'METALF11'),
 ('faces',['QMET25','QMET26','QMET27','QMET32'],'METALF13'),
 ('corroded',['QMET30','QMET28','QMET29','QMET31'],'METALF16'),
 ('tread',['QMET10','QMET33','QMET34','QMET10'],'METALF23'),
 ('gothic-plates',['ADEL_W53','ADEL_W53','ADEL_W54','ADEL_W54'],'METALF05'),
 ('floor-a',['METALF07','METALF08','METALF10','METALF12'],'METALF15'),
 ('floor-b',['METALF17','METALF18','METALF19','METALF20'],'METALF17'),
 ('floor-c',['METALF21','METALF22','METALF15','METALF23'],'METALF21'),
]


def data_checks():
    config=json.loads((ROOT/'tools/organic-materials/materials.json').read_text())
    manifest=json.loads((ROOT/'tools/organic-materials/generated.json').read_text())
    validate_compatibility(config)
    group=config['compatibility_groups']['metal-and-rust'];names=set(group['members'])
    assert names=={v for _,walls,floor in CASES for v in walls+[floor]},'Incomplete native fixture coverage'
    assert len(names)==66 and group['depth']==3
    # Shared crops must be independent of all other colors in the image.
    colors=np.random.default_rng(667).integers(0,256,(24,32,3),dtype=np.uint8)
    a=np.concatenate((np.zeros_like(colors),colors,np.zeros_like(colors)),axis=1)
    b=np.concatenate((np.full_like(colors,255),colors,np.full_like(colors,255)),axis=1)
    ah,an=relief(a,'metal',3,(96,24));bh,bn=relief(b,'metal',3,(96,24))
    assert np.array_equal(ah[:,32:64],bh[:,32:64])
    assert np.array_equal(an[:,33:63],bn[:,33:63])
    assert np.array_equal(metal_surface(a)[:,32:64],metal_surface(b)[:,32:64])
    # Repeating native patches must retain exactly the same relief and normals.
    h,n=relief(colors,'metal',3,(32,24))
    th,tn=relief(np.tile(colors,(2,3,1)),'metal',3,(96,48))
    assert np.array_equal(th,np.tile(h,(2,3)))
    assert np.array_equal(tn,np.tile(n,(2,3,1)))
    # Changing one member's depth must be rejected before generating bindings.
    broken=json.loads(json.dumps(config))
    next(m for m in broken['materials'] if m['name']=='ORUST06')['depth']=6
    try:validate_compatibility(broken)
    except ValueError:pass
    else:raise AssertionError('Inconsistent group accepted')
    data={};covered=0
    for name in sorted(names):
        m=manifest['variants'][name];assert m['depth']==3 and m['profile']=='metal'
        stem=ROOT/'tutnt'/m['stem']
        height=np.asarray(Image.open(str(stem)+'-height.png'))
        normal=np.asarray(Image.open(str(stem)+'-normal.png'))
        surface=np.asarray(Image.open(str(stem)+'-surface.png'))
        assert height.shape==normal.shape[:2]==surface.shape[:2]
        assert np.isfinite(normal).all() and np.min(normal[:,:,2])>127
        assert np.max(np.abs(height_depth(height))*3)<=3
        assert abs(m['min_depth']-float(height_depth(height).min()))<1e-7
        assert abs(m['max_depth']-float(height_depth(height).max()))<1e-7
        covered+=sum(base==name for base in manifest['environment_bindings'].values())
        data[name]=height
    # Verify reused native strips in the real QMET trim family (not synthetic only).
    trim_pairs=[]
    from build_organic_materials import patch_rgb
    pal=np.frombuffer((ROOT/'tutnt/PLAYPAL.pal').read_bytes()[:768],np.uint8).reshape(256,3)
    for left,right in [('QMET11','QMET12'),('QMET12','QMET13'),('QMET14','QMET15'),('ORUST05','ORUST06')]:
        folder='quake1' if left.startswith('QMET') else 'ogro'
        x=patch_rgb((ROOT/f'tutnt/textures/{folder}/{left}.lmp').read_bytes(),pal)
        y=patch_rgb((ROOT/f'tutnt/textures/{folder}/{right}.lmp').read_bytes(),pal)
        equal=np.all(x==y,axis=2)
        # Source .lmp and TEXTURES composites can differ; compare transfer directly.
        assert equal.sum()>0
        assert np.array_equal(metal_height(x)[equal],metal_height(y)[equal])
        assert np.array_equal(data[left][equal],data[right][equal]),'Generated shared relief differs'
        assert np.array_equal(metal_surface(x)[equal],metal_surface(y)[equal])
        trim_pairs.append(dict(pair=[left,right],shared_pixels=int(equal.sum())))
    return dict(ok=True,materials=len(names),environment_aliases=covered,depth=3,shared_artwork=trim_pairs,
                invariants=['shared color transfer','shared normal neighborhoods','periodic repeats','group depth guard','fixture coverage'])


def wad(text):
    chunks=[('METTEST',b''),('TEXTMAP',text.encode()),('ENDMAP',b'')];body=b'';directory=b''
    for name,data in chunks:
        directory+=struct.pack('<II8s',12+len(body),len(data),name.encode().ljust(8,b'\0'));body+=data
    return struct.pack('<4sII',b'PWAD',len(chunks),12+len(body))+body+directory


def fixture(path,baseline,manifest):
    path.mkdir(parents=True,exist_ok=True);(path/'maps').mkdir(exist_ok=True)
    # Clockwise outline: four adjoining 128-unit north-wall panels.
    vertices=[(0,0),(0,384),(128,384),(256,384),(384,384),(512,384),(512,0)]
    text='namespace="ZDoom";\n'
    for x,y in vertices:text+=f'vertex {{ x={x}; y={y}; }}\n'
    text+='sector { heightfloor=0; heightceiling=160; texturefloor="METALF15"; textureceiling="CEIL5_1"; lightlevel=208; }\n'
    for i in range(len(vertices)):
        text+=f'sidedef {{ sector=0; texturemiddle="QMET01"; }}\nlinedef {{ v1={i}; v2={(i+1)%len(vertices)}; sidefront={i}; blocking=true; }}\n'
    text+='thing { x=256; y=272; angle=90; type=1; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; coop=true; dm=true; }\n'
    text+='thing { x=256; y=280; height=96; type=9800; arg0=180; arg1=172; arg2=160; arg3=128; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; coop=true; dm=true; }\n'
    (path/'maps/METTEST.wad').write_bytes(wad(text))
    (path/'MAPINFO').write_text('GameInfo { AddEventHandlers="MetalMaterialChecks" }\nmap METTEST "Metal material regression" { levelnum=99 nointermission }\n')
    source='''version "4.14"
class MetalMaterialChecks : EventHandler {
 int View;bool Report;
 override void NetworkProcess(ConsoleEvent e){if(e.Name=="metalview"){View=e.Args[0];Report=true;}}
 override void WorldTick(){
 if(!(level.MapName~=="METTEST"))return;
 let p=players[0].mo;if(!p)return;
 p.bInvulnerable=true;p.bNoGravity=true;p.bNoClip=true;p.Vel=(0,0,0);players[0].camera=p;
 int sample=View/3;int pose=View%3;
 if(pose==0){p.SetOrigin((256,210,8),false);p.Angle=90;p.Pitch=0;}
 if(pose==1){p.SetOrigin((190,272,8),false);p.Angle=60;p.Pitch=0;}
 if(pose==2){p.SetOrigin((256,180,20),false);p.Angle=90;p.Pitch=42;}
'''
    for i,(_,walls,floor) in enumerate(CASES):
        source+=f'if(sample=={i}){{'
        for side,name in enumerate(walls,1):
            source+=f'level.Sides[{side}].SetTexture(Side.mid,TexMan.CheckForTexture("{name}",TexMan.Type_Any));'
        source+=f'level.Sectors[0].SetTexture(Sector.floor,TexMan.CheckForTexture("{floor}",TexMan.Type_Any));'
        source+='}\n'
    source+='''if(Report){
 for(int i=1;i<=4;i++)Console.Printf("METAL_SURFACE|%d|%d|%s",View,i,TexMan.GetName(level.Sides[i].GetTexture(Side.mid)));
 Console.Printf("METAL_SURFACE|%d|0|%s",View,TexMan.GetName(level.Sectors[0].GetTexture(Sector.floor)));Report=false;
 }
 }}
'''
    (path/'ZSCRIPT').write_text(source)
    if baseline:
        (path/'flat.fp').write_text('void SetupMaterial(inout Material mat){mat.Base=getTexel(vTexCoord.st);mat.Normal=normalize(vWorldNormal.xyz);mat.Specular=vec3(0);mat.SpecularLevel=0;}\n')
        names={v for _,walls,floor in CASES for v in walls+[floor]}
        (path/'GLDEFS').write_text('\n'.join(f'Material "{n}" {{ Shader "flat.fp" Normal "materials/environment/normal.png" Specular "materials/organic/black.png" }}' for n in sorted(names)))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--engine',type=Path);p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
    p.add_argument('--iwad',type=Path,default=Path('F:/DoomDev/DOOM2.WAD'));p.add_argument('--renderer',choices=['0','1'],default='1')
    p.add_argument('--live-materials',action='store_true',help='Overlay current generated materials on an existing package');p.add_argument('--baseline',action='store_true');p.add_argument('--cases',nargs='*');p.add_argument('--data-only',action='store_true')
    a=p.parse_args();dest=CENTRAL/'validation/metal-materials';dest.mkdir(parents=True,exist_ok=True)
    report=data_checks();(dest/'data.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
    if a.data_only:return
    if not a.engine:p.error('--engine required for native checks')
    manifest=json.loads((ROOT/'tools/organic-materials/generated.json').read_text())
    work=CENTRAL/'work/metal-materials';mode='baseline' if a.baseline else 'relief';path=work/(f'fixture-{mode}'+('-live' if a.live_materials else ''));fixture(path,a.baseline,manifest)
    if a.live_materials:
        import shutil
        for name in list(manifest['outputs'])+['tutnt/shaders/organic/relief.glsl','tutnt/shaders/environment/surface.glsl']:
            relative=Path(name).relative_to('tutnt')
            if relative.as_posix()=='GLDEFS.organic':relative=Path('GLDEFS')
            target=path/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
        if a.baseline:fixture(path,True,manifest)
    logs=CENTRAL/'logs/metal-materials';logs.mkdir(parents=True,exist_ok=True)
    results=[]
    import re
    chosen=[i for i,c in enumerate(CASES) if not a.cases or c[0] in a.cases]
    assert chosen,'No selected cases'
    for batch in range(0,len(chosen),6):
        selected=chosen[batch:batch+6];label=f'metal-{mode}-r{a.renderer}-{batch//6}'
        cfg='wait 90;screenblocks 12;';expected={}
        for i in selected:
            for pose in range(3):
                view=i*3+pose;name=CASES[i][0]
                cfg+=f'netevent metalview {view};wait 4;screenshot "logs/metal-materials/{mode}-r{a.renderer}-{name}-{pose}.png";wait 2;'
                expected.update({(view,s):n for s,n in enumerate(CASES[i][1],1)});expected[(view,0)]=CASES[i][2]
        cfg+='save metal-material-regression;wait 3;load metal-material-regression;wait 6;echo UTNT_TEST_END;wait 3;quit\n'
        assert len(cfg.encode())<4000
        settings=[('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_lowerinbackground',False),('use_mouse',False),('use_joystick',False),('r_drawplayersprites',False),('crosshair',0),('con_notifytime',0),('gl_texture_filter',0),('screenblocks',12)]
        result=run_case(a.engine,a.iwad,root=CENTRAL,mod=a.mod,addon=path,mapname='METTEST',renderer=a.renderer,label=label,timeout=55,commands=cfg,settings=settings,quiet=True)
        output=Path(result['log']).read_text(encoding='utf-8')
        found={(int(v),int(s)):n for v,s,n in re.findall(r'METAL_SURFACE\|(\d+)\|(\d+)\|(\S+)',output)}
        if found!=expected:result['ok']=False;result['errors'].append('Native material assignment mismatch')
        if 'ERROR:' in output or 'Failed to compile' in output:result['ok']=False;result['errors'].append('Shader compile error')
        result['live_materials']=a.live_materials;result['surfaces']=len(found);results.append(result);print(json.dumps(result),flush=True)
        if not result['ok']:print(output[-6000:]);break
    (dest/f'native-{mode}-r{a.renderer}.json').write_text(json.dumps(results,indent=2))
    raise SystemExit(0 if all(r['ok'] for r in results) else 1)

if __name__=='__main__':main()
