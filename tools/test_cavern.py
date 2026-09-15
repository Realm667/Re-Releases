"""Real-engine cavern views and save/load regression on both hardware backends."""
from pathlib import Path
import argparse,json,shutil
from check_engine import run_case
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine',default='F:/DoomDev/uzdoom.exe');p.add_argument('--iwad',default='F:/DoomDev/DOOM2.WAD')
    p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
    p.add_argument('--renderer',default='1',choices=['0','1']);p.add_argument('--label',default='cavern')
    p.add_argument('--live-overlay',action='store_true',help='Test current cavern resources over the last complete build')
    p.add_argument('--hub',action='store_true',help='Also exercise hub travel and effect quality zero')
    a=p.parse_args();work=ROOT/'tutnt/.codex/work/cavern-tnt03a2';work.mkdir(parents=True,exist_ok=True)
    label=a.label+'-'+a.renderer
    commands=['god','notarget','wait 100','netevent caveview 0','wait 100','netevent cavecheck']
    for v in range(8):commands += [f'netevent caveview {v}','wait 45',f'screenshot logs/{label}-{v}.png']
    commands += ['netevent caveview 8','wait 30','netevent cavefall','wait 50','netevent cavefallcheck',f'screenshot logs/{label}-fall.png','wait 100',f'screenshot logs/{label}-fall-drift.png','netevent caveview 0']
    commands += [f'save {label}','wait 15',f'load {label}','wait 100','netevent cavecheck','wait 10',f'screenshot logs/{label}-restored.png']
    if a.hub:
        commands += ['UTNT_fxquality 0','wait 350','netevent cavequiet','UTNT_fxquality 3','changemap TNT03A1','wait 80','changemap TNT03A2','wait 100','netevent caveview 0','wait 20','netevent cavecheck']
    commands += ['echo UTNT_TEST_END','wait 5','quit']
    addon=ROOT/'tools/fixtures/cavern'
    if a.live_overlay:
        addon=work/'iteration';addon.mkdir(exist_ok=True)
        old=addon/'ZSCRIPT'
        if old.is_file():old.unlink()
        for p in (ROOT/'tools/fixtures/cavern').iterdir():
            if p.is_file():shutil.copyfile(p,addon/('zscript.zc' if p.name=='ZSCRIPT' else p.name))
        files=['zscript/UTNT_Cavern.zc','zscript/cavern-generated.zc','modeldef/MODELDEF.cavern','gldefs/GLDEFS.cavern','shaders/cavern-haze.fp','zscript/UTNT_CavernAtmosphere.zc','sndinfo/sndinfo.cavern']
        for folder in ['cavern','models/cavern']:
            files += [p.relative_to(ROOT/'tutnt').as_posix() for p in (ROOT/'tutnt'/folder).rglob('*') if p.is_file()]
        for name in files:
            dest=addon/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'tutnt'/name,dest)
        shutil.copyfile(ROOT/'tutnt/textures/definitions/TEXTURES.cavern',addon/'TEXTURES.txt')
        (addon/'SNDINFO.txt').write_text('$include "sndinfo/sndinfo.cavern"\n')
    r=run_case(a.engine,a.iwad,root=work,mod=a.mod,mapname='TNT03A2',addon=addon,renderer=a.renderer,label=label,timeout=110,
        commands='; '.join(commands),settings=[('win_w',1440),('win_h',900),('vid_maxfps',60),('gl_texture_filter',0),('screenblocks',12),('crosshair',0),('con_notifytime',0),('r_drawplayersprites',False),('UTNT_subtitles',False),('fullhud_fullstats',False),('UTNT_fxquality',3),('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_lowerinbackground',False),('use_mouse',False),('use_joystick',False)])
    expected=33 if a.hub else 22
    if r['assertions']!=expected:r['ok']=False;r['errors'].append(f'Expected {expected} lifecycle assertions')
    out=ROOT/'tutnt/.codex/validation/cavern-tnt03a2';out.mkdir(parents=True,exist_ok=True);(out/(label+'.json')).write_text(json.dumps(r,indent=2))
    return 0 if r['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
