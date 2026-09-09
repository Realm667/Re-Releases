"""Two real local UZDoom peers: shared daylight/cloud/weather state on hub return."""
import argparse,json,re,subprocess,time
from pathlib import Path
from check_engine import ROOT,run_case
from test_weather import launch_options

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--work',type=Path,default=ROOT);p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
 p.add_argument('--engine',type=Path,required=True);p.add_argument('--iwad',type=Path,required=True)
 p.add_argument('--port',type=int,default=15367);a=p.parse_args();logs=a.work/'logs';logs.mkdir(exist_ok=True)
 addon=ROOT/'tools/cursed-tests'
 check=run_case(a.engine,a.iwad,root=a.work,mod=a.mod,addon=addon,label='cursed-coop-compile',timeout=20)
 if not check['ok']:return 1
 children=[];results=[]
 try:
  for i in range(2):
   label=f'cursed-coop-{i}';ini=logs/(label+'.ini')
   ini.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=658\nwin_h=527\nvid_maxfps=60\ni_pauseinbackground=false\nvid_activeinbackground=true\nvid_lowerinbackground=false\n')
   cfg=logs/(label+'.cfg')
   cfg.write_text('echo CURSED_HOST_READY; wait 360; netevent peaktime 10000; wait 10; netevent peakpeer 0; changemap TNT03A2; wait 90; netevent peakpeer 1; changemap TNT03A1; wait 90; netevent peakpeer 2\n' if i==0 else 'echo CURSED_CLIENT_READY\n')
   args=[str(a.engine),'-iwad',str(a.iwad),'-file',str(a.mod),str(addon),'-config',str(ini),'-noautoload','-nosound','-stdout','-noidle','+vid_fullscreen','false','+vid_preferbackend','1','+playerclass','Marine','+map','TNT03A1','+exec',cfg.as_posix()]
   args+=['-host','2','-port',str(a.port)] if i==0 else ['-join',f'127.0.0.1:{a.port}']
   handle=(logs/(label+'.log')).open('wb')
   child=subprocess.Popen(args,cwd=a.work,stdout=handle,stderr=subprocess.STDOUT,**launch_options());children.append((child,handle,label))
   if i==0:time.sleep(1)
  deadline=time.monotonic()+55
  while time.monotonic()<deadline:
   out=[(logs/(label+'.log')).read_text(errors='replace') for _,_,label in children]
   if all('CURSED_COOP_COMPLETE' in s for s in out):break
   if any('VM execution aborted' in s or 'Script error,' in s for s in out):break
   time.sleep(.2)
  states=[]
  for child,handle,label in children:
   if child.poll() is None:child.terminate()
   child.wait(timeout=5);handle.close()
   out=(logs/(label+'.log')).read_text(errors='replace');states.append(re.findall(r'CURSED_PEER[^\r\n]*',out))
   ok='CURSED_COOP_COMPLETE' in out and 'UTNT_ASSERT FAIL' not in out and 'out of sync' not in out.lower()
   results.append(dict(label=label,ok=ok,assertions=out.count('UTNT_ASSERT PASS')))
  match=len(states[0])==3 and states[0]==states[1]
  for r in results:r['identical_peer_states']=match;r['ok'] &= match
  (logs/'cursed-coop-result.json').write_text(json.dumps(dict(results=results,states=states),indent=2))
  print(json.dumps(results),flush=True)
  return 0 if all(r['ok'] for r in results) else 1
 finally:
  for child,handle,_ in children:
   if child.poll() is None:child.kill();child.wait()
   if not handle.closed:handle.close()

if __name__=='__main__':raise SystemExit(main())
