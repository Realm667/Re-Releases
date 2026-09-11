"""Two local peers, opposing FX settings, identical Source guardian/shield state."""
from pathlib import Path
import argparse,json,subprocess,time
from check_engine import ROOT
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--map',dest='mapname',choices=['TNT04CN','TNT04C'],default='TNT04CN')
 p.add_argument('--engine',type=Path,required=True);p.add_argument('--iwad',type=Path,required=True)
 p.add_argument('--mod',type=Path,default=ROOT/'tutnt');p.add_argument('--work',type=Path,required=True)
 a=p.parse_args();W=a.work.resolve();W.mkdir(parents=True,exist_ok=True)
 si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
 children=[];results=[]
 try:
  for i in range(2):
   label=f'source-coop-{i}';config=W/(label+'.ini');cfg=W/(label+'.cfg')
   config.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=658\nwin_h=407\nvid_maxfps=60\ni_pauseinbackground=false\nvid_activeinbackground=true\n')
   command='wait 350; netevent sourcecheck 15000 0; wait 35; netevent sourceguardian; wait 30; netevent sourcecheck 15000 1; wait 315; netevent sourcecheck 15000 0; netevent sourceattack 2; wait 50; netevent sourceattackcheck 2; wait 10; netevent sourcekill; wait 111; netevent sourcedeathcheck 108 114; wait 149; netevent sourcedeathcheck 257 263; echo UTNT_SOURCE_COOP_COMPLETE' if i==0 else 'wait 1140; echo UTNT_SOURCE_COOP_COMPLETE'
   cfg.write_text(command+'\n')
   args=[str(a.engine),'-iwad',str(a.iwad),'-file',str(a.mod.resolve()),str(ROOT/'tools/source-tests'),'-config',str(config),'-noautoload','-nosound','-stdout','-noidle',
     '+vid_fullscreen','false','+vid_preferbackend','1','+UTNT_fxquality',str(i*3),'+UTNT_reducedfx','true' if i==0 else 'false','+map',a.mapname,'+exec',cfg.as_posix()]
   args+=['-host','2','-port','15367'] if i==0 else ['-join','127.0.0.1:15367']
   log=W/(label+'.log');handle=log.open('wb')
   child=subprocess.Popen(args,cwd=W,stdout=handle,stderr=subprocess.STDOUT,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
   children.append((child,handle,log))
   if i==0:time.sleep(1)
  deadline=time.monotonic()+65
  while time.monotonic()<deadline:
   logs=[log.read_text(errors='replace') for _,_,log in children]
   if all('UTNT_SOURCE_COOP_COMPLETE' in s for s in logs):break
   if any(any(e in s for e in ['Script error,','VM execution aborted','UTNT_ASSERT FAIL','Consistency failure']) for s in logs):break
   if any(child.poll() is not None for child,_,_ in children):break
   time.sleep(.25)
  for child,handle,log in children:
   if child.poll() is None:child.terminate()
   child.wait(timeout=5);handle.close();s=log.read_text(errors='replace')
   ok='UTNT_SOURCE_COOP_COMPLETE' in s and s.count('UTNT_ASSERT PASS')>=31 and not any(e in s for e in ['UTNT_ASSERT FAIL','VM execution aborted','Script error,','Consistency failure'])
   results.append({'label':log.stem,'ok':ok,'assertions':s.count('UTNT_ASSERT PASS'),'teardown':'runner stopped only its own two test peers'})
 finally:
  for child,handle,_ in children:
   if child.poll() is None:child.kill();child.wait()
   if not handle.closed:handle.close()
 (W/'runtime.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
 return 0 if len(results)==2 and all(r['ok'] for r in results) else 1
if __name__=='__main__':raise SystemExit(main())
