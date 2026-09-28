"""Two real peers: independent sky parallax, viewer switches, shared world clock."""
from pathlib import Path
import argparse,json,re,socket,subprocess,time,zipfile
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--engine',default='F:/DoomDev/uzdoom.exe')
    ap.add_argument('--iwad',default='F:/DoomDev/DOOM2.WAD')
    ap.add_argument('--mod',type=Path,default=ROOT/'zdcmp1.pk3')
    args=ap.parse_args()
    logs=ROOT/'tutnt/.codex/logs/zdc-sky-parallax-coop';logs.mkdir(parents=True,exist_ok=True)
    addon=ROOT/'tutnt/.codex/builds/zdc-sky-parallax-qa.pk3'
    with zipfile.ZipFile(addon,'w') as z:
        z.write(ROOT/'tools/zdcmp1-tests/sky-parallax.zc','zscript.zc')
        z.writestr('mapinfo.txt','gameinfo { AddEventHandlers="ZDCSkyParallaxQA" }')
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as s:
        s.bind(('127.0.0.1',0));port=s.getsockname()[1]
    peers=[];results=[];views=[];states=[]
    si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
    try:
        for i in range(2):
            cfg=logs/f'peer-{i}.ini'
            cfg.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=800\nwin_h=500\nvid_maxfps=60\ni_pauseinbackground=false\nvid_activeinbackground=true\n')
            script=logs/f'peer-{i}.cfg'
            script.write_text('wait 600; quit\n')
            log=logs/f'peer-{i}.log';out=log.open('wb')
            command=[args.engine,'-iwad',args.iwad,'-file',str(args.mod.resolve()),str(addon),'-config',str(cfg),'-noautoload','-nosound','-stdout','-noidle','-rngseed','667','+vid_fullscreen','false','+vid_preferbackend','1','+use_mouse','false','+use_joystick','false','+map','MAP01','+exec',str(script)]
            command+=['-host','2','-port',str(port)] if i==0 else ['-join',f'127.0.0.1:{port}']
            child=subprocess.Popen(command,cwd=logs,stdout=out,stderr=subprocess.STDOUT,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
            peers.append((child,out,log))
            if i==0:time.sleep(1)
        deadline=time.monotonic()+55
        while time.monotonic()<deadline:
            texts=[log.read_text(errors='replace') for _,_,log in peers]
            if all('SKY_PARALLAX_COMPLETE' in t for t in texts):break
            if any('Script error,' in t or 'VM execution aborted' in t for t in texts):break
            if all(p.poll() is not None for p,_,_ in peers):break
            time.sleep(.2)
        for i,(_,_,log) in enumerate(peers):
            text=log.read_text(errors='replace')
            errors=[s for s in ('SKY_ASSERT FAIL','VM execution aborted','Script error,','consistency failure','out of sync','mismatched client-side handling') if s.lower() in text.lower()]
            records=re.findall(r'SKY_VIEW (\d+) (\d+) ([-.\d]+) ([-.\d]+) ([-.\d]+) ([-.\d]+) ([-.\d]+) ([-.\d]+)',text)
            views.append({int(r[1]):tuple(map(float,r[2:])) for r in records})
            sync=re.search(r'SKY_SYNC (.*)',text);states.append(sync[1] if sync else None)
            results.append(dict(peer=i,ok='SKY_PARALLAX_COMPLETE' in text and not errors and text.count('SKY_ASSERT PASS')==20,assertions=text.count('SKY_ASSERT PASS'),errors=errors))
        independent=all(len(v)==5 for v in views)
        if independent:
            a,b=views
            independent=(a[160]!=b[160] and a[160]!=a[240] and b[160]==b[240]
                         and a[240]==a[320] and b[240]!=b[320]
                         and a[380]==b[320] and b[380]==a[320]
                         and a[440]==a[320] and b[440]==b[320])
        for r in results:
            r.update(independent_viewpoints=independent,synchronized_world=states[0] is not None and states[0]==states[1])
            r['ok'] &= independent and r['synchronized_world']
    finally:
        for p,out,_ in peers:
            if p.poll() is None:p.terminate()
            try:p.wait(timeout=5)
            except subprocess.TimeoutExpired:p.kill();p.wait()
            out.close()
    report=dict(results=results,views=views,world_states=states)
    (ROOT/'tutnt/.codex/validation/zdc-sky-parallax-coop.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    return 0 if len(results)==2 and all(r['ok'] for r in results) else 1
if __name__=='__main__':raise SystemExit(main())
