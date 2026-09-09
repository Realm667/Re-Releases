"""Verify the installed package, guarded bindings and save/script behavior."""
from pathlib import Path
import argparse,json,sys,re
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT/'tools'))
from check_engine import run_case
from area_geometry import records

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['engine','iwad','mod','output']:p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--reference-geometry',type=Path)
    a=p.parse_args();work=a.output.resolve();fixture=work/'fixture';fixture.mkdir(parents=True,exist_ok=True)
    (fixture/'geometry.zc').write_text((HERE/'geometry.zc').read_text().split('\n',1)[1])
    (fixture/'zscript.zc').write_text('version "4.14"\n#include "geometry.zc"\n#include "regression.zc"\n')
    (fixture/'MAPINFO.txt').write_text('gameinfo { AddEventHandlers = "SurfaceGeometry", "AreaRegression" }\n')
    code=(HERE/'regression.zc').read_text();tests=[];tables={}
    for item in (a.root/'tutnt/areaalign').glob('*.txt'):
        rows=[line.split('|') for line in item.read_text().splitlines()];tables[item.stem]=rows
        for r in rows:
            if r[0]!='D':continue
            _,si,part,old,alias,ow,oh=r
            tests.append(f'''if(level.MapName=="{item.stem}") {{ let s=level.Sectors[{si}];if(e.Args[0]==0){{s.SetTexture({part},TexMan.CheckForTexture("{old}"));s.SetXOffset({part},{int(ow)*3+7});s.SetYOffset({part},{int(oh)*2+9});}}else Console.Printf("UTNT_ASSERT %s area-dynamic-{si}",TexMan.GetName(s.GetTexture({part}))=="{alias}" && abs(s.GetXOffset({part})-7)<.001 && abs(s.GetYOffset({part})-9)<.001 ? "PASS" : "FAIL"); }}''')
    (fixture/'regression.zc').write_text(code.replace('// GENERATED_DYNAMIC_TEST','\n'.join(tests)))
    common=dict(engine=a.engine,iwad=a.iwad,root=work,mod=a.mod,addon=fixture)
    r=run_case(**common,label='compile');assert r['ok'],Path(r['log']).read_text()[-4000:]
    results=[]
    for name,rows in sorted(tables.items()):
        cmd='wait 100; netevent geometry; netevent areaalign; wait 5; '
        regression=name in ['TNT04B','TNTLE','TNT02']
        if regression:cmd+=f'god; notarget; netevent areabaseline; wait 35; netevent areasnapshot 0; wait 2; save area-{name}; wait 8; load area-{name}; wait 70; netevent areasnapshot 1; wait 2; netevent areadynamic 0; wait 3; netevent areadynamic 1; netevent areaterrain; wait 3; '
        cmd+='echo UTNT_TEST_END; quit'
        r=run_case(**common,mapname=name,renderer='0' if name=='TNTLE' else '1',label=name,timeout=120,commands=cmd,settings=[('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_lowerinbackground',False)])
        log=Path(r['log']).read_text();match=re.search(r'AREAALIGN\|'+name+r'\|(\d+)\|(\d+)\|(\d+)',log)
        expected=int(rows[0][-1]);r['bindings_ok']=bool(match and list(map(int,match.groups()))==[expected,0,expected])
        r['shader_errors']=any(s in log.lower() for s in ['shader compilation failed','failed to compile','unable to load shader'])
        required=1+sum(row[0]=='D' for row in rows) if regression else 0
        r['regression_ok']=r['assertions']>=required
        r['finite_failures']=[]
        if a.reference_geometry:
            before={tuple(v[1:3]):list(map(float,v[3:])) for v in records(a.reference_geometry/f'geometry-{name}.log') if v[0]=='SURFMID'}
            after={tuple(v[1:3]):list(map(float,v[3:])) for v in records(Path(r['log'])) if v[0]=='SURFMID'}
            for row in rows:
                if row[0] not in ['W','P'] or row[8]!='1':continue
                key=tuple(row[1:3])
                if key in before and before[key][0] and (key not in after or any(abs(x-y)>.002 for x,y in zip(before[key],after[key]))):r['finite_failures'].append(key)
        r['ok']=r['ok'] and r['bindings_ok'] and r['regression_ok'] and not r['shader_errors'] and not r['finite_failures']
        results.append(r);(work/'results.json').write_text(json.dumps(results,indent=2))
        if not r['ok']:raise RuntimeError(json.dumps(r)+'\n'+log[-2500:])
    print('PASS: all maps, material bindings, finite panels, save/load, scripted changes, OpenGL and Vulkan.')

if __name__=='__main__':main()
