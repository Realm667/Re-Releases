"""Two real TNT04A peers: independent reading and host-only cinematic skip."""
import argparse,json,os,pathlib,subprocess,time
from check_engine import ROOT
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mod',type=pathlib.Path,default=ROOT/'tutnt');a=p.parse_args()
addon=ROOT/'tools/intro-chapter-tests';logs=ROOT/'logs';processes=[];results=[]
si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
try:
 for i in range(2):
  label=f'intro-coop-{i}';ini=logs/(label+'.ini')
  ini.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=658\nwin_h=527\nvid_maxfps=60\ni_pauseinbackground=false\nvid_activeinbackground=true\n')
  cfg=logs/(label+'.cfg')
  if i==0:commands='wait 330; netevent introcoop; wait 40; +use; wait 5; -use; wait 40; netevent introstage 1; wait 5; echo UTNT_CHAPTER_COOP_COMPLETE\n'
  else:commands='wait 230; netevent utnt_chapter 0 3; wait 10; netevent utnt_chapter 1 3; wait 10; +use; wait 5; -use; wait 75; netevent introcoop; wait 110; netevent introstage 1; wait 5; echo UTNT_CHAPTER_COOP_COMPLETE\n'
  cfg.write_text(commands)
  args=[os.environ['UTNT_ENGINE'],'-iwad',os.environ['UTNT_IWAD'],'-file',str(a.mod.resolve()),str(addon),'-config',str(ini),
        '-noautoload','-nosound','-stdout','-noidle','+vid_fullscreen','false','+vid_preferbackend','1','+UTNT_uiscale','1.5' if i else '1',
        '+language','deu' if i else 'enu','+map','TNT04A','+exec',cfg.as_posix()]
  args+=['-host','2','-port','15349'] if i==0 else ['-join','127.0.0.1:15349']
  f=(logs/(label+'.log')).open('wb');child=subprocess.Popen(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
  processes.append((child,f,label))
  if i==0:time.sleep(1)
 deadline=time.monotonic()+50
 while time.monotonic()<deadline:
  outputs=[(logs/(label+'.log')).read_text(errors='replace') for _,_,label in processes]
  if all('UTNT_CHAPTER_COOP_COMPLETE' in s for s in outputs):break
  if any(any(e in s for e in ('UTNT_ASSERT FAIL','Script error,','VM execution aborted','Consistency failure')) for s in outputs):break
  if any(c.poll() is not None for c,_,_ in processes):break
  time.sleep(.2)
 for child,f,label in processes:
  if child.poll() is None:child.terminate()
  child.wait(timeout=5);f.close();out=(logs/(label+'.log')).read_text(errors='replace')
  ok='UTNT_CHAPTER_COOP_COMPLETE' in out and not any(e in out for e in ('UTNT_ASSERT FAIL','VM execution aborted','Consistency failure','Script error,','Unknown command'))
  r=dict(label=label,ok=ok,assertions=out.count('UTNT_ASSERT PASS'),teardown='runner stopped its own peers');results.append(r);print(json.dumps(r),flush=True)
finally:
 for child,f,_ in processes:
  if child.poll() is None:child.kill();child.wait()
  if not f.closed:f.close()
(logs/'intro-coop-results.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(0 if len(results)==2 and all(r['ok'] for r in results) else 1)
