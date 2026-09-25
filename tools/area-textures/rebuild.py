"""Rebuild texture alignment tables from an immutable native-engine snapshot.

The default is read-only for the project. --apply publishes only areaalign tables
after checking that every map still matches the measured source version.
"""
from pathlib import Path
import argparse,hashlib,json,os,shutil,sys,zipfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_utnt import snapshot,input_files,compile_sources
from check_engine import run_case
from area_maps import allmaps
import area_plan

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE'))
    p.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD'))
    p.add_argument('--acc',type=Path,default=os.environ.get('UTNT_ACC'))
    p.add_argument('--apply',action='store_true')
    p.add_argument('--maps',nargs='+',help='Rebuild only these map names')
    p.add_argument('--baseline-package',type=Path,help='Path for the isolated baseline PK3')
    a=p.parse_args()
    for key in ['engine','iwad','acc']:
        if not getattr(a,key) or not getattr(a,key).is_file():p.error('Supply --'+key+' or UTNT_'+key.upper())
    root=a.root.resolve();work=a.output.resolve();work.mkdir(parents=True,exist_ok=True)
    package=(a.baseline_package or root/'tutnt/.codex/builds/areaalign-baseline.pk3').resolve();package.parent.mkdir(parents=True,exist_ok=True)
    sourcehashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'tutnt/maps').glob('*.wad')}
    shutil.copy2(root/'tools/artwork/area-textures/materials.json',work/'materials.json')
    shutil.copy2(root/'tools/artwork/area-textures/legacy.json',work/'legacy.json')
    with snapshot(root) as (source,hashes,metadata):
        # Measure original native geometry and clipping before area mappings.
        mapinfo=source/'tutnt/MAPINFO.txt'
        mapinfo.write_text(mapinfo.read_text().replace('gameinfo { AddEventHandlers = "UTNT_AreaTextures" }',''))
        compile_sources(source,a.acc)
        with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
            for item in input_files(source):z.write(item,item.relative_to(source/'tutnt'))
        maps=allmaps(source/'tutnt')
        if a.maps:
            requested=[name.upper() for name in a.maps]
            unknown=set(requested)-set(maps)
            if unknown:p.error('Unknown maps: '+', '.join(sorted(unknown)))
            maps={name:maps[name] for name in requested}
        (work/'map-data.json').write_text(json.dumps(maps))
        shutil.copytree(source/'tutnt/maps',work/'baseline/tutnt/maps',dirs_exist_ok=True)
        (work/'source.json').write_text(json.dumps(dict(maps=sourcehashes,build=metadata),indent=2))
    fixture=work/'measure-fixture';fixture.mkdir(exist_ok=True)
    shutil.copy2(HERE/'geometry.zc',fixture/'zscript.zc')
    (fixture/'MAPINFO.txt').write_text('gameinfo { AddEventHandlers = "SurfaceGeometry" }\n')
    for name in maps:
        r=run_case(a.engine,a.iwad,root=work,mod=package,addon=fixture,mapname=name,label='geometry-'+name,timeout=90,
                   commands='wait 70; netevent geometry; wait 5; echo UTNT_TEST_END; quit',settings=[('i_pauseinbackground',False),('vid_activeinbackground',True)])
        if not r['ok']:raise RuntimeError('Geometry measurement failed: '+r['log'])
    area_plan.W=work;area_plan.analyze.W=work;area_plan.build()
    for name,digest in sourcehashes.items():
        if hashlib.sha256((root/'tutnt/maps'/name).read_bytes()).hexdigest()!=digest:raise RuntimeError('Map changed while measuring: '+name)
    if a.apply:
        dest=root/'tutnt/areaalign';dest.mkdir(exist_ok=True)
        for item in (work/'addon/areaalign').glob('*.txt'):
            if item.stem not in maps:continue
            tmp=dest/(item.name+'.tmp');shutil.copy2(item,tmp);os.replace(tmp,dest/item.name)
    print('Verified tables:',work/'addon/areaalign','; applied:',a.apply)

if __name__=='__main__':main()
