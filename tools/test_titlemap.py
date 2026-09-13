"""Run TITLEMAP presentation, menu-clock, aspect-ratio and reduced-effects regressions."""
import argparse,json,os,zipfile
from pathlib import Path
from PIL import Image,ImageChops
from check_engine import run_case
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
    parser.add_argument('--overlay',type=Path)
    parser.add_argument('--engine',default=os.environ.get('UTNT_ENGINE',str(ROOT/'engine/uzdoom.exe')))
    parser.add_argument('--iwad',default=os.environ.get('UTNT_IWAD','F:/DoomDev/DOOM2.WAD'))
    a=parser.parse_args();out=ROOT/'tutnt/.codex/validation/titlemap-cinematic';out.mkdir(parents=True,exist_ok=True)
    addon=ROOT/'tutnt/.codex/builds/titlemap-regression.pk3'
    with zipfile.ZipFile(addon,'w') as z:
        if a.overlay:
            with zipfile.ZipFile(a.overlay) as src:
                for name in src.namelist():
                    if name.upper() not in ('ZSCRIPT','MAPINFO'):z.writestr(name,src.read(name))
                entry=src.read('ZSCRIPT').decode()
        else:entry='version "4.10"\n'
        z.writestr('ZSCRIPT',entry+'\n#include "titleprobe.zc"\n')
        z.writestr('titleprobe.zc',(ROOT/'tools/fixtures/titlemap/ZSCRIPT').read_text(encoding='utf-8').split('\n',1)[1])
        z.write(ROOT/'tools/fixtures/titlemap/MAPINFO','MAPINFO')
    compile_result=run_case(a.engine,a.iwad,root=out,mod=a.mod,addon=addon,label="regression-compile")
    if not compile_result["ok"]:
        print(Path(compile_result["log"]).read_text(encoding="utf-8")[-4000:]);raise SystemExit(1)
    results=[]
    for label,lang,width,height,reduced in [('en','en',1280,720,False),('de','de',1024,768,False),('es-wide','es',1680,720,False),('fr','fr',1280,720,False),('reduced','en',1280,720,True)]:
        if label=='en':
            commands='wait 150; screenshot logs/motion-a.png; wait 25; screenshot logs/motion-b.png; openmenu MainMenu; wait 175; closemenu; wait 480; '
        else:commands='wait 830; '
        commands+=f'screenshot logs/{label}-final.png; wait 35; screenshot logs/{label}-idle.png; openmenu MainMenu; wait 15; screenshot logs/{label}-menu.png; closemenu; wait 10; screenshot logs/{label}-resume.png; '
        if label=='en':commands+='map TNT01; wait 100; screenshot logs/gameplay.png; map TITLEMAP; wait 20; screenshot logs/restart.png; '
        commands+='echo UTNT_TEST_END; wait 3; quit'
        result=run_case(a.engine,a.iwad,root=out,mod=a.mod,addon=addon,mapname='TITLEMAP',label='regression-'+label,timeout=65,regression=True,settings=[('language',lang),('win_w',width),('win_h',height),('UTNT_reducedfx',str(reduced).lower()),('vid_activeinbackground','true'),('i_pauseinbackground','false'),('con_notifytime',0)],commands=commands)
        if label=='en':
            log=Path(result['log']).read_text(encoding='utf-8')
            import re
            samples=[int(n) for n in re.findall(r'UTNT_TITLE_MENU_TICKS (\d+)',log)]
            result['menu_clock_advances']=bool(samples and max(samples)>100)
            result['ok'] &= result['menu_clock_advances']
        if result['ok']:
            first=Image.open(out/f'logs/{label}-final.png').convert('RGB')
            second=Image.open(out/f'logs/{label}-idle.png').convert('RGB')
            different=ImageChops.difference(first,second).getbbox() is not None
            result['idle_motion_correct']=different!=reduced
            result['ok'] &= result['idle_motion_correct']
            if label=='en':
                x=Image.open(out/'logs/motion-a.png').convert('RGB');y=Image.open(out/'logs/motion-b.png').convert('RGB')
                box=(int(x.width*.3),int(x.height*.1),int(x.width*.7),int(x.height*.9))
                result['scene_motion']=ImageChops.difference(x.crop(box),y.crop(box)).getbbox() is not None
                result['ok'] &= result['scene_motion']
        results.append(result)
        (out/'regression-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
        if not result['ok']:raise SystemExit(1)
    print('All TITLEMAP runtime and image regressions passed.')

if __name__=='__main__':main()
