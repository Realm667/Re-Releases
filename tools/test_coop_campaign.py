"""Four real peers: death during the original TNT04A cutscene and transition to TNT04B."""
import json,os,pathlib,subprocess,time
from check_engine import ROOT

engine=pathlib.Path(os.environ['UTNT_ENGINE']);iwad=pathlib.Path(os.environ['UTNT_IWAD'])
logs=ROOT/'logs';logs.mkdir(exist_ok=True)
processes=[];results=[]
si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
try:
 for i in range(4):
  label=f'coop-campaign-{i}'
  ini=logs/(label+'.ini');ini.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=658\nwin_h=527\nvid_maxfps=35\n')
  cfg=logs/(label+'.cfg');cfg.write_text('\n')
  args=[str(engine),'-iwad',str(iwad),'-file',str(ROOT/'tutnt'),str(ROOT/'tools/coop-campaign'),'-config',str(ini),'-noautoload','-nosound','-stdout','-noidle','+vid_fullscreen','false','+vid_preferbackend','1','+playerclass',('Marine','Scout','Commando','Marine')[i],'+UTNT_fxquality',str(i),'+UTNT_reducedfx','true' if i==2 else 'false','+map','TNT04A','+exec',str(cfg)]
  args+=['-host','4','-port','15229'] if i==0 else ['-join','127.0.0.1:15229']
  f=(logs/(label+'.log')).open('wb')
  child=subprocess.Popen(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
  processes.append((child,f,label))
  if i==0:time.sleep(1)
 deadline=time.monotonic()+180
 while time.monotonic()<deadline:
  outputs=[(logs/(label+'.log')).read_text(errors='replace') for _,_,label in processes]
  if all('UTNT_COOP_CAMPAIGN_COMPLETE' in out for out in outputs):break
  if any(c.poll() is not None for c,_,_ in processes[:3]):break
  time.sleep(.2)
 for i,(child,f,label) in enumerate(processes):
  out=(logs/(label+'.log')).read_text(errors='replace')
  marker='UTNT_COOP_CAMPAIGN_COMPLETE'
  ok=marker in out and not any(e in out for e in ('UTNT_ASSERT FAIL','VM execution aborted','Consistency failure'))
  if child.poll() is None:child.terminate()
  code=child.wait(timeout=5);f.close()
  results.append(dict(label=label,ok=ok,exit=code,assertions=out.count('UTNT_ASSERT PASS'),teardown='runner cleanup after assertions'))
finally:
 for child,f,_ in processes:
  if child.poll() is None:child.kill();child.wait()
  f.close()
(logs/'coop-campaign-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
raise SystemExit(0 if len(results)==4 and all(r['ok'] for r in results) else 1)
