"""Isolated UZDoom compile/runtime checks. Set UTNT_ENGINE and UTNT_IWAD.
Python 3.11+. Every runtime case must reach its completion marker.
"""
import argparse, json, os, pathlib, subprocess, time
ROOT=pathlib.Path(__file__).resolve().parent.parent

def run_case(engine, iwad, *, root=ROOT, mod=None, mapname=None, addon=None,
             renderer='1', playerclass='Marine', timeout=30, label='load',
             commands=None, settings=(), regression=False, duration=140, quiet=False):
    root=pathlib.Path(root).resolve()
    engine=pathlib.Path(engine).resolve(); iwad=pathlib.Path(iwad).resolve()
    if mod: mod=pathlib.Path(mod).resolve()
    logs=root/'logs'; logs.mkdir(exist_ok=True)
    (logs/'saves').mkdir(exist_ok=True)
    config=logs/(label+'.ini')
    config.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=978\nwin_h=587\nvid_vsync=false\nvid_maxfps=120\n')
    args=[str(engine),'-iwad',str(iwad),'-file',str(mod or root/'tutnt')]
    if addon: args.append(str(pathlib.Path(addon).resolve()))
    args+=['-config',str(config),'-savedir',str(logs/'saves'),'-noautoload','-nosound','-stdout','-noidle','-rngseed','667']
    if mapname:
        args+=['+vid_fullscreen','false','+vid_preferbackend',str(renderer),'+playerclass',playerclass]
        for name,value in settings: args+=['+'+name,str(value)]
        args+=['+map',mapname]
        cfg=logs/(label+'.cfg')
        cfg.write_text(commands or f'wait {duration}; echo UTNT_TEST_END; screenshot logs/{label}.png; wait 5; quit\n')
        args+=['+exec',str(cfg)]
    else: args+=['-norun','-errorlog','utnt-compile']
    args=[arg.replace(chr(92),'/') for arg in args]
    options={}
    if os.name=='nt':
        si=subprocess.STARTUPINFO(); si.dwFlags|=subprocess.STARTF_USESHOWWINDOW; si.wShowWindow=0
        options={'startupinfo':si,'creationflags':subprocess.CREATE_NO_WINDOW}
    start=time.monotonic()
    try:
        r=subprocess.run(args,cwd=root,capture_output=True,timeout=timeout,**options)
        output=(r.stdout+r.stderr).decode(errors='replace'); code=r.returncode
    except subprocess.TimeoutExpired as e:
        output=((e.stdout or b'')+(e.stderr or b'')).decode(errors='replace'); code=-1
    log=logs/(label+'.log'); log.write_text(output,encoding='utf-8')
    errors=[s for s in ('UTNT_ASSERT FAIL','VM execution aborted','errors while parsing','Script error,','Execution could not continue','ACS: Unknown','P_StartScript: Unknown script') if s in output]
    if mapname and 'UTNT_TEST_END' not in output: errors.append('missing completion marker')
    if regression and 'UTNT_REGRESSION_COMPLETE' not in output: errors.append('missing regression assertions')
    result={'label':label,'ok':code in (0,1337) and not errors,'exit':code,'seconds':round(time.monotonic()-start,2),'log':str(log),'errors':errors,'assertions':output.count('UTNT_ASSERT PASS')}
    if not quiet: print(json.dumps(result),flush=True)
    return result
