"""Four or eight real peers: simultaneous checkpoint respawns and disconnect.
Run with --players 8 for coverage of player slots 5-8.
"""
import argparse,json,os,pathlib,subprocess,time
from check_engine import ROOT
from compile_test_acs import compile_tests
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--players",type=int,choices=(4,8),default=4)
parser.add_argument("--mod",type=pathlib.Path,default=ROOT/"tutnt.pk3")
opts=parser.parse_args();count=opts.players
prefix="eight-player" if count==8 else "four-player"
marker="UTNT_EIGHTPLAYER_COMPLETE" if count==8 else "UTNT_FOURPLAYER_COMPLETE"
compile_tests()
engine=pathlib.Path(os.environ['UTNT_ENGINE']);iwad=pathlib.Path(os.environ['UTNT_IWAD'])
logs=ROOT/'tutnt/.codex/logs'/prefix;logs.mkdir(parents=True,exist_ok=True)
processes=[];results=[]
si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
try:
 for i in range(count):
  label=f'{prefix}-{i}'
  ini=logs/(label+'.ini');ini.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=658\nwin_h=527\nvid_maxfps=35\n')
  cfg=logs/(label+'.cfg');cfg.write_text('wait 365; quit\n' if i==count-1 else '\n')
  args=[str(engine),'-iwad',str(iwad),'-file',str(opts.mod.resolve()),str(ROOT/'tools/runtime-tests'),'-config',str(ini),'-savedir',str(logs),'-noautoload','-nosound','-stdout','-noidle','+vid_fullscreen','false','+vid_preferbackend','1','+playerclass',('Marine','Scout','Commando','Marine')[i%4],'+UTNT_fxquality',str(i%4),'+UTNT_reducedfx','true' if i==2 else 'false','+UTNT_shaderoverlayswitch','true' if i%2 else 'false','+UTNT_ambientsmoke','false' if i%2 else 'true','+UTNT_heartbeatvolume',str((i%4)/3),'+UTNT_lowhealthfx','true' if i%2 else 'false','+map','UTNTTEST','+exec',str(cfg)]
  args+=['-host',str(count),'-port','15219'] if i==0 else ['-join','127.0.0.1:15219']
  f=(logs/(label+'.log')).open('wb')
  child=subprocess.Popen(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
  processes.append((child,f,label))
  if i==0:time.sleep(1)
 deadline=time.monotonic()+150
 while time.monotonic()<deadline:
  outputs=[(logs/(label+'.log')).read_text(errors='replace') for _,_,label in processes]
  if all(marker in out for out in outputs[:-1]):break
  if any(c.poll() is not None for c,_,_ in processes[:-1]):break
  if any(any(error in out for error in ('Script error,','UTNT_ASSERT FAIL','VM execution aborted','Consistency failure')) for out in outputs):break
  time.sleep(.2)
 for i,(child,f,label) in enumerate(processes):
  out=(logs/(label+'.log')).read_text(errors='replace')
  required=marker if i<count-1 else 'UTNT_RESPAWN_COMPLETE'
  ok=required in out and not any(e in out for e in ('UTNT_ASSERT FAIL','VM execution aborted','Consistency failure'))
  if child.poll() is None:child.terminate()
  code=child.wait(timeout=5);f.close()
  results.append(dict(label=label,ok=ok,exit=code,assertions=out.count('UTNT_ASSERT PASS'),teardown='graceful quit' if i==count-1 else 'runner cleanup after assertions'))
finally:
 for child,f,_ in processes:
  if child.poll() is None:child.kill();child.wait()
  f.close()
(logs/'results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
raise SystemExit(0 if len(results)==count and all(r['ok'] for r in results) else 1)
