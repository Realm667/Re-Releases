from pathlib import Path
import subprocess,time,json,os,argparse
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description='Two SteamSpawner peers with opposing local quality settings')
p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
p.add_argument('--root',type=Path,default=ROOT)
p.add_argument('--fixture',type=Path,default=ROOT/'tools/steam-tests')
a=p.parse_args();w=a.root.resolve();logs=w/'logs';logs.mkdir(exist_ok=True)
engine=Path(os.environ['UTNT_ENGINE'])
children=[];results=[]
si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
try:
    for i in range(2):
        label=f'steam-coop-{i}'
        config=logs/(label+'.ini');config.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=658\nwin_h=527\nvid_maxfps=60\ni_pauseinbackground=false\n')
        cmd=('wait 180;event steamcheck 3;wait 30;netevent steamoff;wait 65;event steamcheck 0;wait 30;netevent steamon;wait 80;event steamcheck 3;wait 60;' if i==0 else 'wait 180;event steamcheck 0;wait 95;event steamcheck 0;wait 110;event steamcheck 0;wait 60;')
        cfg=logs/(label+'.cfg');cfg.write_text(cmd+'echo UTNT_STEAM_COOP_COMPLETE\n')
        args=[str(engine),'-iwad',os.environ['UTNT_IWAD'],'-file',str(a.mod.resolve()),str(a.fixture.resolve()),'-config',str(config),'-noautoload','-nosound','-stdout','-noidle','+vid_fullscreen','false','+vid_preferbackend','1','+UTNT_fxquality','3' if i==0 else '0','+UTNT_lod','2000','+UTNT_reducedfx','false','+use_mouse','false','+use_joystick','false','+i_pauseinbackground','false','+map','UTNTSTM','+exec',str(cfg)]
        args+=['-host','2','-port','15487'] if i==0 else ['-join','127.0.0.1:15487']
        f=(logs/(label+'.log')).open('wb')
        child=subprocess.Popen(args,cwd=w,stdout=f,stderr=subprocess.STDOUT,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
        children.append((child,f,label))
        if i==0:time.sleep(1)
    deadline=time.monotonic()+50
    while time.monotonic()<deadline:
        outputs=[(logs/(label+'.log')).read_text(errors='replace') for child,f,label in children]
        if all('UTNT_STEAM_COOP_COMPLETE' in output for output in outputs):break
        if any(child.poll() is not None for child,f,label in children):break
        time.sleep(.2)
    for child,f,label in children:
        if child.poll() is None:child.terminate()
        child.wait(timeout=5);f.close()
        out=(logs/(label+'.log')).read_text(errors='replace')
        ok='UTNT_STEAM_COOP_COMPLETE' in out and 'UTNT_ASSERT FAIL' not in out and 'consistency failure' not in out.lower() and out.count('UTNT_ASSERT PASS')==(14 if label.endswith('-0') else 12)
        result={'label':label,'ok':ok,'assertions':out.count('UTNT_ASSERT PASS'),'teardown':'only this runner\'s two peers terminated after completion'}
        results.append(result);print(json.dumps(result),flush=True)
finally:
    for child,f,label in children:
        if child.poll() is None:child.kill();child.wait()
        if not f.closed:f.close()
(logs/'steam-coop-results.json').write_text(json.dumps(results,indent=2))
assert len(results)==2 and all(r['ok'] for r in results)
