"""Two real peers must have independent local cavern skybox parallax."""
from pathlib import Path
import argparse,json,os,re,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine',default='F:/DoomDev/uzdoom.exe');p.add_argument('--iwad',default='F:/DoomDev/DOOM2.WAD')
    p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3');p.add_argument('--overlay',type=Path)
    p.add_argument('--label',default='cavern-parallax-coop');p.add_argument('--port',default='15517')
    a=p.parse_args();work=ROOT/'tutnt/.codex/work/cavern-tnt03a2';logs=ROOT/'tutnt/.codex/logs/cavern-tnt03a2'
    logs.mkdir(parents=True,exist_ok=True);children=[];results=[];positions=[]
    si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
    try:
        for peer in range(2):
            label=f'{a.label}-{peer}';config=logs/(label+'.ini')
            config.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=720\nwin_h=480\nvid_maxfps=60\ni_pauseinbackground=false\nvid_activeinbackground=true\nvid_lowerinbackground=false\n')
            args=[a.engine,'-iwad',a.iwad,'-file',str(a.mod.resolve())]
            if a.overlay:args.append(str(a.overlay.resolve()))
            args+=[str(ROOT/'tools/fixtures/cavern-coop'),'-config',str(config),'-noautoload','-nosound','-stdout','-noidle','+vid_fullscreen','false','+vid_preferbackend','1','+use_mouse','false','+use_joystick','false','+UTNT_fxquality',str(0 if peer==0 else 3),'+map','TNT03A2']
            args+=['-host','2','-port',a.port] if peer==0 else ['-join','127.0.0.1:'+a.port]
            handle=(logs/(label+'.log')).open('wb')
            child=subprocess.Popen(args,cwd=work,stdout=handle,stderr=subprocess.STDOUT,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
            children.append((child,handle,label))
            if peer==0:time.sleep(1)
        deadline=time.monotonic()+50
        while time.monotonic()<deadline:
            outputs=[(logs/(label+'.log')).read_text(errors='replace') for _,_,label in children]
            if all('UTNT_CAVERN_COOP_COMPLETE' in out for out in outputs):break
            if any(child.poll() is not None for child,_,_ in children):break
            if any('Script error,' in out or 'VM execution aborted' in out for out in outputs):break
            time.sleep(.2)
        for child,handle,label in children:
            if child.poll() is None:child.terminate()
            child.wait(timeout=5);handle.close()
            out=(logs/(label+'.log')).read_text(errors='replace')
            records=re.findall(r'CAVERN_PEER_VIEW (\d+) (\d+) ([\d.-]+) ([\d.-]+) ([\d.-]+)',out)
            positions.append({int(r[1]):tuple(map(float,r[2:])) for r in records})
            errors=[s for s in ['UTNT_ASSERT FAIL','VM execution aborted','Script error,','consistency failure','out of sync','mismatched client-side handling'] if s.lower() in out.lower()]
            ok='UTNT_CAVERN_COOP_COMPLETE' in out and not errors and out.count('UTNT_ASSERT PASS')==7
            results.append(dict(label=label,ok=ok,assertions=out.count('UTNT_ASSERT PASS'),errors=errors))
        independent=len(positions)==2 and all(len(r)==3 for r in positions) and all(positions[0][i]!=positions[1][i] for i in range(3))
        for result in results:result['independent_viewpoints']=independent;result['ok'] &= independent
    finally:
        for child,handle,_ in children:
            if child.poll() is None:child.kill();child.wait()
            if not handle.closed:handle.close()
    dest=ROOT/'tutnt/.codex/validation/cavern-tnt03a2';dest.mkdir(parents=True,exist_ok=True)
    (dest/(a.label+'.json')).write_text(json.dumps(results,indent=2))
    print(json.dumps(results),flush=True)
    return 0 if len(results)==2 and all(r['ok'] for r in results) else 1
if __name__=='__main__':raise SystemExit(main())
