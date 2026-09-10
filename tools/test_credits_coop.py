"""Two actual peers verify shared credits and host-only advancement/skip."""
from pathlib import Path
import subprocess,time,json,argparse
REPO=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--engine',required=True);p.add_argument('--iwad',required=True);p.add_argument('--mod',type=Path,default=REPO/'tutnt.pk3');p.add_argument('--port',default='15387');a=p.parse_args()
ROOT=a.out.resolve();ROOT.mkdir(parents=True,exist_ok=True);logs=ROOT/'logs';logs.mkdir(exist_ok=True);processes=[];results=[]
si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
try:
 for peer in range(2):
  label='credits-coop-'+str(peer);ini=logs/(label+'.ini');cfg=logs/(label+'.cfg')
  ini.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=658\nwin_h=407\nvid_maxfps=60\ni_pauseinbackground=false\nvid_activeinbackground=true\n')
  if peer==0:commands='wait 80; netevent creditstest 6 0 0; wait 35; netevent utnt_credit 0; wait 35; netevent creditstest 6 1 0; wait 40; netevent utnt_credit 2; wait 35; netevent creditstest 6 1 1; wait 5; echo UTNT_CREDITS_COOP_COMPLETE\n'
  else:commands='wait 50; netevent utnt_credit 2; wait 35; netevent creditstest 6 0 0; wait 55; netevent creditstest 6 1 0; wait 75; netevent creditstest 6 1 1; wait 5; echo UTNT_CREDITS_COOP_COMPLETE\n'
  cfg.write_text(commands)
  args=[a.engine,'-iwad',a.iwad,'-file',str(a.mod.resolve()),str(REPO/'tools/credits-tests'),'-config',str(ini),'-noautoload','-nosound','-stdout','-noidle','+vid_fullscreen','false','+vid_preferbackend','1','+con_notifytime','0','+use_mouse','false','+map','ENDMAP01','+exec',cfg.as_posix()]
  args+=['-host','2','-port',a.port] if peer==0 else ['-join','127.0.0.1:'+a.port]
  stream=(logs/(label+'.log')).open('wb');child=subprocess.Popen(args,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW);processes.append((child,stream,label))
  if peer==0:time.sleep(1)
 deadline=time.monotonic()+65
 while time.monotonic()<deadline:
  outputs=[(logs/(label+'.log')).read_text(errors='replace') for _,_,label in processes]
  if all('UTNT_CREDITS_COOP_COMPLETE' in s for s in outputs):break
  if any('UTNT_ASSERT FAIL' in s or 'VM execution aborted' in s or 'Consistency failure' in s for s in outputs):break
  if any(child.poll() is not None for child,_,_ in processes):break
  time.sleep(.2)
 for child,stream,label in processes:
  if child.poll() is None:child.terminate()
  child.wait(timeout=5);stream.close();out=(logs/(label+'.log')).read_text(errors='replace')
  ok='UTNT_CREDITS_COOP_COMPLETE' in out and not any(e in out for e in ['UTNT_ASSERT FAIL','VM execution aborted','Consistency failure','Script error,'])
  result={'label':label,'ok':ok,'assertions':out.count('UTNT_ASSERT PASS')};results.append(result);print(json.dumps(result),flush=True)
finally:
 for child,stream,_ in processes:
  if child.poll() is None:child.kill();child.wait()
  if not stream.closed:stream.close()
(ROOT/'credits-coop.json').write_text(json.dumps(results,indent=2))
assert len(results)==2 and all(r['ok'] and r['assertions']>=12 for r in results),results
