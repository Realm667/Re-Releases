"""Production weather-cycle checks. --root isolates logs, saves and fixtures."""
from pathlib import Path
import argparse,os,sys,json,re
from check_engine import run_case,ROOT
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--root',type=Path,default=ROOT)
p.add_argument('--mod',type=Path)
p.add_argument('--case',choices=['cycle','geometry','lifecycle','quality','motion','hub','profile','colors','coop'],default='cycle')
p.add_argument('--map',default='TNT03A1',dest='mapname')
p.add_argument('--renderer',default='1',choices=['0','1'])
a=p.parse_args()
addon=ROOT/'tools/weather-cycle-tests'
fixture=ROOT/'tools/weather-tests'
label=f'weather-cycle-{a.case}-{a.mapname}-{a.renderer}'
camera='netevent cyclecamera; wait 60; ' if a.mapname=='TNT02' else ''
cmd='wait 140; '+camera
if a.case=='cycle':
    cmd+='netevent cyclemath; netevent cyclephase 4; wait 60; netevent cyclecheck 0 1; event weathercheck 1; '
    cmd+='netevent cyclephase 105; wait 60; netevent cyclecheck 50 52; event weathercheck 1; '
    cmd+='netevent cyclephase 190; wait 140; netevent cyclecheck 99 100; event weathercheck 1; '
    cmd+=f'screenshot logs/{label}-storm.png; '
    cmd+='freeze; wait 5; netevent cyclemark; wait 35; netevent cyclefrozen; freeze; wait 5; '
    cmd+='netevent cyclemark; wait 2; save weather-cycle-save; wait 40; netevent cyclephase 10 9; wait 5; load weather-cycle-save; wait 5; netevent cyclerestore; wait 100; netevent cyclecheck 99 100; event weathercheck 1; '
    cmd+='UTNT_fxquality 1; wait 100; netevent cyclecheck 99 100; event weathercheck 1; '
    cmd+='UTNT_fxquality 2; wait 100; netevent cyclecheck 99 100; event weathercheck 1; '
    cmd+='weatherfx false; wait 30; netevent cyclemark; wait 35; netevent cycleadvances; event weathercheck 0; netevent weatherfog 0; '
    cmd+='weatherfx true; UTNT_fxquality 3; netevent cyclephase 275; wait 100; netevent cyclecheck 5 20; event weathercheck 1; '
    cmd+='netevent cyclephase 298; wait 100; netevent cyclecheck 0 1; event weathercheck 1; '
elif a.case in ['geometry','lifecycle','quality','motion','hub']:
    cmd+='netevent cyclephase 190; wait 140; '
    if a.case=='geometry':cmd+='netevent cycleedges; wait 3; netevent cycleedgecheck; '
    cmd+=(fixture/(a.case+'.cfg')).read_text().replace('echo UTNT_TEST_END;','')
    # Fixture quits itself after its final checks.
    cmd=cmd.replace('quit','netevent cyclecheck 0 100; echo UTNT_TEST_END; quit')
elif a.case=='colors':cmd+='event snowcolors; wait 3; screenshot logs/'+label+'.png; '
elif a.case=='profile':
    cmd+='netevent cyclephase 190; wait 170; netevent cyclecheck 99 100; event weathercheck 1; '
if 'echo UTNT_TEST_END' not in cmd:cmd+='echo UTNT_TEST_END; wait 5; quit\n'
cmd=cmd.replace('weather-cycle-save',label+'-save')
# run_case accepts one directory. A tiny overlay includes the shared fixture.
combined=a.root/'logs'/('addon-'+label);combined.mkdir(parents=True,exist_ok=True)
import shutil
shutil.copytree(fixture,combined,dirs_exist_ok=True)
(combined/'fixture.zc').write_text((fixture/'ZSCRIPT').read_text(encoding='utf-8').replace('version "5.0.0"',''),encoding='utf-8')
(combined/'ZSCRIPT').write_text((addon/'ZSCRIPT').read_text(encoding='utf-8')+'\n#include "fixture.zc"\n',encoding='utf-8')
(combined/'MAPINFO').write_text('gameinfo { AddEventHandlers="UTNTWeatherCycleTests", "UTNTWeatherTests" }\n')
r=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],root=a.root,mod=a.mod,addon=combined,label=label+'-compile',quiet=True)
if not r['ok']:
    print(Path(r['log']).read_text(encoding='utf-8')[-6000:]);raise SystemExit(1)
if a.case=='coop':
    import test_weather
    test_weather.ROOT=a.root
    results=test_weather.coop(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],a.mod,combined)
    climates=[re.findall(r'CLIMATE_SHARED.*',(a.root/'logs'/f'weather-final-coop-{i}.log').read_text(encoding='utf-8')) for i in range(2)]
    matched=bool(climates[0]) and climates[0]==climates[1]
    for result in results:result['climate_matches']=matched;result['ok'] &= matched
    (a.root/'logs/weather-cycle-coop-results.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(results));raise SystemExit(0 if all(result['ok'] for result in results) else 1)
r=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],root=a.root,mod=a.mod,mapname=a.mapname,addon=combined,renderer=a.renderer,label=label,commands=cmd,timeout=120,regression=a.case!='colors',settings=[('weatherfx',True),('UTNT_fxquality',3),('UTNT_lod',2048),('UTNT_atmosphere',False),('con_notifytime',0),('vid_activeinbackground',True),('vid_lowerinbackground',False),('i_pauseinbackground',False)])
if a.case=='colors' and r['ok']:
    from PIL import Image
    im=Image.open(a.root/'logs'/(label+'.png')).convert('RGB')
    colors=[im.crop((100+n*100,100,116+n*100,116)).getextrema() for n in range(3)]
    r['neutral_cc_swatches']=all(c[0]==c[1]==c[2] and abs(c[0][1]-188)<=1 for c in colors)
    r['swatches']=colors;r['ok'] &= r['neutral_cc_swatches']
out=a.root/'logs'/(label+'-result.json');out.write_text(json.dumps(r,indent=2))
if not r['ok']:print(Path(r['log']).read_text(encoding='utf-8')[-11000:])
raise SystemExit(0 if r['ok'] else 1)
