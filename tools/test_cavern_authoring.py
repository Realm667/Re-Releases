"""Prove that manual cavern edits survive startup, save/load and hub return."""
from pathlib import Path
import argparse,json,shutil
from author_cavern import lumps,wad,edit_text
from test_cavern_skyrooms import blocks
from check_engine import run_case
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
    p.add_argument('--engine',default='F:/DoomDev/uzdoom.exe');p.add_argument('--iwad',default='F:/DoomDev/DOOM2.WAD')
    a=p.parse_args();work=ROOT/'tutnt/.codex/work/cavern-tnt03a2';addon=work/'authoring-regression'
    (addon/'maps').mkdir(parents=True,exist_ok=True)
    for name in ('ZSCRIPT','MAPINFO'):shutil.copyfile(ROOT/'tools/fixtures/cavern-authoring'/name,addon/name)
    magic,entries=lumps((ROOT/'tutnt/maps/tnt03a2.wad').read_bytes())
    text=next(d.decode() for n,d in entries if n.rstrip(b'\0')==b'TEXTMAP');things=blocks(text,'thing')
    model=next(i for i,t in enumerate(things) if t.get('type')=='25000')
    camera=next(i for i,t in enumerate(things) if t.get('type')=='25110' and t.get('id')=='65200')
    changes={'thing':{model:{'x':5304,'height':2144,'angle':37},camera:{'x':-12160}},'sector':{2270:{'lightlevel':81,'fogdensity':38},2269:{'lightlevel':171,'fogdensity':52}},'linedef':{4783:{'alpha':'.35'}}}
    data=wad(magic,[(n,edit_text(d.decode(),changes).encode() if n.rstrip(b'\0')==b'TEXTMAP' else d) for n,d in entries])
    (addon/'maps/tnt03a2.wad').write_bytes(data)
    result=run_case(a.engine,a.iwad,root=work,mod=a.mod,addon=addon,mapname='TNT03A2',label='authoring-manual-production',timeout=70,
        commands='wait 100; netevent authorcheck; wait 10; save authoring-manual-production; wait 15; load authoring-manual-production; wait 100; netevent authorcheck; wait 10; changemap TNT03A1; wait 80; changemap TNT03A2; wait 100; netevent authorcheck; wait 10; echo UTNT_TEST_END; quit',
        settings=[('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_maxfps',60),('use_mouse',False),('use_joystick',False)])
    result['ok']=result['ok'] and result['assertions']==15
    out=ROOT/'tutnt/.codex/validation/cavern-tnt03a2';out.mkdir(parents=True,exist_ok=True)
    (out/'authoring-manual-production.json').write_text(json.dumps(result,indent=2)+'\n')
    return 0 if result['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
