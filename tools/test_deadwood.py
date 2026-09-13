"""Validate actual deadwood substitutions, collision, dynamic spawn and save/load.
All artifacts are local under tutnt/.codex; the fixture never ships in UTNT.
"""
from pathlib import Path
import argparse,json,re,time
from check_engine import run_case,ROOT

MAPS = ['TNT01','TNT02','TNT03A1','TNT03A2','TNT03B','TNT04A','TNT04B','TNT04C','TNT04CN','TNTLE','ENDMAP01']

def run(engine,iwad,mod,mapname,renderer,work,restore=False,addon=None):
    label=f'deadwood-{mapname}-{renderer}'
    save_name=f'{label}-{time.time_ns()}'
    commands=['unbindall','god','notarget','con_notifytime 0','vid_setsize 1280 720','screenblocks 12',
        'UTNT_distanceblur 0','wait 40','netevent dwcheck']
    if mapname=='DWLAB':
        commands=['unbindall','god','notarget','con_notifytime 0','vid_setsize 1280 720','screenblocks 12','wait 220']
        for theme in range(3):
            commands += [f'netevent dwgallery {theme}','wait 8',f'screenshot logs/{label}-family-{theme}.png']
    else:
        commands += ['wait 180','netevent dwview','wait 10',f'screenshot logs/{label}.png']
        if restore:
            commands += ['netevent dwlegacyseed','wait 3',f'save {save_name}','wait 10',f'load {save_name}','wait 45',
                'netevent dwcheck 1','netevent dwlegacy','netevent dwspawn','wait 3','netevent dwcheck']
    if mapname=='TNT02':
        for mode,name in [(0,'fixed'),(1,'original'),(2,'dry'),(3,'charred')]:
            commands += [f'netevent dwreported {mode}','wait 8',
                f'screenshot logs/{label}-reported-{name}.png']
    commands += ['echo UTNT_TEST_END','wait 2','quit']
    result=run_case(engine,iwad,mod=mod,root=work,mapname=mapname,renderer=renderer,
        addon=addon or ROOT/'tools/fixtures/deadwood',label=label,commands='; '.join(commands)+'\n',
        timeout=90,settings=[('UTNT_fxquality',1),('UTNT_reducedfx','true'),('UTNT_distanceblur',0)])
    log=Path(result['log']).read_text(encoding='utf-8')
    checked_maps=re.findall(r'DEADWOOD_CHECK_MAP (\w+)',log)
    if mapname!='DWLAB' and (not checked_maps or any(n.upper()!=mapname.upper() for n in checked_maps)):
        result['ok']=False;result['errors'].append('wrong or missing checked map')
    if not result['ok']:print(log[-7000:])
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine',type=Path,default=Path('F:/DoomDev/uzdoom.exe'))
    p.add_argument('--iwad',type=Path,default=Path('F:/DoomDev/DOOM2.WAD'))
    p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
    p.add_argument('--maps',nargs='+',default=MAPS)
    p.add_argument('--renderer',default='1')
    p.add_argument('--restore',action='store_true')
    p.add_argument('--addon',type=Path)
    p.add_argument('--work',type=Path,default=ROOT/'tutnt/.codex/validation/deadwood')
    a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
    results=[]
    for mapname in a.maps:
        results.append(run(a.engine,a.iwad,a.mod,mapname,a.renderer,a.work,a.restore,a.addon))
        (a.work/f'results-{a.renderer}.json').write_text(json.dumps(results,indent=2)+'\n')
        if not results[-1]['ok']:raise SystemExit(1)
