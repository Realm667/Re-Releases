"""Verify client-only render pools after save/load in original UTNT maps."""
from pathlib import Path
import argparse,json
from check_engine import ROOT,run_case

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine',type=Path,required=True);p.add_argument('--iwad',type=Path,required=True)
    p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
    p.add_argument('--maps',nargs='+',default=['TNT02','TNTLE'])
    p.add_argument('--renderers',nargs='+',choices=['0','1'],default=['1'])
    a=p.parse_args();results=[]
    for renderer in a.renderers:
        for mapname in a.maps:
            commands='god; notarget; wait 200; netevent fxremember; save fx-lifecycle; wait 5; load fx-lifecycle; wait 40; netevent fxrestore; wait 5; echo UTNT_TEST_END; wait 5; quit\n'
            result=run_case(a.engine,a.iwad,mod=a.mod,addon=ROOT/'tools/fixtures/cosmetic-lifecycle',mapname=mapname,renderer=renderer,label=f'cosmetic-lifecycle-{mapname}-{renderer}',commands=commands,timeout=60,settings=[('i_pauseinbackground','false'),('vid_activeinbackground','true')])
            result['ok']=result['ok'] and result['assertions']==6
            results.append(result)
    out=ROOT/'tutnt/.codex/validation/cosmetic-lifecycle.json';out.write_text(json.dumps(results,indent=2)+'\n')
    return 0 if all(r['ok'] for r in results) else 1
if __name__=='__main__':raise SystemExit(main())
