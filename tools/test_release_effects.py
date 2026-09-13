"""Exercise imported enemy deaths and local movement tilt in UZDoom.

Outputs are kept under tutnt/.codex. --overlay supports a small development addon.
"""
from pathlib import Path
import argparse,json,zipfile
from build_utnt import write_wad
from check_engine import run_case

ROOT=Path(__file__).resolve().parents[1]


def fixture(output,overlay=None):
    payload={}
    if overlay:
        with zipfile.ZipFile(overlay) as z:payload={n:z.read(n) for n in z.namelist()}
    source=(ROOT/'tools/fixtures/release-effects/ZSCRIPT').read_text(encoding='utf-8')
    if 'ZSCRIPT' in payload:source=payload['ZSCRIPT'].decode()+'\n'+source.split('\n',1)[1]
    payload['ZSCRIPT']=source.encode()
    payload['MAPINFO']=payload.get('MAPINFO',b'')+b'\n'+(ROOT/'tools/fixtures/release-effects/MAPINFO').read_bytes()
    text=['namespace="ZDoom";']
    for x,y in [(-1100,-600),(-1100,600),(1100,600),(1100,-600)]:
        text.append(f'vertex {{x={x};y={y};}}')
    text.append('sector {heightfloor=0;heightceiling=192;texturefloor="FLOOR0_1";textureceiling="CEIL5_2";lightlevel=160;}')
    for i in range(4):
        text.append('sidedef {sector=0;texturemiddle="STARTAN3";}')
        text.append(f'linedef {{v1={i};v2={(i+1)%4};sidefront={i};blocking=true;}}')
    text.append('thing {x=0;y=-430;angle=90;type=1;skill1=true;skill2=true;skill3=true;skill4=true;skill5=true;single=true;coop=true;}')
    payload['maps/FXTEST.wad']=write_wad(b'PWAD',[(b'MAP01',b''),(b'TEXTMAP','\n'.join(text).encode()),(b'ENDMAP',b'')])
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in payload.items():z.writestr(name,data)
    return output


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine',type=Path,default=Path('F:/DoomDev/uzdoom.exe'))
    p.add_argument('--iwad',type=Path,default=Path('F:/DoomDev/DOOM2.WAD'))
    p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
    p.add_argument('--overlay',type=Path)
    p.add_argument('--renderer',choices=['0','1'],default='1')
    a=p.parse_args();out=ROOT/'tutnt/.codex/validation/release-effects';out.mkdir(parents=True,exist_ok=True)
    addon=fixture(ROOT/'tutnt/.codex/builds/release-effects-test.pk3',a.overlay)
    compiled=run_case(a.engine,a.iwad,root=out,mod=a.mod,addon=addon,label='release-effects-fixture-compile')
    if not compiled['ok']:
        print(Path(compiled['log']).read_text(errors='replace')[-7000:]);raise SystemExit(1)
    commands=['god','wait 180','netevent deathcheck','wait 4','save release-effects','wait 5',
              'load release-effects','wait 8','netevent deathcheck','wait 4','netevent revivetest',
              'wait 100','netevent afterraise','wait 5','event tiltmath','netevent tiltmove 1',
              'UTNT_viewtilt false','wait 30','event tiltcheck 0','screenshot logs/tilt-off.png',
              'UTNT_viewtilt true','wait 35','event tiltcheck 1','screenshot logs/tilt-right.png',
              'netevent tiltmove -1','wait 40','event tiltcheck -1','screenshot logs/tilt-left.png',
              'UTNT_reducedfx true','wait 8','event tiltcheck 0','UTNT_reducedfx false',
              'netevent tiltmove 0','wait 35','event tiltcheck 0','UTNT_viewtiltstrength 0',
              'netevent tiltmove 1','wait 35','event tiltcheck 0','UTNT_viewtiltstrength 65',
              'event tiltmenu','wait 5','screenshot logs/tilt-menu.png','event tiltclose','wait 5',
              'event effectsdone','echo UTNT_TEST_END','wait 3','quit']
    result=run_case(a.engine,a.iwad,root=out,mod=a.mod,addon=addon,mapname='FXTEST',
                    renderer=a.renderer,label='release-effects-r'+a.renderer,timeout=100,
                    commands=';'.join(commands),settings=[('vid_activeinbackground',True),
                    ('i_pauseinbackground',False),('use_mouse',False),('use_joystick',False),
                    ('con_notifytime',0),('language','de'),('vid_maxfps',60),('cl_capfps',True)],regression=True)
    log=Path(result['log']).read_text(errors='replace')
    unexpected=[line for line in log.splitlines() if any(x in line for x in ('Unknown command','invalid state','Unable to load','Script error'))]
    result['unexpected']=unexpected;result['ok'] &= not unexpected
    (out/('result-r'+a.renderer+'.json')).write_text(json.dumps(result,indent=2))
    if not result['ok']:print(log[-9000:])
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['ok'] else 1)


if __name__=='__main__':main()
