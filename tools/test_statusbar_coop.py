"""Two local UZDoom peers: map-wide statistics and independent HUD settings/state.
Set UTNT_ENGINE and UTNT_IWAD. Each peer uses its own temporary config.
"""
import argparse,json,os,pathlib,subprocess,time
from check_engine import ROOT
from test_statusbar import compile_fixture

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mod',type=pathlib.Path,default=ROOT/'tutnt')
    a=p.parse_args();addon=compile_fixture();logs=ROOT/'logs';processes=[];results=[]
    si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
    try:
        for i in range(2):
            label=f'statusbar-coop-{i}';mode=0 if i==0 else 4
            config=logs/(label+'.ini')
            config.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=658\nwin_h=527\nvid_maxfps=60\ni_pauseinbackground=false\nvid_activeinbackground=true\n')
            cfg=logs/(label+'.cfg')
            cfg.write_text(f'wait 160; event hudresources; event hudoptions {mode}; netevent hudready; wait 12; netevent hudcheck 0; netevent hudcutscene 1; wait 12; netevent hudcheck 1; netevent hudcutscene 0; wait 12; netevent hudcheck 0; screenshot logs/{label}.png; wait 12; echo UTNT_COOPHUD_COMPLETE\n')
            args=[os.environ['UTNT_ENGINE'],'-iwad',os.environ['UTNT_IWAD'],'-file',str(a.mod.resolve()),str(addon),
                '-config',str(config),'-noautoload','-nosound','-stdout','-noidle','+vid_fullscreen','false',
                '+vid_preferbackend','1','+screenblocks','11','+fullhud_stats',str(mode),'+map','UTNTTEST','+exec',str(cfg)]
            args+=['-host','2','-port','15219'] if i==0 else ['-join','127.0.0.1:15219']
            handle=(logs/(label+'.log')).open('wb')
            child=subprocess.Popen(args,cwd=ROOT,stdout=handle,stderr=subprocess.STDOUT,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
            processes.append((child,handle,label))
            if i==0:time.sleep(1)
        deadline=time.monotonic()+40
        while time.monotonic()<deadline:
            outputs=[(logs/(label+'.log')).read_text(errors='replace') for child,handle,label in processes]
            if all('UTNT_COOPHUD_COMPLETE' in out for out in outputs):break
            if any('Script error,' in out or 'UTNT_ASSERT FAIL' in out for out in outputs):break
            if any(child.poll() is not None for child,handle,label in processes):break
            time.sleep(0.2)
        for child,handle,label in processes:
            if child.poll() is None:child.terminate()
            child.wait(timeout=5);handle.close()
            out=(logs/(label+'.log')).read_text(errors='replace')
            ok=all(marker in out for marker in ['UTNT_COOPHUD_COMPLETE','UTNT_HUD_STATS_COMPLETE','UTNT_REGRESSION_COMPLETE'])
            ok=ok and not any(error in out for error in ['UTNT_ASSERT FAIL','VM execution aborted','Script error,','Unknown command'])
            result=dict(label=label,ok=ok,assertions=out.count('UTNT_ASSERT PASS'),teardown='runner stopped its own peers after completion markers')
            results.append(result);print(json.dumps(result),flush=True)
    finally:
        for child,handle,label in processes:
            if child.poll() is None:child.kill();child.wait()
            if not handle.closed:handle.close()
    (logs/'statusbar-coop-results.json').write_text(json.dumps(results,indent=2)+'\n')
    raise SystemExit(0 if len(results)==2 and all(r['ok'] for r in results) else 1)

if __name__=='__main__':main()
