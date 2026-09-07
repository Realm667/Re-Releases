"""TNTLE-style UTNT SBARINFO: real stats, resources, saved visibility and screenshots.
Runs isolated UZDoom configs on both renderers; addon assets never ship in the PK3.
Set UTNT_ENGINE and UTNT_IWAD. Optional --mod checks a freshly built package.
"""
import argparse,json,os,pathlib,shutil,subprocess,struct
from check_engine import ROOT,run_case

def compile_fixture():
    addon=ROOT/'tools/statusbar-tests'
    (addon/'acs').mkdir(exist_ok=True)
    (addon/'maps').mkdir(exist_ok=True)
    shutil.copyfile(ROOT/'tools/runtime-tests/maps/utnttest.wad',addon/'maps/utnttest.wad')
    acc=pathlib.Path(os.environ.get('UTNT_ACC',r'F:\DoomDev\Tools\UltimateDoombuilder\Compilers\ZDoom\acc.exe'))
    result=subprocess.run([str(acc),'-i',str(acc.parent),'-i',str(ROOT/'tutnt/source'),str(addon/'hud-regression.acs'),str(addon/'acs/UTHUDREG.o')],capture_output=True)
    if result.returncode: raise RuntimeError((result.stdout+result.stderr).decode(errors='replace'))
    return addon

def commands(label):
    c=['wait 400','event hudresources','netevent hudready','wait 15','netevent hudcheck 0']
    def snap(name): c.extend(['wait 12',f'screenshot logs/{label}-{name}.png'])
    snap('fullscreen')
    c.extend(['screenblocks 10']);snap('normal')
    c.extend(['togglemap']);snap('automap')
    c.extend(['togglemap','screenblocks 11','fullhud_trans 0']);snap('opaque')
    for pos in range(4):
        c.extend([f'fullhud_statspos {pos}',f'fullhud_stats {2 if pos%2==0 else 4}',f'fullhud_fullstats {int(pos<2)}'])
        snap(f'stats-{pos}')
    c.extend(['fullhud_statspos 1','fullhud_stats 0']);snap('stats-off')
    c.extend(['fullhud_stats 2','fullhud_fullstats 1','fullhud_trans 1','netevent hudcutscene 1','wait 12','netevent hudcheck 1'])
    snap('cutscene')
    c.extend([f'save {label}','wait 5','netevent hudcutscene 0','wait 12',f'load {label}','wait 20','netevent hudcheck 1'])
    snap('load-cutscene')
    c.extend(['netevent hudcutscene 0','wait 12','netevent hudcheck 0','netevent hudfreeze 1','wait 12','netevent hudcheck 1'])
    snap('frozen')
    c.extend(['netevent hudfreeze 0','netevent hudcamera 1','wait 12','netevent hudcheck 1']);snap('camera')
    c.extend(['netevent hudcamera 0','wait 12','netevent hudcheck 0','fullhud_mugswitch 0','netevent huditems']);snap('inventory-no-face')
    c.extend(['netevent hudcutscene 1','wait 12','netevent hudcheck 1']);snap('inventory-hidden')
    c.extend(['netevent hudcutscene 0','netevent hudclearitems','fullhud_mugswitch 1','give Clip 50','give UTNTHUDDualWeapon','use UTNTHUDDualWeapon','wait 40','netevent huddualcheck']);snap('dual-ammo')
    c.extend(['vid_setsize 1920 1080']);snap('1080p')
    c.extend(['vid_setsize 1024 768']);snap('4by3')
    c.extend(['vid_setsize 2560 1080']);snap('ultrawide')
    c.extend(['language deu','openmenu UTNTHUDOptions']);snap('menu-de')
    c.extend(['closemenu','map TNT03A1','wait 60','netevent hudcheck 0','wait 12','echo UTNT_TEST_END','wait 5','quit'])
    return '; '.join(c)+'\n'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--renderer',choices=['0','1','both'],default='both')
    p.add_argument('--mod',type=pathlib.Path)
    p.add_argument('--label',default='statusbar')
    a=p.parse_args();addon=compile_fixture();results=[]
    for renderer in ['0','1'] if a.renderer=='both' else [a.renderer]:
        label=f'{a.label}-{renderer}'
        result=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],mod=a.mod,
            mapname='UTNTTEST',addon=addon,renderer=renderer,label=label,timeout=60,regression=True,
            commands=commands(label),settings=[('screenblocks',11),('fullhud_stats',2),('con_notifytime',0),
                ('i_pauseinbackground',False),('vid_activeinbackground',True)])
        log=pathlib.Path(result['log']).read_text(encoding='utf-8')
        for error in ['Unknown command','Unknown font','is not a type of inventory item']:
            if error in log: result['errors'].append(error)
        if 'UTNT_HUD_STATS_COMPLETE' not in log:result['errors'].append('missing live statistics tests')
        for name,size in [('1080p',(1920,1080)),('4by3',(1024,768)),('ultrawide',(2560,1080))]:
            shot=ROOT/'logs'/f'{label}-{name}.png'
            actual=struct.unpack('>II',shot.read_bytes()[16:24]) if shot.exists() else None
            if actual!=size:result['errors'].append(f'{name}: expected {size}, got {actual}')
        result['ok']=result['ok'] and not result['errors'];results.append(result)
    (ROOT/'logs'/f'{a.label}-results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    raise SystemExit(0 if all(r['ok'] for r in results) else 1)

if __name__=='__main__':main()
