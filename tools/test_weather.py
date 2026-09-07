"""UZDoom weather regression suite. Uses isolated settings/saves and an add-on.

Set UTNT_ENGINE / UTNT_IWAD, then run python tools/test_weather.py.
--case selects a smaller subset; --mod can test the final packaged PK3.
"""
import argparse,json,os,pathlib,re,subprocess,time
from check_engine import ROOT,run_case

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case',choices=['all','motion','quality','geometry','lifecycle','smoke','review','hub','audio','coop'],default='all')
    p.add_argument('--renderer',choices=['0','1','both'],default='both')
    p.add_argument('--mod',type=pathlib.Path)
    a=p.parse_args(); addon=ROOT/'tools/weather-tests'; results=[]
    engine=os.environ['UTNT_ENGINE']; iwad=os.environ['UTNT_IWAD']
    compile_check=run_case(engine,iwad,mod=a.mod,addon=addon,label='weather-final-compile')
    if not compile_check['ok']: raise SystemExit(1)
    renderers=['0','1'] if a.renderer=='both' else [a.renderer]
    cases=['motion','quality','geometry','lifecycle','smoke','review','hub','audio','coop'] if a.case=='all' else [a.case]
    for case in cases:
        if case in ['audio','coop']: continue
        maps=['UTNTWX'] if case in ['geometry','motion','quality'] else ['TNT02','TNT03A1'] if case in ['lifecycle','review'] else ['TNT03A2'] if case=='smoke' else ['TNT03A1']
        for renderer in renderers:
            for name in maps:
                label=f'weather-final-{case}-{name}-{renderer}'
                commands=(addon/(case+'.cfg')).read_text() if case in ['geometry','motion','quality','lifecycle','hub'] else ''
                if case=='smoke': commands='wait 300; event weathercheck 1; echo UTNT_TEST_END; wait 5; quit\n'
                if case=='review':
                    size='1440 1080' if name=='TNT03A1' else '1440 810'
                    place='netevent weathertree 3 270; wait 80;' if name=='TNT02' else ''
                    commands=f'wait 100; {place} use UTNTMinigun; screenblocks 12; crosshair 0; UTNT_subtitles false; fullhud_fullstats false; vid_setsize {size}; wait 250; event weathercheck 1; screenshot logs/{label}.png; echo UTNT_TEST_END; wait 5; quit\n'
                r=run_case(engine,iwad,mod=a.mod,mapname=name,renderer=renderer,addon=addon,label=label,commands=commands,timeout=65,regression=True,
                    settings=[('weatherfx',True),('UTNT_fxquality',3),('UTNT_reducedfx',False),('UTNT_atmosphere',False),('con_notifytime',0),('i_pauseinbackground',False),('vid_activeinbackground',True)])
                log=pathlib.Path(r['log']).read_text()
                if case=='geometry':
                    counts=re.findall(r'accounting live (\d+) actual',log)
                    r['freeze_stable']=len(counts)>=3 and counts[1]==counts[2]
                    r['ok'] &= r['freeze_stable']
                results.append(r)
                if not r['ok']: print(log[-5000:]); break
    if 'audio' in cases: results.append(audio(engine,iwad,a.mod,addon))
    if 'coop' in cases: results.extend(coop(engine,iwad,a.mod,addon))
    (ROOT/'logs'/f'weather-final-{a.case}-results.json').write_text(json.dumps(results,indent=2)+'\n')
    raise SystemExit(0 if results and all(r['ok'] for r in results) else 1)

def launch_options():
    if os.name!='nt': return {}
    si=subprocess.STARTUPINFO(); si.dwFlags|=subprocess.STARTF_USESHOWWINDOW; si.wShowWindow=0
    return dict(startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)

def audio(engine,iwad,mod,addon):
    label='weather-final-audio'; logs=ROOT/'logs'
    ini=logs/(label+'.ini'); ini.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=658\nwin_h=527\n')
    cfg=logs/(label+'.cfg'); cfg.write_text('wait 100; netevent weatheraudio; wait 10; echo UTNT_TEST_END; quit\n')
    args=[engine,'-iwad',iwad,'-file',str(mod or ROOT/'tutnt'),str(addon),'-config',str(ini),'-noautoload','-stdout','-noidle',
          '+snd_sfxvolume','0.01','+snd_musicvolume','0','+map','UTNTWX','+exec',str(cfg)]
    r=subprocess.run(args,cwd=ROOT,capture_output=True,timeout=30,**launch_options())
    out=(r.stdout+r.stderr).decode(errors='replace'); (logs/(label+'.log')).write_text(out)
    result=dict(label=label,ok=r.returncode==0 and 'UTNT_ASSERT PASS: weather audio decodes' in out and 'UTNT_TEST_END' in out,assertions=out.count('UTNT_ASSERT PASS'))
    print(json.dumps(result),flush=True)
    if not result['ok']: print(out[-3000:])
    return result

def coop(engine,iwad,mod,addon):
    logs=ROOT/'logs'; children=[]; results=[]
    try:
        for i in range(2):
            label=f'weather-final-coop-{i}'; config=logs/(label+'.ini')
            config.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=658\nwin_h=527\nvid_maxfps=60\ni_pauseinbackground=false\nvid_activeinbackground=true\n')
            cfg=logs/(label+'.cfg')
            cfg.write_text(f'wait 240; event weathercheck {i}; netevent weatherworld; wait 80; event weathercheck {i}; echo UTNT_WEATHER_COOP_COMPLETE\n')
            args=[engine,'-iwad',iwad,'-file',str(mod or ROOT/'tutnt'),str(addon),'-config',str(config),'-noautoload','-nosound','-stdout','-noidle',
                  '+vid_fullscreen','false','+vid_preferbackend','1','+weatherfx','true','+UTNT_fxquality',str(0 if i==0 else 3),'+map','UTNTWX','+exec',str(cfg)]
            args+=['-host','2','-port','15239'] if i==0 else ['-join','127.0.0.1:15239']
            handle=(logs/(label+'.log')).open('wb')
            child=subprocess.Popen(args,cwd=ROOT,stdout=handle,stderr=subprocess.STDOUT,**launch_options());children.append((child,handle,label))
            if i==0: time.sleep(1)
        deadline=time.monotonic()+40
        while time.monotonic()<deadline:
            out=[(logs/(label+'.log')).read_text(errors='replace') for _,_,label in children]
            if all('UTNT_WEATHER_COOP_COMPLETE' in s for s in out): break
            if any('VM execution aborted' in s or 'Script error,' in s for s in out): break
            time.sleep(.2)
        shared=[]
        for child,handle,label in children:
            if child.poll() is None: child.terminate()
            child.wait(timeout=5); handle.close()
            out=(logs/(label+'.log')).read_text(errors='replace'); shared.append(re.findall(r'WEATHER_SHARED.*',out))
            ok='UTNT_WEATHER_COOP_COMPLETE' in out and 'UTNT_ASSERT FAIL' not in out and 'out of sync' not in out.lower()
            results.append(dict(label=label,ok=ok,assertions=out.count('UTNT_ASSERT PASS')))
        match=bool(shared[0]) and shared[0]==shared[1]
        for result in results: result['shared_state_matches']=match; result['ok'] &= match; print(json.dumps(result),flush=True)
    finally:
        for child,handle,_ in children:
            if child.poll() is None: child.kill();child.wait()
            if not handle.closed:handle.close()
    return results

if __name__=='__main__': main()
