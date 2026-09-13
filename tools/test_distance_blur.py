"""Engine and image regression for global Distance Blur; artifacts stay in .codex."""
import argparse
import json
from pathlib import Path
import shutil
import struct
from PIL import Image, ImageChops, ImageStat
from check_engine import run_case

ROOT=Path(__file__).resolve().parents[1]

def fixture():
    addon=ROOT/'tutnt/.codex/work/distance-blur/fixture'
    addon.mkdir(parents=True,exist_ok=True)
    for name in ('MAPINFO','ZSCRIPT'):
        shutil.copyfile(ROOT/'tools/fixtures/distance-blur'/name,addon/name)
    text='namespace="ZDoom";\n'
    for x,y in ((0,-2048),(0,2048),(4096,2048),(4096,-2048)):
        text+=f'vertex {{ x={x}.0; y={y}.0; }}\n'
    for i in range(4):
        text+=f'sidedef {{ sector=0; texturemiddle="STARTAN3"; }}\n'
        text+=f'linedef {{ v1={i}; v2={(i+1)%4}; sidefront={i}; blocking=true; }}\n'
    text+='sector { heightfloor=0; heightceiling=1536; texturefloor="FLOOR0_1"; textureceiling="CEIL1_1"; lightlevel=200; }\n'
    for x,y,kind in ((128,0,1),(512,-128,3004),(2048,256,3004),(3584,-384,3004)):
        text+=f'thing {{ x={x}.0; y={y}.0; angle=0; type={kind}; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; }}\n'
    entries=[(b'BLURTEST',b''),(b'TEXTMAP',text.encode()),(b'ENDMAP',b'')]
    body=bytearray(); directory=bytearray()
    for name,data in entries:
        directory+=struct.pack('<II8s',12+len(body),len(data),name);body+=data
    maps=addon/'maps';maps.mkdir(exist_ok=True)
    (maps/'BLURTEST.wad').write_bytes(struct.pack('<4sII',b'PWAD',3,12+len(body))+body+directory)
    return addon

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine',default='F:/DoomDev/Projects/wolfendoom.dev/#standalone/uzdoom.exe')
    p.add_argument('--iwad',default='F:/DoomDev/DOOM2.WAD')
    p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
    p.add_argument('--renderers',nargs='+',default=['0','1'])
    a=p.parse_args();addon=fixture();out=ROOT/'tutnt/.codex/validation/distance-blur';out.mkdir(parents=True,exist_ok=True)
    results=[]
    for renderer in a.renderers:
        label='blur-'+renderer
        cmds=['wait 70','freeze','event blurmenu','wait 5','event blurcheck 1 50 640',
              'UTNT_distanceblur false','wait 5',f'screenshot logs/{label}-off.png','event blurcheck 0 50 640',
              'UTNT_distanceblur true','wait 5',f'screenshot logs/{label}-default.png',
              'UTNT_distanceblurstrength 0','wait 5',f'screenshot logs/{label}-zero.png','event blurcheck 0 0 640',
              'UTNT_distanceblurstrength 100','UTNT_distanceblurstart 128','wait 5',f'screenshot logs/{label}-max.png','event blurcheck 1 100 128',
              'UTNT_distanceblurstart 2569','wait 5',f'screenshot logs/{label}-far.png','event blurcheck 1 100 2569',
              'UTNT_distanceblurstrength 200','UTNT_distanceblurstart 9999','wait 5','event blurcheck 1 100 2569',
              'UTNT_distanceblurstrength -50','UTNT_distanceblurstart 0','wait 5','event blurcheck 0 0 128',
              'UTNT_distanceblurstrength 50','UTNT_distanceblurstart 640','UTNT_reducedfx true','wait 5','event blurcheck 0 50 640',
              'UTNT_reducedfx false','wait 5','event blurcheck 1 50 640','save blur-state','wait 5','load blur-state','wait 15','event blurcheck 1 50 640']
        for lang in ('en','de','es','fr'):
            cmds+=['language '+lang,'openmenu UTNTDisplayOptions','wait 5',f'screenshot logs/{label}-menu-{lang}.png','event blurmenu']
        cmds+=['echo UTNT_TEST_END','quit']
        result=run_case(a.engine,a.iwad,root=out,mod=a.mod,addon=addon,mapname='BLURTEST',renderer=renderer,label=label,
            timeout=70,commands='; '.join(cmds),regression=True,settings=[('con_notifytime',0),('vid_activeinbackground',True),
            ('i_pauseinbackground',False),('UTNT_reducedfx',False),('UTNT_underwateratmosphere',False),('motionblur',False),('crosshair',0)])
        if result['ok']:
            images={name:Image.open(out/f'logs/{label}-{name}.png').convert('RGB') for name in ('off','zero','default','max','far')}
            diffs={name:sum(ImageStat.Stat(ImageChops.difference(images['off'],im)).mean) for name,im in images.items() if name!='off'}
            result['image_differences']=diffs
            result['ok']=diffs['zero']==0 and diffs['max']>diffs['default']>0 and 0<diffs['far']<diffs['max']
            if not result['ok']:result['errors'].append('image regression: zero equals off; maximum > default; far start reduces blur')
        if not result['ok']:print(Path(result['log']).read_text(encoding='utf-8')[-5000:])
        print(json.dumps(result));results.append(result)
    (out/'results.json').write_text(json.dumps(results,indent=2))
    return int(any(not r['ok'] for r in results))

if __name__=='__main__':raise SystemExit(main())
