"""Two local peers, isolated configs, opposing local effect settings; no user saves."""
import json, os, pathlib, subprocess, time
from check_engine import ROOT
from compile_test_acs import compile_tests
compile_tests()
engine=pathlib.Path(os.environ.get('UTNT_ENGINE',ROOT/'engine/uzdoom.exe'))
iwad=pathlib.Path(os.environ.get('UTNT_IWAD',r'F:\DoomDev\DOOM2.WAD'))
logs=ROOT/'logs'; processes=[]; results=[]
si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
try:
 for i in range(2):
  label=f'coop-{i}'
  config=logs/(label+'.ini');config.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=658\nwin_h=527\nvid_maxfps=60\n')
  cfg=logs/(label+'.cfg');cfg.write_text('+forward\n')
  args=[str(engine),'-iwad',str(iwad),'-file',str(ROOT/'tutnt'),str(ROOT/'tools/runtime-tests'),'-config',str(config),'-noautoload','-nosound','-stdout','-noidle','+vid_fullscreen','false','+vid_preferbackend','1','+UTNT_fxquality','0' if i==0 else '3','+motionblur','false' if i==0 else 'true','+map','UTNTTEST','+exec',str(cfg)]
  args+=['-host','2','-port','15209'] if i==0 else ['-join','127.0.0.1:15209']
  f=(logs/(label+'.log')).open('wb')
  child=subprocess.Popen(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
  processes.append((child,f,label))
  if i==0:time.sleep(1)
 deadline=time.monotonic()+40
 while time.monotonic()<deadline:
  outputs=[(logs/(label+'.log')).read_text(errors='replace') for child,f,label in processes]
  if all('UTNT_RESPAWN_COMPLETE' in out for out in outputs):break
  if any(child.poll() is not None for child,f,label in processes):break
  time.sleep(0.2)
 for child,f,label in processes:
  # Explicit fixture teardown: only these two child processes belong to this run.
  stopped=child.poll() is None
  if stopped:child.terminate()
  code=child.wait(timeout=5);f.close();out=(logs/(label+'.log')).read_text(errors='replace')
  ok=stopped and 'UTNT_RESPAWN_COMPLETE' in out and 'second player keeps portal active' in out and 'UTNT_ASSERT FAIL' not in out
  result={'label':label,'ok':ok,'teardown':'runner terminated its peer after assertions','exit':code,'assertions':out.count('UTNT_ASSERT PASS')};results.append(result);print(json.dumps(result),flush=True)
finally:
 for child,f,label in processes:
  if child.poll() is None:child.kill();child.wait()
  if not f.closed:f.close()
(logs/'coop-results.json').write_text(json.dumps(results,indent=2))
raise SystemExit(0 if len(results)==2 and all(r['ok'] for r in results) else 1)
