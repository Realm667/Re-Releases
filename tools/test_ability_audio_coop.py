"""Verify local ability cue routing on two actual network peers with sound enabled."""
from pathlib import Path
import argparse,subprocess,sys,os,json,time,shutil
repo=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--engine',default=os.environ.get('UTNT_ENGINE'));p.add_argument('--iwad',default=os.environ.get('UTNT_IWAD'));p.add_argument('--mod',type=Path,default=repo/'tutnt');p.add_argument('--output',type=Path,default=repo/'logs/ability-audio-coop');a=p.parse_args()
if not a.engine or not a.iwad:p.error('Pass --engine/--iwad or set UTNT_ENGINE/UTNT_IWAD')
w=a.output.resolve();w.mkdir(parents=True,exist_ok=True);logs=w/'logs';logs.mkdir(exist_ok=True)
fixture=w/'fixture';shutil.copytree(repo/'tools/ability-tests',fixture,dirs_exist_ok=True)
shutil.copyfile(repo/'tools/ability-audio-tests/audio-tests.zc',fixture/'audio-tests.zc')
with (fixture/'ZSCRIPT').open('a') as f:f.write('\n#include "audio-tests.zc"\n')
with (fixture/'MAPINFO').open('a') as f:f.write('\ngameinfo { AddEventHandlers="AbilityAudioTest" }\n')
si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
children=[];results=[]
try:
    for i,cls in enumerate(['Scout','Commando']):
        label=f'ability-audio-coop-{i}';cfg=logs/(label+'.ini')
        cfg.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=658\nwin_h=527\nvid_maxfps=60\n')
        args=[a.engine,'-iwad',a.iwad,'-file',str(a.mod.resolve()),str(fixture),'-config',str(cfg),'-noautoload','-stdout','-noidle','+snd_musicvolume','0','+snd_sfxvolume','0.1','+playerclass',cls,'+vid_preferbackend','1','+use_mouse','false','+i_pauseinbackground','false','+map','ABTEST']
        args+=['-host','2','-port','15329'] if i==0 else ['-join','127.0.0.1:15329']
        f=(logs/(label+'.log')).open('wb');child=subprocess.Popen(args,cwd=w,stdout=f,stderr=subprocess.STDOUT,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
        children.append((child,f,label))
        if i==0:time.sleep(1)
    deadline=time.monotonic()+45
    while time.monotonic()<deadline:
        outputs=[(logs/(label+'.log')).read_text(errors='replace') for _,_,label in children]
        if all('ABILITY_AUDIO_COOP_COMPLETE' in s for s in outputs):break
        if any(child.poll() is not None for child,_,_ in children):break
        time.sleep(.2)
    for child,f,label in children:
        if child.poll() is None:child.terminate()
        child.wait(timeout=5);f.close()
        s=(logs/(label+'.log')).read_text(errors='replace')
        r={'label':label,'ok':'ABILITY_AUDIO_COOP_COMPLETE' in s and 'UTNT_ASSERT FAIL' not in s and 'VM execution aborted' not in s,'assertions':s.count('UTNT_ASSERT PASS')}
        results.append(r);print(json.dumps(r),flush=True)
        if not r['ok']:print(s[-6000:])
finally:
    for child,f,_ in children:
        if child.poll() is None:child.kill();child.wait()
        if not f.closed:f.close()
(logs/'results.json').write_text(json.dumps(results,indent=2))
sys.exit(0 if len(results)==2 and all(r['ok'] and r['assertions']>=2 for r in results) else 1)
