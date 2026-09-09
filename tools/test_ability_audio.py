"""Ability sound delivery and decoding with the actual audio backend enabled."""
from pathlib import Path
import argparse,json,os,shutil,subprocess,sys
repo=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(repo/'tools'))
from check_engine import run_case
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine',default=os.environ.get('UTNT_ENGINE'));p.add_argument('--iwad',default=os.environ.get('UTNT_IWAD'))
p.add_argument('--mod',default=str(repo/'tutnt'));p.add_argument('--output',type=Path,default=repo/'logs/ability-audio')
p.add_argument('--class',dest='cls',default='Marine');p.add_argument('--fast',action='store_true',help='Shorten both active timers; still expire through the production Tick path');a=p.parse_args()
if not a.engine or not a.iwad:p.error('Pass --engine/--iwad or set UTNT_ENGINE/UTNT_IWAD')
w=a.output.resolve();w.mkdir(parents=True,exist_ok=True)
fixture=w/('fixture-'+a.cls.lower());shutil.copytree(repo/'tools/ability-tests',fixture,dirs_exist_ok=True)
shutil.copyfile(repo/'tools/ability-audio-tests/audio-tests.zc',fixture/'audio-tests.zc')
with (fixture/'ZSCRIPT').open('a') as f:f.write('\n#include "audio-tests.zc"\n')
with (fixture/'MAPINFO').open('a') as f:f.write('\ngameinfo { AddEventHandlers="AbilityAudioTest" }\n')
commands=['wait 100','event soundreset','event soundassets','netevent soundbegin 1','wait 8','event soundcheck 1 0 0',
    'wait 525','event soundcheck 1 1 0','netevent soundexpire','netevent soundfinish','wait 4','event soundcheck 1 1 0',
    'netevent soundbegin 2','wait 8','event soundcheck 2 1 0','wait 525','event soundcheck 2 2 0',
    'netevent soundbegin 1','wait 4','netevent soundfinish','wait 4','event soundcheck 3 2 0',
    'netevent soundready','wait 5','event soundcheck 3 2 1',
    'netevent soundbegin 2','wait 50','save audio-save','wait 4','load audio-save','wait 8','event soundreset','wait 8','event soundcheck 0 0 0',
    'netevent soundexpire','wait 8','event soundcheck 0 1 0',
    'netevent soundbegin 1','wait 50','changemap ABTEST2','wait 25','event soundreset','wait 8','event soundcheck 0 0 0',
    'netevent soundexpire','wait 8','event soundcheck 0 1 0',
    'netevent soundbegin 1','wait 8','netevent sounddie','wait 8','event soundcheck 1 1 0','echo UTNT_TEST_END','quit']
if a.fast:
    commands=[part for c in commands for part in (['netevent soundexpire','wait 8'] if c=='wait 525' else [c])]
# check_engine normally mutes audio for render tests. Enable it here, retaining
# its hidden launch, isolated settings and completion/error checks.
native_run=subprocess.run
def audio_run(args,*pargs,**kwargs):
    if args and str(args[0])==str(Path(a.engine).resolve()):args=[v for v in args if v!='-nosound']
    return native_run(args,*pargs,**kwargs)
subprocess.run=audio_run
try:
    result=run_case(a.engine,a.iwad,root=w,mod=a.mod,addon=fixture,mapname='ABTEST',playerclass=a.cls,label=a.cls.lower()+'-ability-audio',
        commands='; '.join(commands)+'\n',timeout=95,settings=[('snd_musicvolume',0),('snd_sfxvolume',0.25),('use_mouse',False),('i_pauseinbackground',False),('con_notifytime',0)])
finally:subprocess.run=native_run
output=Path(result['log']).read_text()
result['ok']=result['ok'] and result['assertions']>=sum(c.startswith('event soundcheck') for c in commands)+1 and 'Sound init failed' not in output
(w/'logs'/(a.cls.lower()+'-ability-audio.json')).write_text(json.dumps(result,indent=2))
if not result['ok']:print(output[-8000:])
sys.exit(0 if result['ok'] else 1)
