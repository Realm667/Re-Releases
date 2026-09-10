"""Native map/material checks and repeatable screenshots for organic relief."""
from pathlib import Path
import argparse,json,re,sys,shutil
from check_engine import run_case
ROOT=Path(__file__).resolve().parent.parent

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mod',type=Path,required=True)
    p.add_argument('--engine',type=Path,required=True)
    p.add_argument('--iwad',type=Path,default=Path('F:/DoomDev/DOOM2.WAD'))
    p.add_argument('--renderer',choices=['0','1'],default='1')
    p.add_argument('--maps',nargs='*')
    p.add_argument('--capture',action='store_true')
    p.add_argument('--baseline',action='store_true')
    p.add_argument('--views',type=Path,default=ROOT/'tools/organic-materials/views.json')
    p.add_argument('--tag',default='organic',help='Separate fixture, capture and report names')
    p.add_argument('--live-shaders',action='store_true',help='Check current shader source over a previously built package')
    a=p.parse_args()
    if not re.fullmatch(r'[a-z0-9-]+',a.tag):p.error('--tag must use lowercase letters, numbers and hyphens')
    central=ROOT/'tutnt/.codex';work=central/'work'/f'{a.tag}-materials';logs=central/'logs'/f'{a.tag}-materials'
    work.mkdir(parents=True,exist_ok=True);logs.mkdir(parents=True,exist_ok=True)
    fixture=work/(('fixture-original' if a.baseline else 'fixture-relief')+('-live' if a.live_shaders else ''));fixture.mkdir(exist_ok=True)
    if a.live_shaders:
        for rel in ('shaders/organic/material.fp','shaders/organic/environment.fp','shaders/organic/relief.glsl','shaders/environment/surface.glsl'):
            dest=fixture/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/'tutnt'/rel,dest)
    views=json.loads(a.views.read_text())
    manifest=json.loads((ROOT/'tools/organic-materials/generated.json').read_text())
    (fixture/'MAPINFO').write_text('GameInfo { AddEventHandlers = "OrganicMaterialChecks" }\n')
    src='''version "4.14"
class OrganicMaterialChecks : EventHandler {
 int View;bool Report;
 override void NetworkProcess(ConsoleEvent e){if(e.Name=="organicview"){View=e.Args[0];Report=true;}}
 override void WorldTick(){
 let p=players[0].mo;if(!p||level.time<20)return;
 p.bInvulnerable=true;p.bNoGravity=true;p.bNoClip=true;players[0].camera=p;
 let h=UTNTThunderHandler(EventHandler.Find("UTNTThunderHandler"));if(h)h.DebugManual=true;
'''
    for i,v in enumerate(views):
        x,y,z=v['position']
        if 'sector' in v:z=f'level.Sectors[{v["sector"]}].floorplane.ZatPoint(({x},{y}))+48'
        src+=f'if(level.MapName~=="{v["map"]}" && View=={i}){{p.SetOrigin(({x},{y},{z}),false);p.Vel=(0,0,0);p.Angle={v["angle"]};p.Pitch={v["pitch"]};'
        if 'side' in v:
            src+=f'if(Report)Console.Printf("ORGANIC_SURFACE|{i}|%s",TexMan.GetName(level.Sides[{v["side"]}].GetTexture(Side.mid)));'
        elif 'sector' in v:
            src+=f'if(Report)Console.Printf("ORGANIC_SURFACE|{i}|%s",TexMan.GetName(p.CurSector.GetTexture(Sector.floor)));'
        src+='Report=false;}'
    (fixture/'ZSCRIPT').write_text(src+'}}\n')
    if a.baseline:
        # Explicit later material overrides: an empty include does not reliably
        # replace an include resolved inside the base archive.
        flat='void OrganicFlat(inout Material mat){mat.Base=getTexel(vTexCoord.st);mat.Normal=normalize(vWorldNormal.xyz);mat.Specular=vec3(0);mat.SpecularLevel=0;}\n'
        (fixture/'organic-flat.fp').write_text(flat+'void SetupMaterial(inout Material mat){OrganicFlat(mat);}\n')
        surface=(ROOT/'tutnt/shaders/environment/surface.glsl').read_text()
        (fixture/'organic-flat-environment.fp').write_text(flat+surface.replace('ENV_ORIGINAL_BODY','OrganicFlat(mat);'))
        defs=[]
        for name in list(manifest['variants'])+list(manifest['environment_bindings']):
            env=name in manifest['environment_bindings']
            shader='organic-flat-environment.fp' if env else 'organic-flat.fp'
            body=f'Material "{name}" {{ Shader "{shader}" Normal "materials/environment/normal.png" Specular "materials/organic/black.png"'
            if env:body+=f' Texture envMeta "materials/environment/{name}.png" Texture envState "UENVSTATE"'
            defs.append(body+' }')
        (fixture/'GLDEFS').write_text('\n'.join(defs)+'\n')
    maps=a.maps or sorted(p.stem.upper() for p in (ROOT/'tutnt/maps').glob('*.wad'))
    results=[]
    for mp in maps:
        label=f'{a.tag}-{"base" if a.baseline else "relief"}-r{a.renderer}-{mp}' + ('' if a.capture else '-smoke') + ('-live' if a.live_shaders else '')
        cfg='wait '+('350;' if a.capture else '70;')
        selected=[(i,v) for i,v in enumerate(views) if v['map']==mp] if a.capture else []
        for i,v in selected:
            image=logs/f'{label}-{v.get("label",v["family"])}.png'
            cfg+=f'netevent organicview {i};wait 8;screenshot "{image.as_posix()}";wait 3;'
        if mp=='TNT02' and not a.baseline:
            cfg+='save organic-material-regression;wait 5;load organic-material-regression;wait 15;'
        cfg+='echo UTNT_TEST_END;wait 3;quit\n'
        settings=[('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_lowerinbackground',False),
                  ('use_mouse',False),('use_joystick',False),('r_drawplayersprites',False),('crosshair',0),
                  ('con_notifytime',0),('gl_texture_filter',0),('screenblocks',12)]
        result=run_case(a.engine,a.iwad,root=central,mod=a.mod,addon=fixture,mapname=mp,renderer=a.renderer,
                        label=label,timeout=55,commands=cfg,settings=settings,quiet=True)
        output=Path(result['log']).read_text()
        if any(e in output for e in ('ERROR:','Failed to compile')):result['ok']=False
        checked=0
        for i,actual in re.findall(r'ORGANIC_SURFACE\|(\d+)\|(\S+)',output):
            v=views[int(i)]
            base=manifest['environment_bindings'].get(actual,actual)
            family=manifest['variants'].get(base,{}).get('family')
            if family!=v['family']:result['ok']=False;result['errors'].append(f'{v["family"]} resolved as {actual}')
            checked+=1
        if checked != sum('sector' in v for _,v in selected):
            result['ok']=False;result['errors'].append('Missing native surface reports')
        result['native_surfaces']=checked
        results.append(result);print(json.dumps(result),flush=True)
        if not result['ok']:
            print(output[-5000:]);break
    dest=central/'validation'/f'{a.tag}-materials';dest.mkdir(parents=True,exist_ok=True)
    name=f'{"capture" if a.capture else "maps"}-{"baseline" if a.baseline else "relief"}-r{a.renderer}'+('-live' if a.live_shaders else '')+'.json'
    (dest/name).write_text(json.dumps(results,indent=2))
    raise SystemExit(0 if all(r['ok'] for r in results) else 1)

if __name__=='__main__':main()
