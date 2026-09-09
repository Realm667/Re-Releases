"""Two real local peers: network controls, Cloak, damage and respawn persistence."""
from pathlib import Path
import subprocess,time,json,os,argparse,shutil
repo=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('--engine',default=os.environ.get('UTNT_ENGINE'));p.add_argument('--iwad',default=os.environ.get('UTNT_IWAD'));p.add_argument('--mod',type=Path,default=repo/'tutnt');p.add_argument('--output',type=Path,default=repo/'logs/class-abilities');a=p.parse_args()
if not a.engine or not a.iwad:p.error('Set UTNT_ENGINE and UTNT_IWAD, or pass --engine and --iwad')
w=a.output.resolve();w.mkdir(parents=True,exist_ok=True)
shutil.copytree(repo/'tools/ability-tests',w/'tests',dirs_exist_ok=True)
addon=w/'coop-addon';addon.mkdir(exist_ok=True)
(addon/'ZSCRIPT').write_bytes((w/'tests/coop.zc').read_bytes())
(addon/'MAPINFO').write_text('gameinfo { AddEventHandlers="AbilityCoopTest" }\n')
logs=w/'logs';logs.mkdir(exist_ok=True);children=[];results=[]
si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
try:
    for i,cls in enumerate(['Scout','Commando']):
        label=f'abilities-coop-{i}';config=logs/(label+'.ini')
        config.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=658\nwin_h=527\nvid_maxfps=60\n')
        cfg=logs/(label+'.cfg')
        cfg.write_text('wait 60; utnt_defense; wait 70; utnt_offense; wait 210; utnt_offense; wait 55; +use; wait 4; -use\n')
        args=[a.engine,'-iwad',a.iwad,'-file',str(a.mod.resolve()),str(w/'tests'),str(addon),'-config',str(config),'-noautoload','-nosound','-stdout','-noidle','-rngseed','667','+playerclass',cls,'+vid_fullscreen','false','+vid_preferbackend','1','+use_mouse','false','+i_pauseinbackground','false','+map','ABTEST','+exec',str(cfg)]
        args+=['-host','2','-port','15319'] if i==0 else ['-join','127.0.0.1:15319']
        f=(logs/(label+'.log')).open('wb')
        child=subprocess.Popen(args,cwd=w,stdout=f,stderr=subprocess.STDOUT,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
        children.append((child,f,label))
        if i==0:time.sleep(1)
    deadline=time.monotonic()+45
    while time.monotonic()<deadline:
        outputs=[(logs/(label+'.log')).read_text(errors='replace') for _,_,label in children]
        if all('ABILITY_COOP_COMPLETE' in s for s in outputs):break
        if any(child.poll() is not None for child,_,_ in children):break
        time.sleep(.2)
    for child,f,label in children:
        if child.poll() is None:child.terminate()
        child.wait(timeout=5);f.close()
        output=(logs/(label+'.log')).read_text(errors='replace')
        result={'label':label,'ok':'ABILITY_COOP_COMPLETE' in output and 'UTNT_ASSERT FAIL' not in output and 'VM execution aborted' not in output,'assertions':output.count('UTNT_ASSERT PASS')}
        results.append(result);print(json.dumps(result),flush=True)
        if not result['ok']:print(output[-4500:])
finally:
    for child,f,_ in children:
        if child.poll() is None:child.kill();child.wait()
        if not f.closed:f.close()
(logs/'abilities-coop-results.json').write_text(json.dumps(results,indent=2))
raise SystemExit(0 if len(results)==2 and all(r['ok'] for r in results) else 1)
