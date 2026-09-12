"""Check legacy emitter dimensions and lifecycle in UZDoom (OpenGL/Vulkan)."""
import argparse, json, os, zipfile
from pathlib import Path
from check_engine import ROOT, run_case

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE',ROOT/'engine/uzdoom.exe'))
    p.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD','F:/DoomDev/DOOM2.WAD'))
    p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
    p.add_argument('--renderer',choices=['0','1','both'],default='both')
    p.add_argument('--overlay-source',action='store_true',help='Overlay only the current UTNT_Visuals.zc for isolated pre-build checks')
    a=p.parse_args(); results=[]
    addon=ROOT/'tutnt/.codex/builds/particle-size-tests.pk3'
    with zipfile.ZipFile(addon,'w') as z:
        z.write(ROOT/'tools/particle-size-tests/ZSCRIPT','ZSCRIPT')
        z.writestr('MAPINFO','gameinfo { AddEventHandlers="UTNTParticleSizeTest" }\nmap UTNTIFX "Particle size validation" { levelnum=98 }\n')
        z.write(ROOT/'tools/industrial-revision-tests/maps/utntifx.wad','maps/utntifx.wad')
        if a.overlay_source:z.write(ROOT/'tutnt/zscript/UTNT_Visuals.zc','zscript/UTNT_Visuals.zc')
    compiled=run_case(a.engine,a.iwad,mod=a.mod,addon=addon,label='particle-size-compile')
    if not compiled['ok']:raise SystemExit(1)
    for renderer in ['0','1'] if a.renderer=='both' else [a.renderer]:
        label='particle-size-'+renderer
        commands=['unbindall','con_notifytime 0','wait 180','netevent particlesize 0','wait 100','event particlesizecheck 1',
            f'screenshot logs/{label}-emitters.png','netevent particlesize 2','wait 60','event particlesizecheck 2',
            'netevent particlesize 3','wait 100','event particlesizecheck 1','UTNT_fxquality 0','wait 70','event particlesizecheck 0',
            'UTNT_fxquality 1','wait 100','event particlesizecheck 1','UTNT_fxquality 2','wait 100','event particlesizecheck 1',
            'UTNT_fxquality 3','UTNT_reducedfx true','wait 100','event particlesizecheck 1','UTNT_reducedfx false',
            'UTNT_lod 0','wait 70','event particlesizecheck 0','UTNT_lod 2048','wait 100','event particlesizecheck 1',
            'netevent particlesize 1','wait 70','event particlesizecheck 0',
            'vid_setsize 1920 1080','wait 15','netevent particlesize 4','wait 5',f'screenshot logs/{label}-scale-pairs.png',
            'echo UTNT_TEST_END','quit']
        results.append(run_case(a.engine,a.iwad,mod=a.mod,addon=addon,mapname='UTNTIFX',renderer=renderer,
            label=label,timeout=100,commands='; '.join(commands)+'\n',
            settings=[('UTNT_fxquality',3),('UTNT_reducedfx',False),('UTNT_lod',2048),('use_mouse',False),
                      ('i_pauseinbackground',False),('screenblocks',12),('r_drawplayersprites',False),('crosshair',0),('gl_bloom',False)]))
    out=ROOT/'tutnt/.codex/validation/particle-size-results.json';out.write_text(json.dumps(results,indent=2)+'\n')
    raise SystemExit(not all(r['ok'] for r in results))
if __name__=='__main__':main()
