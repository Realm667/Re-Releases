"""Four real peers compare all rows, reject guest skip and require readiness."""
import argparse,json,os,subprocess,time
from pathlib import Path
from check_engine import ROOT

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
    parser.add_argument('--metrics',action='store_true')
    a=parser.parse_args();logs=ROOT/'tutnt/.codex/logs';children=[];results=[]
    si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
    try:
        for i in range(4):
            label=f'transitions-coop-{i}';ini=logs/(label+'.ini');cfg=logs/(label+'.cfg')
            ini.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=978\nwin_h=587\nvid_maxfps=60\ni_pauseinbackground=false\nvid_activeinbackground=true\n')
            if i==0:
                commands=['wait 120','netevent trseed','wait 10','netevent trfade 1','wait 250',
                  'netevent trcheck 20 20 0','netevent utnt_chapter 4 1','wait 15','event trview',
                  f'screenshot logs/{label}-chapter.png','netevent utnt_chapter 4 1','wait 15',
                  'netevent utnt_chapter 5 1','wait 15','netevent trphase 0','wait 170',
                  'netevent utnt_chapter 5 1','wait 140','netevent trmap 2','netevent trreleased']
            else:
                commands=['wait 410','netevent utnt_chapter 3 1','wait 15','netevent trphase 0',
                  'netevent trcheck 20 20 0','netevent utnt_chapter 4 1','wait 15',
                  f'screenshot logs/{label}-chapter.png','netevent utnt_chapter 4 1','wait 15',
                  'netevent utnt_chapter 5 1','wait 270','netevent trmap 2','netevent trreleased']
            if a.metrics:
                # Host applies deterministic gameplay events to all four player pawns.
                if i==0:
                    commands=['wait 130','netevent metrun','wait 40','netevent metweapon','netevent trfade 1',
                      'wait 8','event metfade','wait 245','netevent metresults','netevent utnt_chapter 4 1','wait 15',
                      'netevent utnt_chapter 6 1','wait 15',f'screenshot logs/{label}-combat.png',
                      'netevent utnt_chapter 6 1','wait 15',f'screenshot logs/{label}-weapons.png',
                      'netevent utnt_chapter 6 1','wait 15','netevent utnt_chapter 6 1','wait 15',
                      f'screenshot logs/{label}-abilities.png','netevent utnt_chapter 4 1','wait 15',
                      'netevent utnt_chapter 5 1','wait 60','netevent utnt_chapter 5 1','wait 140','netevent trmap 2']
                else:
                    commands=['wait 460','netevent metresults','netevent utnt_chapter 4 1','wait 15',
                      'netevent utnt_chapter 6 1','wait 15',f'screenshot logs/{label}-combat.png',
                      'netevent utnt_chapter 4 1','wait 15','netevent utnt_chapter 5 1','wait 310','netevent trmap 2']
            cfg.write_text('; '.join(commands+['echo UTNT_COOP_TRANSITION_END']))
            args=[os.environ.get('UTNT_ENGINE','F:/DoomDev/uzdoom.exe'),'-iwad',os.environ.get('UTNT_IWAD','F:/DoomDev/DOOM2.WAD'),
              '-file',str(a.mod.resolve()),str(ROOT/'tools/fixtures/transitions'),'-config',str(ini),'-savedir',str(logs/'saves'),
              '-noautoload','-nosound','-stdout','-noidle','+name',f'Player {i+1}',
              '+vid_fullscreen','false','+vid_preferbackend','1','+language',['en','de','es','fr'][i],
              '+wipetype','1','+con_notifytime','0','+map','TNT01','+exec',str(cfg)]
            args+=['-host','4','-port','15257'] if i==0 else ['-join','127.0.0.1:15257']
            f=(logs/(label+'.log')).open('wb')
            child=subprocess.Popen(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
            children.append((child,f,label))
            if i==0:time.sleep(1)
        deadline=time.monotonic()+100
        while time.monotonic()<deadline:
            outputs=[(logs/(label+'.log')).read_text(errors='replace') for _,_,label in children]
            if all('UTNT_COOP_TRANSITION_END' in s for s in outputs):break
            if any(any(e in s for e in ('UTNT_ASSERT FAIL','Script error,','VM execution aborted','Consistency failure')) for s in outputs):break
            if any(c.poll() is not None for c,_,_ in children):break
            time.sleep(.2)
        for child,f,label in children:
            if child.poll() is None:child.terminate()
            child.wait(timeout=5);f.close();out=(logs/(label+'.log')).read_text(errors='replace')
            ok='UTNT_COOP_TRANSITION_END' in out and not any(e in out for e in ('UTNT_ASSERT FAIL','VM execution aborted','Consistency failure','Script error,','Unknown command'))
            result=dict(label=label,ok=ok,assertions=out.count('UTNT_ASSERT PASS'))
            results.append(result);print(json.dumps(result),flush=True)
    finally:
        for child,f,_ in children:
            if child.poll() is None:child.kill();child.wait()
            if not f.closed:f.close()
    (logs/'transitions-coop-results.json').write_text(json.dumps(results,indent=2)+'\n')
    raise SystemExit(0 if len(results)==4 and all(r['ok'] for r in results) else 1)

if __name__=='__main__':main()
