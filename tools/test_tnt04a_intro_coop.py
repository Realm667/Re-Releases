from pathlib import Path
import subprocess,time,json,os,argparse
from check_engine import ROOT
p=argparse.ArgumentParser(description="Two real peers: the guest skips the shared TNT04A intro.")
p.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE'))
p.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD'))
p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
p.add_argument('--work',type=Path,default=ROOT)
p.add_argument('--port',type=int,default=15253)
a=p.parse_args()
if not a.engine or not a.iwad:p.error('Configure engine and IWAD')
R=ROOT;W=a.work;logs=W/'logs';logs.mkdir(parents=True,exist_ok=True);procs=[]

si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
try:
 for i in range(2):
  label='intro-coop-'+str(i);ini=logs/(label+'.ini');ini.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=658\nwin_h=527\nvid_maxfps=60\ni_pauseinbackground=false\nvid_activeinbackground=true\n')
  cmd=['wait 100','netevent introstage 0']
  if i:cmd+=['wait 80','+use','wait 5','-use']
  else:cmd+=['wait 85']
  cmd+=['wait 100','netevent introstage 1','netevent introvoice','wait 175','netevent introobjectives','wait 20','echo UTNT_INTRO_COOP_COMPLETE']
  cfg=logs/(label+'.cfg');cfg.write_text('; '.join(cmd))
  args=[str(a.engine),'-iwad',str(a.iwad),'-file',str(a.mod.resolve()),str(ROOT/'tools/intro-skip-tests'),'-config',str(ini),'-noautoload','-nosound','-stdout','-noidle','+vid_fullscreen','false','+vid_preferbackend','1','+map','TNT04A','+exec',cfg.as_posix()]
  args+=['-host','2','-port',str(a.port)] if i==0 else ['-join','127.0.0.1:'+str(a.port)]
  f=(logs/(label+'.log')).open('wb');child=subprocess.Popen(args,cwd=W,stdout=f,stderr=subprocess.STDOUT,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW);procs.append((child,f,label))
  if not i:time.sleep(1)
 deadline=time.monotonic()+60
 while time.monotonic()<deadline:
  outputs=[(logs/(label+'.log')).read_text(errors='replace') for _,_,label in procs]
  if all('UTNT_INTRO_COOP_COMPLETE' in s for s in outputs):break
  if any(any(e in s for e in ['UTNT_ASSERT FAIL','Script error,','VM execution aborted','Consistency failure']) for s in outputs):break
  if any(p.poll() is not None for p,_,_ in procs):break
  time.sleep(.3)
 results=[]
 for p,f,label in procs:
  if p.poll() is None:p.terminate()
  p.wait(timeout=5);f.close();out=(logs/(label+'.log')).read_text(errors='replace');ok='UTNT_INTRO_COOP_COMPLETE' in out and not any(e in out for e in ['UTNT_ASSERT FAIL','Script error,','VM execution aborted','Consistency failure'])
  results.append(dict(label=label,ok=ok,assertions=out.count('UTNT_ASSERT PASS')))
 (W/'coop-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))
finally:
 for p,f,_ in procs:
  if p.poll() is None:p.kill();p.wait()
  if not f.closed:f.close()

raise SystemExit(0 if len(results)==2 and all(r["ok"] for r in results) else 1)
